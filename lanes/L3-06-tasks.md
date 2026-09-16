> **[AUTHORITATIVE — FD-B1-L3 2026-09-02]**
> This is the authoritative task plan for Lane 3. All competing plans are superseded.

> **L0 ATTENTION — 4 work items from superseded phase files lack L3-06 equivalents (Session 12, 2026-09-08):**
> 1. CMP-10: lifecycle vs Renovate monitoring/CI config (from L3-01-12) — needs L3-06 task or L0 explicit drop
> 2. CMP-12: Shared Service registry dependency check (from L3-01-14) — needs L3-06 task or L0 explicit drop
> 3. create-product scaffold conformance verifier / AT-001 dashboard product-list guarantee (from L3-04-12) — needs L3-06 task or L0 explicit drop
> 4. 14-day delegation expiry warning (from L3-05-26) — needs L3-06 task or L0 explicit drop
> authority_delta.py: L3 wins — file is in validators/drift/ which is L3's owned namespace. L3-03 reference was stale. No L0 ruling needed. (Resolved Session 12, 2026-09-08)
> These items will NOT be dispatched unless L3-06 tasks are added for them.
> **Session 12 (2026-09-08):** All four tasks added as L3-P0-CMP10, L3-P0-CMP12, L3-P0-AT001, L3-P0-DEL14 below.

---

### L3-P0-CMP10 — Lifecycle vs Renovate monitoring

**Ported from** `lanes/L3-01-diff-engine.md` task L3-01-12 by Session 12 (FD-B1-L3 corollary)
**Spec:** §53.1 row 10 ("Auto-repair where safe; alert otherwise"); §18.1 (lifecycle states: `active | maintenance | paused | sunset | archived`); §33.2 (Renovate disposition policy)
**Files:** `reconciler/comparators/cmp_10_lifecycle.py`, `reconciler/comparators/lifecycle-expectations.yaml`, `reconciler/comparators/tests/test_cmp_10.py`

The safe/unsafe split is read from `lifecycle-expectations.yaml`, never decided in code. A safe row proposes a Level-3 repair (proposed only — rule R1). An unsafe row raises an Amber alert at Level 2 and proposes nothing. Exactly two checks are unsafe: `repository-archived-flag` and `ci-workflow-present` (§53.2 Level-3 "Applies to" list is closed; neither is on it).

**Commands**

```bash
set -euo pipefail
# Ported from lanes/L3-01-diff-engine.md by Session 12 (FD-B1-L3 corollary)
[ -n "$CP" ] || { echo "ERROR: CP is not set"; exit 1; }
cd "$CP"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/3/p0-cmp10-lifecycle
# Write reconciler/comparators/lifecycle-expectations.yaml (CMP-10 table; states, checks, safe flags)
# Write reconciler/comparators/cmp_10_lifecycle.py (Lifecycle comparator, comparator_id="CMP-10")
# Write reconciler/comparators/tests/test_cmp_10.py (six tests)
python -m pytest reconciler/comparators/tests/test_cmp_10.py -q 2>&1 | grep -oE '^[0-9]+ passed'
git add reconciler/comparators
git diff --cached --name-only | grep -vE '^(reconciler/|tools/provision/|validators/drift/)' && { echo "LANE-GUARD FAIL: foreign path staged"; exit 1; } || echo "LANE-GUARD OK"
git commit -m "L3-P0-CMP10: lifecycle vs Renovate monitoring and CI configuration"
git fetch origin && git rebase origin/integration && git push -u origin lane/3/p0-cmp10-lifecycle
gh pr create --base integration --title "L3-P0-CMP10: lifecycle vs Renovate monitoring" --body "Lane 3. Task L3-P0-CMP10 (ported from L3-01-12). Acceptance command in L3-06-tasks.md passed."
```

**Acceptance criteria**

| # | Criterion | Proving command | Required output |
| --- | --- | --- | --- |
| A1 | Six CMP-10 tests pass | `cd "$CP" && python -m pytest reconciler/comparators/tests/test_cmp_10.py -q 2>&1 \| grep -oE '^[0-9]+ passed'` | `6 passed` |
| A2 | Five lifecycle states matching §18.1 | `cd "$CP" && python -c "from reconciler.comparators.cmp_10_lifecycle import load_table as t; print(' '.join(t()['states']))"` | `active maintenance paused sunset archived` |
| A3 | Exactly two checks are unsafe | `cd "$CP" && python -c "from reconciler.comparators.cmp_10_lifecycle import load_table as t; print(sum(1 for c in t()['checks'] if not c['safe']))"` | `2` |
| A4 | No repair applied in this phase | `cd "$CP" && grep -c '"applied": False' reconciler/comparators/cmp_10_lifecycle.py` | `1` |
| A5 | No foreign path touched | see SELF-VERIFY | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
# Ported from lanes/L3-01-diff-engine.md by Session 12 (FD-B1-L3 corollary)
cd "$CP"
python -m pytest reconciler/comparators/tests/test_cmp_10.py -q 2>&1 | grep -oE '^[0-9]+ passed'
python -c "from reconciler.comparators.cmp_10_lifecycle import load_table as t; print(sum(1 for c in t()['checks'] if not c['safe']))"
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'
```

Expected output, exactly:

```
6 passed
2
0
```

**STOP** — if `registries/products/*/product.yaml` carries a `identity.lifecycle` value outside the five of §18.1, do not add a sixth state. File the blocker (§0.6). Do not mark `repository-archived-flag` or `ci-workflow-present` safe.

---

### L3-P0-CMP12 — Shared Service registry dependency check

**Ported from** `lanes/L3-01-diff-engine.md` task L3-01-14 by Session 12 (FD-B1-L3 corollary)
**Spec:** §53.1 rows 11 and 12; §10.2; §12.2; §20.1 ("A product cannot declare a dependency on a shared service that does not exist in the registry"); invariant 55
**Files:** `reconciler/comparators/cmp_11_expired_access.py`, `reconciler/comparators/cmp_12_dependencies.py`, `reconciler/comparators/tests/test_cmp_11_12.py`
**Registry keys:** CMP-11 → `product.yaml`; CMP-12 → `services`

CMP-12 is the only comparator that issues **no API call at all**: both sides are declared state. It still counts rows and still fails the run's `services` count if it narrows. CMP-12 iterates the service registry one Row per declared service so that `rows_compared` for the `services` key reaches `rows_declared`.

**Commands**

```bash
set -euo pipefail
# Ported from lanes/L3-01-diff-engine.md by Session 12 (FD-B1-L3 corollary)
[ -n "$CP" ] || { echo "ERROR: CP is not set"; exit 1; }
cd "$CP"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/3/p0-cmp12-dependencies
# Write reconciler/comparators/cmp_11_expired_access.py (CMP-11, proposed revoke only — rule R1)
# Write reconciler/comparators/cmp_12_dependencies.py (CMP-12, registry_key="services", no API call)
# Write reconciler/comparators/tests/test_cmp_11_12.py (six tests)
python -m pytest reconciler/comparators/tests/test_cmp_11_12.py -q 2>&1 | grep -oE '^[0-9]+ passed'
git add reconciler/comparators
git diff --cached --name-only | grep -vE '^(reconciler/|tools/provision/|validators/drift/)' && { echo "LANE-GUARD FAIL: foreign path staged"; exit 1; } || echo "LANE-GUARD OK"
git commit -m "L3-P0-CMP12: expired access and Shared Service registry dependency check"
git fetch origin && git rebase origin/integration && git push -u origin lane/3/p0-cmp12-dependencies
gh pr create --base integration --title "L3-P0-CMP12: Shared Service registry dependency check" --body "Lane 3. Task L3-P0-CMP12 (ported from L3-01-14). Acceptance command in L3-06-tasks.md passed."
```

**Acceptance criteria**

| # | Criterion | Proving command | Required output |
| --- | --- | --- | --- |
| A1 | Six tests pass | `cd "$CP" && python -m pytest reconciler/comparators/tests/test_cmp_11_12.py -q 2>&1 \| grep -oE '^[0-9]+ passed'` | `6 passed` |
| A2 | CMP-12 issues no API call | `cd "$CP" && grep -cE 'ctx\.client\.' reconciler/comparators/cmp_12_dependencies.py` | `0` |
| A3 | CMP-11 proposes and never applies | `cd "$CP" && grep -c '"applied": False' reconciler/comparators/cmp_11_expired_access.py` | `2` |
| A4 | CMP-12 counts toward `services` | `cd "$CP" && python -c "from reconciler.comparators.cmp_12_dependencies import Dependencies as D; print(D.registry_key)"` | `services` |
| A5 | No foreign path touched | see SELF-VERIFY | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
# Ported from lanes/L3-01-diff-engine.md by Session 12 (FD-B1-L3 corollary)
cd "$CP"
python -m pytest reconciler/comparators/tests/test_cmp_11_12.py -q 2>&1 | grep -oE '^[0-9]+ passed'
grep -cE 'ctx\.client\.' reconciler/comparators/cmp_12_dependencies.py
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'
```

Expected output, exactly:

```
6 passed
0
0
```

**STOP** — if `registries/services/` does not exist, STOP and file the blocker `Blocked-on: L1`. CMP-12's declared side has no source; its `rows_declared` would be `0`, making the comparison vacuously clean (EC-109). Do not execute the proposed revoke; do not call the team-membership removal endpoint.

---

### L3-P0-AT001 — create-product scaffold conformance verifier

**Ported from** `lanes/L3-04-provisioning.md` task L3-04-12 by Session 12 (FD-B1-L3 corollary)
**Spec:** §19.1 ("Automatic discovery is mandatory. … If a human must edit a dashboard to add a product, that is a defect in the operating system, not a task."); §11 (no hard-coded repository list); invariant 52; AT-001 ("No dashboard, workflow or script contains a product list"); §20.2; §92.3
**Files:** `tools/provision/provision/steps/surfaces.py`, `tools/provision/provision/ops/verify_surfaces.py`, `tools/provision/provision/surfaces/surfaces.yaml`, `tools/provision/tests/test_verify_surfaces.py`

This task adds no registration call. Registration is a consequence of the registry entry. The task builds the verifier that proves it. Static check runs with no dashboard server in existence. A hit in a dashboard JSON, workflow, script or config file is a defect, reported as `HARD-CODED-PRODUCT: <path>:<line>` and exits 3.

**Commands**

```bash
set -euo pipefail
# Ported from lanes/L3-04-provisioning.md by Session 12 (FD-B1-L3 corollary)
[ -n "$CP" ] || { echo "ERROR: CP is not set"; exit 1; }
cd "$CP"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/3/p0-at001-scaffold-verifier
source "$CP/tools/provision/scripts/lane.sh"
# Write tools/provision/provision/surfaces/surfaces.yaml (six surfaces from §19.1)
# Write tools/provision/provision/steps/surfaces.py (step cp-10-surfaces; read-only, no write call)
# Write tools/provision/provision/ops/verify_surfaces.py (static and live check logic)
# Write tools/provision/tests/test_verify_surfaces.py
cd "$CP/tools/provision" && . .venv/bin/activate && python -m pytest tests/test_verify_surfaces.py -q
python -m provision verify-surfaces --static --root "$CP"
cd "$CP" && git add tools/provision
git diff --cached --name-only | grep -vE '^(reconciler/|tools/provision/|validators/drift/)' && { echo "LANE-GUARD FAIL: foreign path staged"; exit 1; } || echo "LANE-GUARD OK"
git commit -m "L3-P0-AT001: surface-registration verifier; hard-coded product list is a build failure"
git fetch origin && git rebase origin/integration && git push -u origin lane/3/p0-at001-scaffold-verifier
gh pr create --base integration --title "L3-P0-AT001: create-product scaffold conformance verifier" --body "Lane 3. Task L3-P0-AT001 (ported from L3-04-12). Acceptance command in L3-06-tasks.md passed."
```

**Acceptance criteria**

| # | Criterion | Proving command | Required output |
| --- | --- | --- | --- |
| A1 | Exactly six surfaces asserted | `cd "$CP/tools/provision" && python -m provision verify-surfaces --list \| wc -l` | `6` |
| A2 | No hard-coded product id in control-plane tree | `cd "$CP/tools/provision" && python -m provision verify-surfaces --static --root "$CP" \| tail -1` | `SURFACES-STATIC: 0 HARD-CODED` |
| A3 | Seeded hard-coded id is detected | `cd "$CP/tools/provision" && python -m pytest tests/test_verify_surfaces.py::test_seeded_hardcode_detected -q >/dev/null && echo OK` | `OK` |
| A4 | Unreachable surface never reports pass | `cd "$CP/tools/provision" && python -m pytest tests/test_verify_surfaces.py::test_unreachable_is_failure -q >/dev/null && echo OK` | `OK` |
| A5 | Step makes no surface-specific write call | `cd "$CP/tools/provision" && grep -rn "call(" provision/steps/surfaces.py \| grep -vc "'GET'"` | `0` |
| A6 | Lane guard clean | `source "$CP/tools/provision/scripts/lane.sh" && lane_guard` | `LANE-GUARD: PASS` |

**SELF-VERIFY**

```bash
set -euo pipefail
# Ported from lanes/L3-04-provisioning.md by Session 12 (FD-B1-L3 corollary)
cd "$CP/tools/provision" \
  && [ "$(python -m provision verify-surfaces --list | wc -l)" -eq 6 ] \
  && [ "$(python -m provision verify-surfaces --static --root "$CP" | tail -1)" = "SURFACES-STATIC: 0 HARD-CODED" ] \
  && python -m pytest tests/test_verify_surfaces.py -q >/dev/null \
  && ( source "$CP/tools/provision/scripts/lane.sh"; lane_guard ) \
  && echo "SELF-VERIFY L3-P0-AT001: PASS"
```

Expected output (last line, exactly): `SELF-VERIFY L3-P0-AT001: PASS`

**STOP** — if the static check reports `HARD-CODED-PRODUCT` in a path outside `tools/provision/**`, do not fix it. File the §0.6 blocker titled `BLOCKER L3-P0-AT001: hard-coded product list found in <path>` quoting the exact `path:line`, and route to the owning lane through L0.

---

### L3-P0-DEL14 — 14-day delegation expiry warning

> **BLOCKED pending DR-L3-05-B (2026-09-08):** This task will stop at step 0 until DR-L3-05-B is resolved (L0 must decide the delegation warning type list). See `PENDING_FOUNDER_DECISIONS.md` for the decision queue.

**Ported from** `lanes/L3-05-orphans.md` task L3-05-26 by Session 12 (FD-B1-L3 corollary)
**Spec:** §10.1 line 787 ("Delegation expiry is warned, never silent. Every delegation-type assignment receives a 14-day advance expiry warning in the daily expiry check, exactly as expiring assets do (Section 49).")
**Files:** `reconciler/expiry/warnings.py`, `reconciler/tests/expiry/test_delegation_warning.py`, fixtures `reconciler/tests/fixtures/expiry/DELEGATION-WARN/**`, `reconciler/tests/fixtures/expiry/DELEGATION-NO-WARN/**`
**Blocked by:** DR-L3-05-B (which `assignments[].type` tokens are "delegation-type") — STOP at step 0 if `DELEGATION_WARNING_TYPES` is `None`.

**Commands**

```bash
set -euo pipefail
# Ported from lanes/L3-05-orphans.md by Session 12 (FD-B1-L3 corollary)
[ -n "$CP" ] || { echo "ERROR: CP is not set"; exit 1; }
cd "$CP"
# Step 0 — decision gate (STOP if DELEG-DR False)
python -c "import reconciler.orphans.decisions as d; print('DELEG-DR', d.DELEGATION_WARNING_TYPES is not None)"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/3/p0-del14-delegation-warning
# Write reconciler/expiry/warnings.py:
#   WARNING_LEAD_DAYS_DELEGATION = 14  (§10.1 line 787 — not configurable)
#   @dataclass(frozen=True) class ExpiryWarning: kind, subject, holder, expiry, days_remaining, recipient, detail, open_items
#   def delegation_warnings(ctx) -> list[ExpiryWarning]  (window: 0 <= days <= 14, inclusive)
#   def warning_payloads(warnings) -> list[dict]  (event_type = "delegation expiry warning issued")
# Write reconciler/tests/expiry/test_delegation_warning.py
# Write fixtures DELEGATION-WARN (as_of 2026-08-27, four assignments: +14d, 0d, +15d, -1d; expect 2 warnings)
# Write fixtures DELEGATION-NO-WARN (same four but non-delegation type; expect 0 warnings)
python -m pytest reconciler/tests/expiry/test_delegation_warning.py -q
git add reconciler/expiry reconciler/tests/expiry
git diff --cached --name-only | grep -vE '^(reconciler/|tools/provision/|validators/drift/)' && { echo "LANE-GUARD FAIL: foreign path staged"; exit 1; } || echo "LANE-GUARD OK"
git commit -m "L3-P0-DEL14: 14-day delegation expiry warning"
git fetch origin && git rebase origin/integration && git push -u origin lane/3/p0-del14-delegation-warning
gh pr create --base integration --title "L3-P0-DEL14: 14-day delegation expiry warning" --body "Lane 3. Task L3-P0-DEL14 (ported from L3-05-26). Acceptance command in L3-06-tasks.md passed."
```

**Acceptance criteria**

| # | Criterion | Proving command | Expected output |
| --- | --- | --- | --- |
| A1 | Lead time is exactly 14 | `python -c "from reconciler.expiry.warnings import WARNING_LEAD_DAYS_DELEGATION as d;print(d)"` | `14` |
| A2 | Boundaries inclusive at 14 and 0, exclusive at 15 and −1 | SELF-VERIFY | `WARN 2 0,14` |
| A3 | Non-delegation types never warn | SELF-VERIFY | `NOWARN 0` |
| A4 | Event token verbatim | SELF-VERIFY | `EVENT delegation expiry warning issued` |
| A5 | Tests pass | `python -m pytest reconciler/tests/expiry/test_delegation_warning.py -q \| tail -1` | contains `passed`, not `failed` |
| A6 | No foreign path | §0.6 lane-guard block | `LANE-GUARD OK` |

**SELF-VERIFY**

```bash
set -euo pipefail
# Ported from lanes/L3-05-orphans.md by Session 12 (FD-B1-L3 corollary)
cd "$CP"
python - <<'EOF'
from pathlib import Path
from datetime import date
from reconciler.orphans.loader import load_control_plane
from reconciler.expiry.warnings import delegation_warnings, warning_payloads, WARNING_LEAD_DAYS_DELEGATION
B = Path('reconciler/tests/fixtures/expiry')
w = delegation_warnings(load_control_plane(B/'DELEGATION-WARN', date(2026,8,27),'current'))
print("LEAD", WARNING_LEAD_DAYS_DELEGATION)
print("WARN", len(w), ",".join(str(x.days_remaining) for x in sorted(w, key=lambda x: x.days_remaining)))
print("NOWARN", len(delegation_warnings(load_control_plane(B/'DELEGATION-NO-WARN', date(2026,8,27),'current'))))
print("EVENT", warning_payloads(w)[0]["event_type"])
EOF
```

Expected output, exactly:

```
LEAD 14
WARN 2 0,14
NOWARN 0
EVENT delegation expiry warning issued
```

**STOP** — if `DELEGATION_WARNING_TYPES` is `None` (DR-L3-05-B unresolved), STOP and file the blocker. §10.1 line 787 states 14 days; do not make it configurable, do not read it from a registry, and do not align it with the 30-day asset threshold of §49.1 — those are different clocks on different objects.

---

# L3-06 — Lane 3 Atomic Task List

# Phase-to-file mapping (FD-B1-L3: L3-06-tasks.md is authoritative — FD-045 superseded by FD-B1-L3 2026-09-02)

**Lane 3 — Reconciler & Provisioning.** Subsystems **C** (Reconciliation engine) and **D** (Provisioning and scaffolding), spec §99.2.
**Branch prefix:** `lane/3/*` · **Merge train position:** 4th (L1 → L4 → L2 → **L3** → L5), per `PARTITION.md`.
**Owned paths (exclusive):** `reconciler/**`, `tools/provision/**`, `validators/drift/**`.

This file is the complete, ordered work list for Lane 3. Work it **top to bottom**. Every task below is executable without opening another document. Do not skip, do not reorder, do not batch.

> §99.6 risk 6: *"the reconciler is the highest-privilege identity in the system"* and auto-repair is *"the most dangerous code"*. Every rule in §0.3 below exists because of that sentence. None of them is optional.

---

## 0. Standing protocol — read once, apply to every task

### 0.1 Path ownership (hard)

You may create or edit files **only** under these three roots:

```
reconciler/**
tools/provision/**
validators/drift/**
```

You may **read** anything in the repository. You may **never write** to `contracts/**`, `schemas/**`, `registries/**`, `.github/workflows/**`, `validators/registry/**`, `tools/evidence/**`, `access/**`, `infra/**`, `ops-vm/**`, `metrics/**`, `records/**`, `events/**`, `CODEOWNERS`, `Makefile`, or any root file. A pull request touching a foreign path fails the lane-guard check and is rejected (`PARTITION.md` rule 1).

**Namespace-package rule.** Do **not** create `tools/__init__.py` or `validators/__init__.py`. Those two directories are shared parents owned by other lanes. `tools.provision` and `validators.drift` import as PEP 420 implicit namespace packages. Creating either `__init__.py` is a foreign-path write and will be rejected.

### 0.2 Git protocol — every task, no exceptions

Start of every task:

```bash
[ -n "$CP" ] || { echo "ERROR: CP is not set"; exit 1; }
cd "$CP"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/3/<task-slug>
```

End of every task (after its acceptance command passes):

```bash
git add <the exact files named in the task>
git commit -m "<TASK-ID>: <task title>"
git fetch origin && git rebase origin/integration
git push -u origin lane/3/<task-slug>
gh pr create --base integration --title "<TASK-ID>: <task title>" --body "Lane 3. Task <TASK-ID>. Acceptance command in L3-06-tasks.md passed."
```

One branch per task. Never merge another lane's branch. Never rebase another lane's branch.

### 0.3 The five reconciler safety rules — enforced in code, tested, never relaxed

These are transcribed from §53.3, §101 invariant 81, §40.1 and §99.6 risk 6. Any task whose implementation would violate one of these is a STOP.

1. **Stricter-only.** A repair is permitted only when it moves actual state toward declared state **and** declared state is at least as restrictive as actual state. Where actual is stricter than declared, emit Level 2 and repair nothing (§53.3, AT-033).
2. **Never loosen, never touch runtime, never touch data, never touch secrets.** Reconciliation never relaxes a control, never modifies production runtime configuration, never modifies data, never rotates or writes secrets (§53.3).
3. **Detect before repair.** Every repair class ships **disabled by default** and is enabled one class at a time by explicit configuration (§98.2 Phase 3; §98.3; §99.4 item 6).
4. **The reconciler credential is bounded and the bound is executed, not asserted.** Six negative attempts must fail: GitHub Actions secret write, environment write, workflow-file change, organisation-settings change, `records/**` write, any Layer B access (AT-110, §40.1).
5. **The instrument is suspect by default.** A run reporting zero findings — including the seeded canary — is a **FAILED** run, not a clean one (§53.1 seeded-canary rule; AT-102).

### 0.4 Where this lane's output runs (it is not this lane's job to schedule it)

| Artifact | Built by | Scheduled / wired by | Do not build it here |
| --- | --- | --- | --- |
| Reconciler program | **L3** (`reconciler/**`) | L5 (`ops-vm/**` timer) | the systemd unit |
| Independent control verifier program | **L3** (`validators/drift/**`) | L2 (`.github/workflows/**` scheduled workflow) | the workflow YAML |
| Provisioning CLI | **L3** (`tools/provision/**`) | invoked by a human DevOps-capability holder (§19.1) | any workflow that calls it |

Consequence, binding on every task in this file: **every acceptance command and every SELF-VERIFY command must run locally, offline, against a fixture.** No task's acceptance may depend on a live GitHub organisation, a running CI job, or another lane's merged branch. Tasks that must eventually touch live GitHub ship a fixture-backed adapter and a `--live` flag that is never exercised in acceptance.

### 0.5 Deterministic output contract (used by every SELF-VERIFY in this file)

Every comparator and every operation prints exactly one summary line to stdout on `--summary`:

```
<STATUS> <id> findings=<int> compared=<int>
```

`STATUS` is `OK` when the module executed, `FAIL` when it could not execute. `findings` counts drift findings emitted. `compared` counts rows actually compared (§53.1: *"Every run additionally records its per-registry comparison counts"*). Run level prints one additional line:

```
CANARY <found|missing>
```

Exit codes, fixed: `0` = executed, no Blocking findings. `2` = executed, at least one Blocking finding. `3` = run FAILED (instrument failure, canary missing). Any other non-zero = crash, which is a STOP.

**`--only` suppression rule.** When `--only <comparator-id>` is given, the CLI runs one comparator only and suppresses the canary-missing rule. The summary prints `CANARY n/a` (not `CANARY missing`) and the exit code is `0` or `2` only — never `3`. The `3 = FAILED` rule applies exclusively to full (non-`--only`) runs. Phase-1 SELF-VERIFYs that use `--only` must therefore expect exit `0` or `2` with `CANARY n/a` once `L3-P1-17` is merged; before `L3-P1-17` exists the canary module is absent and the output is `CANARY missing` with exit `0` or `2` (unchanged).

### 0.6 STOP rule and blocker-issue template

**Standing STOP rule.** If a task's stated STOP condition occurs, if any command errors in a way the task does not describe, if a file you must edit is outside §0.1, or if a fact you need is not written in this file — **stop, commit nothing, and file the blocker below.** Do not guess, do not substitute, do not proceed to the next task.

```bash
gh issue create --title "BLOCKER <TASK-ID>: <one-line symptom>" --label blocker,lane-3 --body "$(cat <<'EOF'
blocked_task: <TASK-ID>
lane: 3
branch: lane/3/<task-slug>
stop_condition_hit: <quote the STOP line from L3-06-tasks.md verbatim>
command_run: |
  <the exact command>
observed_output: |
  <paste verbatim, do not summarise>
expected_output: |
  <paste the SELF-VERIFY expected block verbatim>
files_touched_so_far: <list, or "none">
decision_required_from: L0
EOF
)"
```

Then post the issue number in the lane channel and take the next **unblocked** task, or idle. Never work around a blocker.

---

## 1. DECISION REQUIRED — the four decisions L0 owns

These are design choices. The spec does not settle them and the executor has no authority to settle them. **L3-D1 and L3-D2 block the start of the lane**: work stops at L3-P0-02 until L0 records an answer in `docs/` and links it here. **L3-D3** blocks two Phase 5 tasks only. **L3-D4** is stated in full at §5 below, where it applies, and blocks nothing — its interim behaviour is defined there.

| Decision | Question in one line | Blocks |
| --- | --- | --- |
| **L3-D1** | implementation language, runtime version, dependency pinning | L3-P0-02 and therefore everything |
| **L3-D2** | the five `contracts/**` paths Lane 3 reads | L3-P0-03 and its dependants |
| **L3-D3** | Closed: L3-D3 resolved — GitHub App credential confirmed. | L3-P5-06, L3-P5-07 |
| **L3-D4** | drift class for orphan severities `High` and `Medium` (stated at §5) | nothing — interim behaviour defined |

### DECISION REQUIRED — L3-D1: implementation language and runtime

**Question.** What language, runtime version and dependency-pinning mechanism do `reconciler/**`, `tools/provision/**` and `validators/drift/**` use?
**Why L0.** §99.5 fixes the git host, CI, dashboards, records format and identity bridge. It does not fix the implementation language of subsystems C and D. Choosing one is architecture.
**Constraint from spec.** §101 invariant 85: third-party dependencies are pinned. §99.1: *"a schema-and-validator suite, a reconciliation engine, a provisioning and scaffolding CLI"* — scripts and CLIs, not an application.
**This file is written assuming L0 ratifies:** Python 3.12, dependencies pinned by exact `==` version in `reconciler/requirements.txt`, no lockfile generator.
**If L0 ratifies anything else:** STOP at L3-P0-02 and file the blocker; this whole file needs reissuing by L0.

### DECISION REQUIRED — L3-D2: the contract filenames Lane 3 consumes

**Question.** Give the exact frozen paths under `contracts/**` for the five artifacts Lane 3 reads. Lane 3 never edits them (`PARTITION.md` rule 2).
**The five roles Lane 3 needs a contract for:**

| Role | What Lane 3 does with it | Spec anchor |
| --- | --- | --- |
| Drift finding | the object every comparator emits | §53.1, §53.4 |
| Reconciliation run record | the object each run writes | §53.1 *"Every reconciliation run writes its result"* |
| Repair record | the object each Level-3 repair writes | §26.4 *"logged as repair records"* |
| Branch-protection template | the declared side of the §53.1 protection row | §11.3 |
| Environment template | the declared side of the §53.1 environment rows | §33.4 |

**Why L0.** `contracts/**` is L0-owned and frozen in Phase 0. Lane 3 guessing a filename produces a lane that compiles against nothing.
**Discovery aid for L0:** `ls -1 contracts/`
**Until answered:** L3-P0-03 is blocked, and every task depending on it is blocked.

### Binding: L3-D3 resolved — reconciler machine identity: GitHub App credential confirmed (was: DECISION REQUIRED — reconciler machine identity form and test organisation)

**Question.** Is the reconciler credential a GitHub App installation token or a fine-grained PAT, and what organisation login do `--live` smoke runs target?
**Why L0.** §40.1 allows either (*"a least-privilege GitHub App or fine-grained PAT"*) and D80 states a preference (*"machine identities prefer GitHub Apps over seat accounts where the mechanism allows"*) without deciding. The App-vs-PAT choice changes the auth code path and the AT-110 probe shape.
**Blocks:** L3-P5-06 (AT-110 probe), L3-P5-07 (behavioural envelope), L3-P8-05 (lane acceptance-matrix runner), and L3-P8-06 (lane handoff manifest). Fixture-backed tasks proceed without it; L3-P8-05 and L3-P8-06 do not, because L3-P8-05's AT traceability matrix maps AT-110 → L3-P5-06 and therefore cannot report `MATRIX passed=11 total=11` until this decision is recorded.

---

## 2. Master task table — all 78 tasks in execution order

Work top to bottom. `Deps` are task ids that must be **merged to `integration`** first.

| # | ID | Ph | Title | Files touched | Deps | Sz | Acceptance command |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | L3-P0-01 | 0 | Lane tree and ownership marker | `reconciler/README.md`, `tools/provision/README.md`, `validators/drift/README.md` | — | S | `bash reconciler/scripts/check-ownership.sh` |
| 2 | L3-P0-02 | 0 | Package skeleton and pinned deps | `reconciler/__init__.py`, `reconciler/requirements.txt`, `reconciler/scripts/check-ownership.sh` | L3-P0-01, L3-D1 | S | `python -c "import reconciler; print('ok')"` |
| 3 | L3-P0-03 | 0 | Contract map module | `reconciler/contracts_map.py`, `reconciler/tests/test_contracts_map.py` | L3-P0-02, L3-D2 | S | `python -m pytest reconciler/tests/test_contracts_map.py -q` |
| 4 | L3-P0-04 | 0 | Fixture set `fixture-a` | `reconciler/fixtures/fixture-a/**` | L3-P0-02 | M | `python -m reconciler.fixtures.verify fixture-a` |
| 5 | L3-P0-05 | 0 | Finding model, drift classes, levels | `reconciler/model.py`, `reconciler/tests/test_model.py` | L3-P0-03 | S | `python -m pytest reconciler/tests/test_model.py -q` |
| 6 | L3-P0-06 | 0 | `GitHubState` port and fixture adapter | `reconciler/state/**` | L3-P0-04, L3-P0-05 | M | `python -m pytest reconciler/tests/test_state.py -q` |
| 7 | L3-P0-07 | 0 | Run record writer and summary line | `reconciler/runrecord.py`, `reconciler/tests/test_runrecord.py` | L3-P0-06 | M | `python -m pytest reconciler/tests/test_runrecord.py -q` |
| 8 | L3-P1-01 | 1 | Comparator registry and `reconciler.cli` | `reconciler/registry.py`, `reconciler/cli.py`, `reconciler/tests/test_cli.py` | L3-P0-07 | M | `python -m reconciler.cli list` |
| 9 | L3-P1-02 | 1 | Comparator: org membership | `reconciler/comparators/org_membership.py` (+test) | L3-P1-01 | M | `python -m reconciler.cli run --fixture fixture-a --only org_membership --summary` |
| 10 | L3-P1-03 | 1 | Comparator: capability vs team-implied authority | `reconciler/comparators/capability_authority.py` (+test) | L3-P1-01 | M | `python -m reconciler.cli run --fixture fixture-a --only capability_authority --summary` |
| 11 | L3-P1-04 | 1 | Comparator: assignments vs Team membership | `reconciler/comparators/team_membership.py` (+test) | L3-P1-01 | M | `python -m reconciler.cli run --fixture fixture-a --only team_membership --summary` |
| 12 | L3-P1-05 | 1 | Comparator: assignments vs CODEOWNERS | `reconciler/comparators/codeowners.py` (+test) | L3-P1-01 | M | `python -m reconciler.cli run --fixture fixture-a --only codeowners --summary` |
| 13 | L3-P1-06 | 1 | Comparator: branch protection template | `reconciler/comparators/branch_protection.py` (+test) | L3-P1-01 | M | `python -m reconciler.cli run --fixture fixture-a --only branch_protection --summary` |
| 14 | L3-P1-07 | 1 | Comparator: workflow template version | `reconciler/comparators/workflow_version.py` (+test) | L3-P1-01 | M | `python -m reconciler.cli run --fixture fixture-a --only workflow_version --summary` |
| 15 | L3-P1-08 | 1 | Comparator: environments and deployment branch/tag policy | `reconciler/comparators/environments.py` (+test) | L3-P1-01 | M | `python -m reconciler.cli run --fixture fixture-a --only environments --summary` |
| 16 | L3-P1-09 | 1 | Comparator: assignment `end_date` expiry | `reconciler/comparators/expiry.py` (+test) | L3-P1-01 | M | `python -m reconciler.cli run --fixture fixture-a --as-of 2026-08-27 --only expiry --summary` |
| 17 | L3-P1-10 | 1 | Comparator: `platform.yaml` workflow tag → SHA | `reconciler/comparators/workflow_tag_sha.py` (+test) | L3-P1-01 | M | `python -m reconciler.cli run --fixture fixture-a --only workflow_tag_sha --summary` |
| 18 | L3-P1-11 | 1 | Comparator: Renovate bypass ruleset split | `reconciler/comparators/renovate_bypass.py` (+test) | L3-P1-01 | M | `python -m reconciler.cli run --fixture fixture-a --only renovate_bypass --summary` |
| 19 | L3-P1-12 | 1 | Comparator: machine workflow-file change and bypass-branch authorship | `reconciler/comparators/machine_authorship.py` (+test) | L3-P1-01 | M | `python -m reconciler.cli run --fixture fixture-a --only machine_authorship --summary` |
| 20 | L3-P1-13 | 1 | Comparator: infrastructure attestation window | `reconciler/comparators/infra_attestation.py` (+test) | L3-P1-01 | S | `python -m reconciler.cli run --fixture fixture-a --as-of 2026-08-27 --only infra_attestation --summary` |
| 21 | L3-P1-14 | 1 | Comparator: record-store write freshness | `reconciler/comparators/write_freshness.py` (+test) | L3-P1-01 | M | `python -m reconciler.cli run --fixture fixture-a --as-of 2026-08-27 --only write_freshness --summary` |
| 22 | L3-P1-15 | 1 | Comparator: `restore_tested` vs restore-test records | `reconciler/comparators/restore_tested.py` (+test) | L3-P1-01 | M | `python -m reconciler.cli run --fixture fixture-a --as-of 2026-08-27 --only restore_tested --summary` |
| 23 | L3-P1-16 | 1 | Per-registry comparison counts on the run record | `reconciler/runrecord.py`, `reconciler/tests/test_counts.py` | L3-P1-02..L3-P1-15 | S | `python -m pytest reconciler/tests/test_counts.py -q` |
| 24 | L3-P1-17 | 1 | Seeded canary and the zero-findings FAIL rule | `reconciler/canary.py`, `reconciler/tests/test_canary.py` | L3-P1-16 | M | `python -m pytest reconciler/tests/test_canary.py -q` |
| 25 | L3-P1-18 | 1 | Run annotations: `external-cause`, `acknowledged_by/at`, clean-run record | `reconciler/annotations.py` (+test) | L3-P1-17 | S | `python -m pytest reconciler/tests/test_annotations.py -q` |
| 26 | L3-P1-19 | 1 | Fail-closed matrix for Blocking-class checks | `reconciler/failmode.py` (+test) | L3-P1-17 | M | `python -m pytest reconciler/tests/test_failmode.py -q` |
| 27 | L3-P1-20 | 1 | SIG-13 emission on a failed run | `reconciler/signals.py` (+test) | L3-P1-17, L3-P1-18 | S | `python -m pytest reconciler/tests/test_signals.py -q` |
| 28 | L3-P2-01 | 2 | Orphan framework and the 16-type severity map | `reconciler/orphans/__init__.py`, `reconciler/orphans/types.py` (+test) | L3-P1-01 | M | `python -m pytest reconciler/tests/test_orphan_types.py -q` |
| 29 | L3-P2-02 | 2 | Orphan detectors 1–5 (ownership slots, shared service) | `reconciler/orphans/ownership.py` (+test) | L3-P2-01 | M | `python -m reconciler.cli orphans --fixture fixture-a --group ownership --summary` |
| 30 | L3-P2-03 | 2 | Orphan detectors 6–10 (assets, commitments) | `reconciler/orphans/assets.py` (+test) | L3-P2-01 | M | `python -m reconciler.cli orphans --fixture fixture-a --group assets --summary` |
| 31 | L3-P2-04 | 2 | Orphan detectors 11–16 (migration, verification, H1, temp expiry, policy, exception) | `reconciler/orphans/governance.py` (+test) | L3-P2-01 | M | `python -m reconciler.cli orphans --fixture fixture-a --group governance --summary` |
| 32 | L3-P2-05 | 2 | Prospective orphan mode on `availability: departing` | `reconciler/orphans/prospective.py` (+test) | L3-P2-02, L3-P2-03, L3-P2-04 | M | `python -m reconciler.cli orphans --fixture fixture-a --prospective --as-of 2026-08-27 --summary` |
| 33 | L3-P2-06 | 2 | Blocking orphans non-dismissible, SIG-05 emission | `reconciler/orphans/dismissal.py` (+test) | L3-P2-05 | S | `python -m pytest reconciler/tests/test_orphan_dismissal.py -q` |
| 34 | L3-P3-01 | 3 | Drift-class config loader from `os-health.yaml` | `reconciler/driftclass.py` (+test) | L3-P1-19 | M | `python -m pytest reconciler/tests/test_driftclass.py -q` |
| 35 | L3-P3-02 | 3 | `control-plane/blocking-drift` check-run publisher | `reconciler/checkrun.py` (+test) | L3-P3-01 | M | `python -m pytest reconciler/tests/test_checkrun.py -q` |
| 36 | L3-P3-03 | 3 | Check-run identity assertion | `reconciler/comparators/checkrun_identity.py` (+test) | L3-P3-02 | S | `python -m reconciler.cli run --fixture fixture-a --only checkrun_identity --summary` |
| 37 | L3-P3-04 | 3 | Drift budget counters (Amber 2/product, Red flat 3) | `reconciler/budget.py` (+test) | L3-P3-01 | M | `python -m pytest reconciler/tests/test_budget.py -q` |
| 38 | L3-P3-05 | 3 | Reclassification gate | `reconciler/reclassify.py` (+test) | L3-P3-01 | S | `python -m pytest reconciler/tests/test_reclassify.py -q` |
| 39 | L3-P3-06 | 3 | Closure-quality audit sampler | `reconciler/closure_audit.py` (+test) | L3-P3-04 | M | `python -m pytest reconciler/tests/test_closure_audit.py -q` |
| 40 | L3-P4-01 | 4 | `provision` CLI skeleton, dry-run default | `tools/provision/cli.py`, `tools/provision/tests/test_cli.py` | L3-P0-06 | M | `python -m tools.provision.cli --help` |
| 41 | L3-P4-02 | 4 | CODEOWNERS generator, human identities only | `tools/provision/codeowners.py` (+test) | L3-P4-01 | M | `python -m pytest tools/provision/tests/test_codeowners.py -q` |
| 42 | L3-P4-03 | 4 | Branch-protection applier from template | `tools/provision/protection.py` (+test) | L3-P4-01 | M | `python -m pytest tools/provision/tests/test_protection.py -q` |
| 43 | L3-P4-04 | 4 | Environments and deployment branch/tag policy applier | `tools/provision/environments.py` (+test) | L3-P4-01 | M | `python -m pytest tools/provision/tests/test_environments.py -q` |
| 44 | L3-P4-05 | 4 | Team creator derived from registries | `tools/provision/teams.py` (+test) | L3-P4-01 | M | `python -m pytest tools/provision/tests/test_teams.py -q` |
| 45 | L3-P4-06 | 4 | Repo-from-template and required-file assertion | `tools/provision/repo.py` (+test) | L3-P4-01 | M | `python -m pytest tools/provision/tests/test_repo.py -q` |
| 46 | L3-P4-07 | 4 | `create-product` orchestrator | `tools/provision/create_product.py` (+test) | L3-P4-02..L3-P4-06 | L | `python -m tools.provision.cli create-product --fixture fixture-a --product gamma --dry-run --summary` |
| 47 | L3-P4-08 | 4 | CONFIGURE checklist and manual-step issue emitter | `tools/provision/checklists.py` (+test) | L3-P4-07 | S | `python -m pytest tools/provision/tests/test_checklists.py -q` |
| 48 | L3-P4-09 | 4 | `add-person` orchestrator | `tools/provision/add_person.py` (+test) | L3-P4-02, L3-P4-05 | L | `python -m tools.provision.cli add-person --fixture fixture-a --login dev-3 --dry-run --summary` |
| 49 | L3-P4-10 | 4 | Pre-provisioning (T-1 week) checklist emitter | `tools/provision/preprovision.py` (+test) | L3-P4-09 | S | `python -m pytest tools/provision/tests/test_preprovision.py -q` |
| 50 | L3-P5-01 | 5 | Independent verifier skeleton, separate credential | `validators/drift/verifier.py` (+test) | L3-P4-02 | M | `python -m validators.drift.verifier --fixture fixture-a --summary` |
| 51 | L3-P5-02 | 5 | Verifier assertion A: no machine identity in any CODEOWNERS | `validators/drift/assert_codeowners.py` (+test) | L3-P5-01 | M | `python -m validators.drift.verifier --fixture fixture-a --only codeowners_human_only --summary` |
| 52 | L3-P5-03 | 5 | Verifier assertion B: protection and ruleset JSON match template | `validators/drift/assert_protection.py` (+test) | L3-P5-01 | M | `python -m validators.drift.verifier --fixture fixture-a --only protection_matches_template --summary` |
| 53 | L3-P5-04 | 5 | Verifier assertion C: bypass-actor list is exactly as declared | `validators/drift/assert_bypass.py` (+test) | L3-P5-01 | M | `python -m validators.drift.verifier --fixture fixture-a --only bypass_actors_exact --summary` |
| 54 | L3-P5-05 | 5 | Verifier absence for one cycle is Level 5 | `validators/drift/liveness.py` (+test) | L3-P5-01 | S | `python -m pytest validators/drift/tests/test_liveness.py -q` |
| 55 | L3-P5-06 | 5 | AT-110 credential-bounds probe (six negative attempts) | `validators/drift/credential_bounds.py` (+test) | L3-P3-02 | L | `python -m pytest validators/drift/tests/test_credential_bounds.py -q` |
| 56 | L3-P5-07 | 5 | Behavioural-envelope checks | `reconciler/envelope.py` (+test) | L3-P1-18 | L | `python -m pytest reconciler/tests/test_envelope.py -q` |
| 57 | L3-P5-08 | 5 | Records-repo head SHA anchor | `reconciler/anchor.py` (+test) | L3-P1-18 | M | `python -m pytest reconciler/tests/test_anchor.py -q` |
| 58 | L3-P6-01 | 6 | Stricter-only predicate and its proof suite | `reconciler/repair/stricter.py` (+test) | L3-P1-19 | L | `python -m pytest reconciler/tests/test_stricter.py -q` |
| 59 | L3-P6-02 | 6 | Repair enablement registry, every class default-off | `reconciler/repair/enablement.py` (+test) | L3-P6-01 | M | `python -m reconciler.cli repair-classes --summary` |
| 60 | L3-P6-03 | 6 | Repair class: Team membership sync | `reconciler/repair/team_sync.py` (+test) | L3-P6-02 | M | `python -m pytest reconciler/tests/test_repair_team_sync.py -q` |
| 61 | L3-P6-04 | 6 | Repair class: CODEOWNERS regeneration | `reconciler/repair/codeowners_regen.py` (+test) | L3-P6-02, L3-P4-02 | M | `python -m pytest reconciler/tests/test_repair_codeowners.py -q` |
| 62 | L3-P6-05 | 6 | Repair class: re-apply declared branch protection | `reconciler/repair/protection_reapply.py` (+test) | L3-P6-02, L3-P4-03 | M | `python -m pytest reconciler/tests/test_repair_protection.py -q` |
| 63 | L3-P6-06 | 6 | Repair class: expired assignment and expired access removal | `reconciler/repair/expiry_revoke.py` (+test) | L3-P6-02 | M | `python -m pytest reconciler/tests/test_repair_expiry.py -q` |
| 64 | L3-P6-07 | 6 | Repair class: label and board field sync | `reconciler/repair/label_sync.py` (+test) | L3-P6-02 | M | `python -m pytest reconciler/tests/test_repair_labels.py -q` |
| 65 | L3-P6-08 | 6 | Repair record emitter | `reconciler/repair/records.py` (+test) | L3-P6-02 | M | `python -m pytest reconciler/tests/test_repair_records.py -q` |
| 66 | L3-P6-09 | 6 | Prohibited-repair guards | `reconciler/repair/guards.py` (+test) | L3-P6-01 | M | `python -m pytest reconciler/tests/test_repair_guards.py -q` |
| 67 | L3-P6-10 | 6 | Repeated failed repair escalates to Level 5 | `reconciler/repair/escalation.py` (+test) | L3-P6-08 | S | `python -m pytest reconciler/tests/test_repair_escalation.py -q` |
| 68 | L3-P7-01 | 7 | `change-role` operation | `tools/provision/change_role.py` (+test) | L3-P4-09 | L | `python -m tools.provision.cli change-role --fixture fixture-a --login dev-1 --to-role qa --dry-run --summary` |
| 69 | L3-P7-02 | 7 | `remove-person` operation | `tools/provision/remove_person.py` (+test) | L3-P2-05, L3-P4-09 | L | `python -m tools.provision.cli remove-person --fixture fixture-a --login dev-1 --dry-run --summary` |
| 70 | L3-P7-03 | 7 | Registry-edit canary staging | `reconciler/staging.py` (+test) | L3-P6-02 | L | `python -m pytest reconciler/tests/test_staging.py -q` |
| 71 | L3-P7-04 | 7 | Authority-delta detector | `validators/drift/authority_delta.py` (+test) | L3-P7-03 | M | `python -m pytest validators/drift/tests/test_authority_delta.py -q` |
| 72 | L3-P7-05 | 7 | Temporary-person expiry treated as an exit | `tools/provision/temp_expiry.py` (+test) | L3-P7-02 | M | `python -m pytest tools/provision/tests/test_temp_expiry.py -q` |
| 73 | L3-P8-01 | 8 | Gap detector and expiry replay | `reconciler/gap/detect.py` (+test) | L3-P6-06 | M | `python -m pytest reconciler/tests/test_gap_detect.py -q` |
| 74 | L3-P8-02 | 8 | Gap diff-audit of the gap window | `reconciler/gap/audit.py` (+test) | L3-P8-01 | L | `python -m pytest reconciler/tests/test_gap_audit.py -q` |
| 75 | L3-P8-03 | 8 | `gap-window` marking | `reconciler/gap/marking.py` (+test) | L3-P8-01 | M | `python -m pytest reconciler/tests/test_gap_marking.py -q` |
| 76 | L3-P8-04 | 8 | Wrong-repair freeze and revert branch | `reconciler/gap/wrong_repair.py` (+test) | L3-P6-08 | L | `python -m pytest reconciler/tests/test_wrong_repair.py -q` |
| 77 | L3-P8-05 | 8 | Lane acceptance-matrix runner | `reconciler/acceptance/run_matrix.py` (+test) | all above | M | `python -m reconciler.acceptance.run_matrix --summary` |
| 78 | L3-P8-06 | 8 | Lane handoff manifest | `reconciler/HANDOFF.md` | L3-P8-05 | S | `bash reconciler/scripts/check-handoff.sh` |

**Sizes:** S under half a day · M half a day to two days · L two to five days.

---

## 3. Phase 0 — Lane bootstrap and harness

Goal: a package that imports, a fixture that is the single source of every expected number in this file, and a finding model carrying the §53.4 scale. Nothing here touches GitHub.

---

### L3-P0-01 — Lane tree and ownership marker

**Phase** 0 · **Size** S · **Deps** — · **Spec** `PARTITION.md` §"STRICT path ownership"

**Files (create):** `reconciler/README.md`, `tools/provision/README.md`, `validators/drift/README.md`

```bash
set -euo pipefail
[ -n "$CP" ] || { echo "ERROR: CP is not set"; exit 1; }
cd "$CP" && git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/3/p0-01-lane-tree
mkdir -p reconciler tools/provision validators/drift
printf '%s\n' '# reconciler - Lane 3 (Subsystem C). Owned exclusively by lane/3/*.' > reconciler/README.md
printf '%s\n' '# tools/provision - Lane 3 (Subsystem D). Owned exclusively by lane/3/*.' > tools/provision/README.md
printf '%s\n' '# validators/drift - Lane 3 independent control verifier (spec 53.1).' > validators/drift/README.md
git add reconciler/README.md tools/provision/README.md validators/drift/README.md
git commit -m "L3-P0-01: lane tree and ownership marker"
git fetch origin && git rebase origin/integration && git push -u origin lane/3/p0-01-lane-tree
gh pr create --base integration --title "L3-P0-01: lane tree and ownership marker" --body "Lane 3 task L3-P0-01."
```

**Acceptance** — all true:
1. The three README files exist and each names its lane and subsystem.
2. `git diff --name-only origin/integration...HEAD` lists nothing outside the three owned roots.
3. `tools/__init__.py` and `validators/__init__.py` do **not** exist (§0.1 namespace rule).

**SELF-VERIFY**

```bash
ls reconciler/README.md tools/provision/README.md validators/drift/README.md && test ! -e tools/__init__.py && test ! -e validators/__init__.py && echo "P0-01 OK"
```

Expected output, exactly:

```
reconciler/README.md
tools/provision/README.md
validators/drift/README.md
P0-01 OK
```

**STOP** — if `tools/__init__.py` or `validators/__init__.py` already exists on `integration`, do not delete it and do not proceed: another lane owns that parent. File the blocker (§0.6).

---

### L3-P0-02 — Package skeleton and pinned dependencies

**Phase** 0 · **Size** S · **Deps** L3-P0-01, **DECISION L3-D1** · **Spec** §99.1; §101 invariant 85

**Files (create):** `reconciler/__init__.py`, `reconciler/requirements.txt`, `reconciler/scripts/check-ownership.sh`, `reconciler/tests/__init__.py`, `tools/provision/tests/__init__.py`, `validators/drift/tests/__init__.py`

Create the directories, then write the three content files exactly as specified.

`reconciler/__init__.py` — one line: `__version__ = "0.1.0"`

`reconciler/requirements.txt` — exactly two lines, both `==`-pinned:

```
PyYAML==6.0.2
pytest==8.3.3
```

`reconciler/scripts/check-ownership.sh` — a bash script with `set -euo pipefail` that (a) reads `git diff --name-only origin/integration...HEAD` and fails, printing `FOREIGN PATHS:` and the offending lines, if any path does not start with `reconciler/`, `tools/provision/` or `validators/drift/`; (b) fails printing `NAMESPACE VIOLATION` if `tools/__init__.py` or `validators/__init__.py` exists; (c) otherwise prints `OWNERSHIP OK` and exits 0.

```bash
set -euo pipefail
git checkout integration && git pull --ff-only origin integration && git checkout -b lane/3/p0-02-package
mkdir -p reconciler/scripts reconciler/tests tools/provision/tests validators/drift/tests
# write the three content files described above, plus the three empty tests/__init__.py markers
chmod +x reconciler/scripts/check-ownership.sh
python -m pip install -r reconciler/requirements.txt
python -c "import reconciler; print('ok')"
git add reconciler tools/provision/tests validators/drift/tests
git commit -m "L3-P0-02: package skeleton and pinned deps"
git fetch origin && git rebase origin/integration && git push -u origin lane/3/p0-02-package
gh pr create --base integration --title "L3-P0-02: package skeleton and pinned deps" --body "Lane 3 task L3-P0-02."
```

**Acceptance** — all true:
1. `python -c "import reconciler"` succeeds from the repository root.
2. `reconciler/requirements.txt` pins every dependency with `==`; no `>=`, no `~=`, no wildcard (§101 invariant 85).
3. `reconciler/scripts/check-ownership.sh` exits 0 on this branch.

**SELF-VERIFY**

```bash
python -c "import reconciler; print('ok')" && ! grep -Eq '(>=|~=|\*)' reconciler/requirements.txt && bash reconciler/scripts/check-ownership.sh
```

Expected output, exactly:

```
ok
OWNERSHIP OK
```

**STOP** — if L0 has not recorded an answer to **L3-D1**, do not start. If L0 ratified any runtime other than Python 3.12, STOP: every command in this file assumes Python 3.12, and the file must be reissued by L0.

---

### L3-P0-03 — Contract map module

**Phase** 0 · **Size** S · **Deps** L3-P0-02, **DECISION L3-D2** · **Spec** `PARTITION.md` rule 2; §53.1; §26.4

**Files (create):** `reconciler/contracts_map.py`, `reconciler/tests/test_contracts_map.py`

Write `reconciler/contracts_map.py` containing exactly one dictionary named `CONTRACTS` with these five keys — `drift_finding`, `run_record`, `repair_record`, `branch_protection_template`, `environment_template` — whose values are the five paths L0 recorded in **L3-D2**, copied verbatim. Add one function `load(key)` reading the JSON at `CONTRACTS[key]` and raising `FileNotFoundError` naming the key when the path is absent.

Write `reconciler/tests/test_contracts_map.py` with four tests asserting: all five keys present and no sixth; every value starts with `contracts/`; every value exists on disk; `load()` returns a `dict` for each key.

```bash
set -euo pipefail
git checkout integration && git pull --ff-only origin integration && git checkout -b lane/3/p0-03-contracts-map
ls -1 contracts/
# write the two files, copying the five paths verbatim from L0's L3-D2 answer
python -m pytest reconciler/tests/test_contracts_map.py -q
git add reconciler/contracts_map.py reconciler/tests/test_contracts_map.py
git commit -m "L3-P0-03: contract map module"
git fetch origin && git rebase origin/integration && git push -u origin lane/3/p0-03-contracts-map
gh pr create --base integration --title "L3-P0-03: contract map module" --body "Lane 3 task L3-P0-03."
```

**Acceptance** — all true:
1. `CONTRACTS` has exactly the five keys named above, no more.
2. No value is invented: each is copied verbatim from L0's L3-D2 answer.
3. No file under `contracts/` is created or modified.

**SELF-VERIFY**

```bash
python -m pytest reconciler/tests/test_contracts_map.py -q && echo "foreign-contract-writes=$(git diff --name-only origin/integration...HEAD | grep -c '^contracts/')"
```

Expected output, exactly:

```
4 passed
foreign-contract-writes=0
```

**STOP** — if any path in L3-D2's answer does not exist under `contracts/`, do not create it and do not substitute a similar filename. File the blocker naming the missing path.

---

### L3-P0-04 — Fixture set `fixture-a`

**Phase** 0 · **Size** M · **Deps** L3-P0-02 · **Spec** §53.1; §12.2; §11.3; §33.4; §40.1

`fixture-a` is **the single source of every expected number in this file.** Create it exactly as written. Every later SELF-VERIFY count derives from these contents; changing one value silently breaks tasks 9 through 78.

**Files (create):** `reconciler/fixtures/__init__.py`, `reconciler/fixtures/verify.py`, and the sixteen fixture data files below.

```bash
set -euo pipefail
git checkout integration && git pull --ff-only origin integration && git checkout -b lane/3/p0-04-fixture-a
mkdir -p reconciler/fixtures/fixture-a/declared/products reconciler/fixtures/fixture-a/declared/templates reconciler/fixtures/fixture-a/actual/codeowners
```

<!-- CONTESTED(DR-L3-05-A): pre-resolved placeholder — not yet decided by Founder. Do not ship until FD closes DR-L3-05-A. -->
**File 1 —** `reconciler/fixtures/fixture-a/declared/people.yaml`

```yaml
people:
  - github_login: founder-1
    availability: active
    access_status: active
    capabilities: [platform-admin, production-approval, escalation, devops]
  - github_login: lead-1
    availability: active
    access_status: active
    capabilities: [escalation, reviewer-matrix-change, code-review]
  - github_login: dev-1
    availability: active
    access_status: active
    capabilities: [code-review]
  - github_login: dev-2
    availability: departed
    access_status: revoked
    capabilities: []
  - github_login: qa-1
    availability: departing
    end_date: "2026-09-30"
    access_status: active
    capabilities: [verification, code-review]
```

<!-- CONTESTED(DR-L3-05-B): pre-resolved placeholder — not yet decided by Founder. Do not ship until FD closes DR-L3-05-B. -->
**File 2 —** `reconciler/fixtures/fixture-a/declared/products/alpha.yaml`

```yaml
product: alpha
lifecycle: active
restore_tested: "2026-08-01"
assignments:
  primary_owner: lead-1
  cross_reviewer: dev-1
  backup_owner: founder-1
  incident_responder_primary: lead-1
  incident_responder_backup: dev-1
  verification_responsibility: qa-1
temporary_assignments:
  - person: dev-1
    type: temporary_contributor
    end_date: "2026-01-31"
commitments:
  - id: COM-alpha-001
    owner: ""
infrastructure:
  attestation_date: "2026-08-05"
workflow_tag: "workflows/v3"
```

**File 3 —** `reconciler/fixtures/fixture-a/declared/products/beta.yaml`

```yaml
product: beta
lifecycle: active
restore_tested: "2026-08-10"
assignments:
  primary_owner: dev-1
  cross_reviewer: ""
  backup_owner: ""
  incident_responder_primary: ""
  incident_responder_backup: ""
  verification_responsibility: ""
temporary_assignments: []
commitments: []
infrastructure:
  attestation_date: "2026-06-01"
workflow_tag: "workflows/v3"
```

**File 4 —** `reconciler/fixtures/fixture-a/declared/platform.yaml`

```yaml
workflow_tags:
  - tag: "workflows/v3"
    sha: "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
attestation_window_days: 30
```

<!-- CONTESTED(DR-L3-05-C): pre-resolved placeholder — not yet decided by Founder. Do not ship until FD closes DR-L3-05-C. -->
**File 5 —** `reconciler/fixtures/fixture-a/declared/os-health.yaml`

```yaml
drift_budget:
  amber_per_product: 2
  red_portfolio_flat: 3
write_freshness_max_hours:
  "events/": 24
  "records/deployments/": 168
  "records/uat/": 168
```

<!-- CONTESTED(DR-L3-05-D): pre-resolved placeholder — not yet decided by Founder. Do not ship until FD closes DR-L3-05-D. -->
**File 6 —** `reconciler/fixtures/fixture-a/declared/assets.yaml`

```yaml
assets:
  - id: cert-1
    kind: certificate
    owner: qa-1
  - id: domain-1
    kind: domain
    owner: ""
  - id: vendor-1
    kind: vendor
    owner: ""
  - id: opasset-1
    kind: operational
    owner: founder-1
```

**File 7 —** `reconciler/fixtures/fixture-a/declared/policies.yaml`

```yaml
policies:
  - id: POL-001
    owner: ""
```

**File 8 —** `reconciler/fixtures/fixture-a/declared/exceptions.yaml`

```yaml
exceptions:
  - id: EXC-001
    requester: dev-2
    authority: founder-1
    expires: "2026-12-01"
```

**File 9 —** `reconciler/fixtures/fixture-a/declared/shared-services.yaml`

```yaml
services:
  - name: auth-service
    owner: ""
```

<!-- CONTESTED(DR-L3-05-E): pre-resolved placeholder — not yet decided by Founder. Do not ship until FD closes DR-L3-05-E. -->
**File 10 —** `reconciler/fixtures/fixture-a/declared/board.yaml`

```yaml
items:
  - id: WI-101
    horizon: H1
    assignee: ""
  - id: WI-102
    horizon: H1
    assignee: dev-1
open_gate_items:
  - id: REV-9
    holder: dev-1
    kind: security_review
migrations:
  - id: MIG-1
    owner: lead-1
```

**File 11 —** `reconciler/fixtures/fixture-a/declared/templates/branch-protection.json`

```json
{"required_pull_request_reviews":{"required_approving_review_count":1,"require_code_owner_reviews":true,"require_last_push_approval":true,"dismiss_stale_reviews":true},"required_status_checks":{"strict":true,"contexts":["control-plane/blocking-drift"]},"allow_force_pushes":false,"allow_deletions":false,"enforce_admins":true}
```

**File 12 —** `reconciler/fixtures/fixture-a/declared/templates/environment.json`

```json
{"environments":["staging","production"],"deployment_branch_policy":{"protected_branches":true,"custom_branch_policies":false}}
```

**File 13 —** `reconciler/fixtures/fixture-a/actual/org.json`

```json
{
  "members": ["founder-1","lead-1","dev-1","dev-2","qa-1"],
  "teams": {"alpha": ["lead-1","dev-1","founder-1","qa-1","dev-2"], "beta": ["dev-1"]},
  "branch_protection": {
    "alpha": {"required_pull_request_reviews":{"required_approving_review_count":1,"require_code_owner_reviews":true,"require_last_push_approval":true,"dismiss_stale_reviews":true},"required_status_checks":{"strict":true,"contexts":["control-plane/blocking-drift"]},"allow_force_pushes":false,"allow_deletions":false,"enforce_admins":true},
    "beta": {"required_pull_request_reviews":{"required_approving_review_count":1,"require_code_owner_reviews":false,"require_last_push_approval":true,"dismiss_stale_reviews":true},"required_status_checks":{"strict":true,"contexts":["control-plane/blocking-drift"]},"allow_force_pushes":false,"allow_deletions":false,"enforce_admins":true}
  },
  "environments": {
    "alpha": {"staging":{"deployment_branch_policy":{"protected_branches":true,"custom_branch_policies":false}},"production":{"deployment_branch_policy":{"protected_branches":true,"custom_branch_policies":false}}},
    "beta": {"staging":{"deployment_branch_policy":{"protected_branches":true,"custom_branch_policies":false}},"production":{"deployment_branch_policy":null}}
  },
  "workflow_files": {
    "alpha":{"ci.yml":{"uses_tag":"workflows/v3","last_pusher":"ci-bot[bot]","pusher_is_machine":true}},
    "beta":{"ci.yml":{"uses_tag":"workflows/v2","last_pusher":"lead-1","pusher_is_machine":false}}
  },
  "tag_resolution": {"workflows/v3":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"},
  "rulesets": [
    {"name":"renovate-A","rules":["pull_request"],"bypass_actors":["renovate[bot]"]},
    {"name":"renovate-B","rules":["required_status_checks:renovate-path-guard"],"bypass_actors":["renovate[bot]"]}
  ],
  "bypass_branches": [{"branch":"renovate/dep-1","commit_authors":["renovate[bot]","dev-1"],"declared_bypass_actor":"renovate[bot]"}],
  "check_runs": {"alpha":{"control-plane/blocking-drift":{"published_by":"other-bot"}},"beta":{"control-plane/blocking-drift":{"published_by":"reconciler"}}},
  "store_last_write": {"events/":"2026-08-27T06:00:00Z","records/deployments/":"2026-08-01T06:00:00Z","records/uat/":"2026-08-26T06:00:00Z"},
  "restore_test_records": [{"product":"alpha","date":"2026-08-01","result":"pass"}]
}
```

**File 14 —** `reconciler/fixtures/fixture-a/actual/codeowners/alpha.CODEOWNERS`

```
* @lead-1 @dev-1 @founder-1
/verification/ @qa-1
/.github/ @ci-bot
```

**File 15 —** `reconciler/fixtures/fixture-a/actual/codeowners/beta.CODEOWNERS`

```
* @dev-1 @lead-1
```

**File 16 —** `reconciler/fixtures/fixture-a/canary.yaml` — the permanent seeded canary of §53.1

```yaml
canary:
  id: CANARY-001
  comparator: display_name
  product: alpha
  declared_display_name: "Alpha"
  actual_display_name: "Alpha (seeded canary - do not fix)"
  drift_class: Green
```

Then write `reconciler/fixtures/verify.py` — a `__main__` entry taking one positional fixture name, which loads all sixteen data files above, asserts each exists and parses, and prints exactly one line: `FIXTURE <name> files=<int> people=<int> products=<int>`. Also create the empty package marker `reconciler/fixtures/__init__.py`.

```bash
set -euo pipefail
python -m reconciler.fixtures.verify fixture-a
git add reconciler/fixtures
git commit -m "L3-P0-04: fixture-a"
git fetch origin && git rebase origin/integration && git push -u origin lane/3/p0-04-fixture-a
gh pr create --base integration --title "L3-P0-04: fixture-a" --body "Lane 3 task L3-P0-04."
```

**Acceptance** — all true:
1. All sixteen data files plus `verify.py` and `__init__.py` exist, with exactly the content shown.
2. `verify.py` parses all of them without error.
3. No fixture file names a real GitHub organisation, a real person's login, or any credential.

**SELF-VERIFY**

```bash
python -m reconciler.fixtures.verify fixture-a
```

Expected output, exactly:

```
FIXTURE fixture-a files=16 people=5 products=2
```

**STOP** — if `files=` is anything other than `16`, you have added or omitted a fixture data file. Do not adjust the expected number; restore the list above exactly. If it still differs, file the blocker.

---

### L3-P0-05 — Finding model, drift classes, levels

**Phase** 0 · **Size** S · **Deps** L3-P0-03 · **Spec** §53.4 (four classes); §53.2 (five levels); §6.7

**Files (create):** `reconciler/model.py`, `reconciler/tests/test_model.py`

Write `reconciler/model.py` containing exactly:

* `class DriftClass(str, Enum)` with exactly four members: `GREEN`, `AMBER`, `RED`, `BLOCKING`. No fifth member. Module docstring quotes §53.4: *"There is exactly one drift severity scale, used everywhere."*
* `class Level(IntEnum)` with exactly five members: `DETECT=1`, `WARN=2`, `AUTO_REPAIR=3`, `BLOCK=4`, `ESCALATE=5`.
* `RESPONSE_TIME`, transcribed cell for cell from the §53.4 table: `GREEN -> None`, `AMBER -> "next_planning_cycle_h2"`, `RED -> "2_business_days"`, `BLOCKING -> "immediate"`.
* `BLOCKS_WORK`, transcribed cell for cell from the §53.4 table: `GREEN -> False`, `AMBER -> False`, `RED -> False`, `BLOCKING -> True`.
* `@dataclass(frozen=True) class Finding` with fields `id: str`, `comparator: str`, `scope: str`, `drift_class: DriftClass`, `level: Level`, `evidence: str`, `first_seen: str`, `acknowledged_by: str | None = None`, `acknowledged_at: str | None = None`, `external_cause: str | None = None`, `gap_window: bool = False`.
* `def security_floor(drift_class, is_security_or_prod_env)` returning `RED` when the input is `GREEN` or `AMBER` and the flag is true, else the input unchanged — §53.4: *"Security drift and production environment drift are never classified below Red."*

Write six tests asserting: exactly four `DriftClass` members; exactly five `Level` members; `RESPONSE_TIME` matches §53.4; `BLOCKS_WORK` matches §53.4; `security_floor(GREEN, True) is RED` and `security_floor(BLOCKING, True) is BLOCKING`; `Finding` is immutable (attribute assignment raises).

```bash
set -euo pipefail
git checkout integration && git pull --ff-only origin integration && git checkout -b lane/3/p0-05-model
# write the two files
python -m pytest reconciler/tests/test_model.py -q
git add reconciler/model.py reconciler/tests/test_model.py
git commit -m "L3-P0-05: finding model, drift classes, levels"
git fetch origin && git rebase origin/integration && git push -u origin lane/3/p0-05-model
gh pr create --base integration --title "L3-P0-05: finding model, drift classes, levels" --body "Lane 3 task L3-P0-05."
```

**Acceptance** — all true:
1. `len(DriftClass) == 4` and `len(Level) == 5`.
2. No retired severity vocabulary is used as a value or member name anywhere in the module (§53.4: *"No other severity vocabulary exists anywhere in this system"*).
3. `Finding` is frozen.

**SELF-VERIFY**

```bash
python -m pytest reconciler/tests/test_model.py -q && python -c "
from reconciler.model import DriftClass, Level
print('classes', len(DriftClass), 'levels', len(Level))"
```

Expected output, exactly:

```
6 passed
classes 4 levels 5
```

**STOP** — if a later task appears to need a fifth drift class or a sixth level, stop: that is a spec change, not an implementation choice. File the blocker addressed to L0.

---

### L3-P0-06 — `GitHubState` port and fixture adapter

**Phase** 0 · **Size** M · **Deps** L3-P0-04, L3-P0-05 · **Spec** §0.4 above; §53.1; §53.3

**Files (create):** `reconciler/state/__init__.py`, `reconciler/state/port.py`, `reconciler/state/fixture_adapter.py`, `reconciler/state/live_adapter.py`, `reconciler/tests/test_state.py`

Write `port.py` with abstract class `GitHubState` exposing exactly these twelve read methods and **no write method of any kind**: `org_members()`, `team_members(product)`, `branch_protection(repo)`, `environments(repo)`, `codeowners(repo)`, `workflow_files(repo)`, `resolve_tag(tag)`, `rulesets()`, `bypass_branches()`, `check_runs(repo)`, `store_last_write()`, `restore_test_records()`.

Write `fixture_adapter.py` (`class FixtureState`) implementing every method by reading `reconciler/fixtures/<name>/actual/`. Write `live_adapter.py` implementing the same interface against the GitHub REST API, gated behind an explicit `--live` flag; it is never exercised by any acceptance command in this file.

Tests assert: `GitHubState` has zero methods whose name begins `set_`, `write_`, `create_`, `delete_`, `update_` or `put_`; `FixtureState('fixture-a')` returns 5 org members, an alpha team of 5, and a beta team of 1.

```bash
set -euo pipefail
git checkout integration && git pull --ff-only origin integration && git checkout -b lane/3/p0-06-state
# write the five files
python -m pytest reconciler/tests/test_state.py -q
git add reconciler/state reconciler/tests/test_state.py
git commit -m "L3-P0-06: GitHubState port and fixture adapter"
git fetch origin && git rebase origin/integration && git push -u origin lane/3/p0-06-state
gh pr create --base integration --title "L3-P0-06: GitHubState port and fixture adapter" --body "Lane 3 task L3-P0-06."
```

**Acceptance** — all true:
1. `GitHubState` exposes read methods only. This is the mechanical half of safety rule 2 (§0.3): the detect path physically cannot write.
2. The fixture adapter reads only from `reconciler/fixtures/**`.
3. `live_adapter.py` issues no request unless `--live` is passed.

**SELF-VERIFY**

```bash
python -m pytest reconciler/tests/test_state.py -q && python -c "
from reconciler.state.fixture_adapter import FixtureState
s=FixtureState('fixture-a')
print('members', len(s.org_members()), 'alpha', len(s.team_members('alpha')), 'beta', len(s.team_members('beta')))"
```

Expected output, exactly:

```
5 passed
members 5 alpha 5 beta 1
```

**STOP** — if a comparator later seems to need a write method on `GitHubState`, stop. Writes belong only to `reconciler/repair/**` behind the Phase 6 enablement registry. File the blocker.

---

### L3-P0-07 — Run record writer and summary line

**Phase** 0 · **Size** M · **Deps** L3-P0-06 · **Spec** §53.1 *"Every reconciliation run writes its result, and a clean run is recorded as clean"*; §0.5 above; §40.1 (D89)

**Files (create):** `reconciler/runrecord.py`, `reconciler/tests/test_runrecord.py`

Write `runrecord.py` with `class RunRecord` holding `run_id`, `started_at`, `finished_at`, `status` (`OK` | `FAILED`), `findings: list[Finding]`, `comparison_counts: dict[str, int]`, `canary_found: bool`, `external_cause: str | None`. Provide `to_dict()` shaped to the `run_record` contract from `contracts_map`; `summary_lines()` returning the §0.5 lines in order (one per comparator, then the `CANARY` line); and `write(path)` serialising to YAML that **raises** if `path` starts with `records/` or `events/`.

Five tests: summary format byte-exact; a zero-finding record still serialises with `status` present; `write()` refuses `records/`; `write()` refuses `events/`; `to_dict()` keys match the contract's required key list.

```bash
set -euo pipefail
git checkout integration && git pull --ff-only origin integration && git checkout -b lane/3/p0-07-runrecord
# write the two files
python -m pytest reconciler/tests/test_runrecord.py -q
git add reconciler/runrecord.py reconciler/tests/test_runrecord.py
git commit -m "L3-P0-07: run record writer and summary line"
git fetch origin && git rebase origin/integration && git push -u origin lane/3/p0-07-runrecord
gh pr create --base integration --title "L3-P0-07: run record writer and summary line" --body "Lane 3 task L3-P0-07."
```

**Acceptance** — all true:
1. Summary lines match §0.5 byte for byte.
2. `write()` refuses any path under `records/` or `events/` — safety rule 4, and negative attempt 5 of AT-110.
3. A clean run produces a record, not an empty file (§53.1: *"a clean run is recorded as clean"*).

**SELF-VERIFY**

```bash
python -m pytest reconciler/tests/test_runrecord.py -q && python -c "
from reconciler.runrecord import RunRecord
r=RunRecord(run_id='R1',started_at='2026-08-27T00:00:00Z',finished_at='2026-08-27T00:01:00Z',status='OK',findings=[],comparison_counts={'demo':3},canary_found=True,external_cause=None)
print('\n'.join(r.summary_lines()))
try:
    r.write('records/x.yaml'); print('LEAK')
except Exception: print('REFUSED records/')"
```

Expected output, exactly:

```
5 passed
OK demo findings=0 compared=3
CANARY found
REFUSED records/
```

**STOP** — if a later task appears to require writing the run record into the records repository, stop: `records/**` belongs to Lane 4 and the reconciler credential must not reach it (§40.1 D89; AT-110). File the blocker requesting a contract-mediated handoff.

---

## 4. Phase 1 — The comparison set (detect only)

Every task in this phase adds exactly one row of the §53.1 declared-versus-actual table, or one instrument-integrity control. **No repair code is written in this phase** (§98.2 Phase 3: *"Auto-repair is not built here"*).

Each comparator module exposes one function `compare(declared, actual, as_of) -> tuple[list[Finding], int]` returning findings and the compared-row count, and registers itself under its `id`.

---

### L3-P1-01 — Comparator registry and `reconciler.cli`

**Phase** 1 · **Size** M · **Deps** L3-P0-07 · **Spec** §53.1; §0.5 above

**Files (create):** `reconciler/registry.py`, `reconciler/cli.py`, `reconciler/comparators/__init__.py`, `reconciler/tests/test_cli.py`

`registry.py`: a `COMPARATORS: dict[str, Callable]` populated by a `@comparator("<id>")` decorator, each registration also declaring the comparator's fail mode class (consumed in L3-P1-19). `cli.py`: subcommands `list` (prints each registered id, one per line, sorted) and `run` with flags `--fixture <name>`, `--only <id>` (repeatable), `--as-of <YYYY-MM-DD>` (default: today, UTC), `--summary`, `--format json`, `--live`. Exit codes per §0.5.

```bash
set -euo pipefail
git checkout integration && git pull --ff-only origin integration && git checkout -b lane/3/p1-01-registry
# write the four files
python -m reconciler.cli list
python -m pytest reconciler/tests/test_cli.py -q
git add reconciler/registry.py reconciler/cli.py reconciler/comparators reconciler/tests/test_cli.py
git commit -m "L3-P1-01: comparator registry and CLI"
git fetch origin && git rebase origin/integration && git push -u origin lane/3/p1-01-registry
gh pr create --base integration --title "L3-P1-01: comparator registry and CLI" --body "Lane 3 task L3-P1-01."
```

**Acceptance** — all true:
1. `python -m reconciler.cli list` exits 0 and prints nothing (no comparator is registered yet).
2. `--as-of` is honoured; no comparator may call the wall clock directly — all time comes from `as_of`. Without this, no SELF-VERIFY in this file is reproducible.
3. Exit codes are exactly `0`, `2`, `3` as §0.5 specifies.

**SELF-VERIFY**

```bash
python -m reconciler.cli list; echo "exit=$?"; grep -rn "datetime.now\|date.today" reconciler/comparators/ | wc -l
```

Expected output, exactly:

```
exit=0
0
```

**STOP** — if a comparator you write later needs the wall clock rather than `--as-of`, stop and file the blocker: a non-deterministic comparator cannot be accepted by any command in this file.

---

### L3-P1-02 — Comparator: `people.yaml` vs organisation membership

**Phase** 1 · **Size** M · **Deps** L3-P1-01 · **Spec** §53.1 row 1 (*"Alert; block on removal drift"*); §11.2; §12.2

**Files (create):** `reconciler/comparators/org_membership.py`, `reconciler/tests/test_org_membership.py`

Rule, exactly: for each person in `people.yaml`, compare `access_status`/`availability` against `org_members()`. A person whose `access_status` is `revoked` or whose `availability` is `departed`, **and who is still an organisation member**, is *removal drift*: emit `DriftClass.BLOCKING`, `Level.BLOCK`. A person `active` and absent from the organisation is `AMBER`, `Level.WARN`. `compared` = number of people rows examined.

```bash
set -euo pipefail
git checkout integration && git pull --ff-only origin integration && git checkout -b lane/3/p1-02-org-membership
# write the two files
python -m reconciler.cli run --fixture fixture-a --only org_membership --summary
python -m pytest reconciler/tests/test_org_membership.py -q
git add reconciler/comparators/org_membership.py reconciler/tests/test_org_membership.py
git commit -m "L3-P1-02: org membership comparator"
git fetch origin && git rebase origin/integration && git push -u origin lane/3/p1-02-org-membership
gh pr create --base integration --title "L3-P1-02: org membership comparator" --body "Lane 3 task L3-P1-02."
```

**Acceptance** — all true:
1. On `fixture-a`, exactly one finding: `dev-2`, class `BLOCKING` (declared `departed`/`revoked`, still an organisation member).
2. `compared` equals 5 (all people rows), satisfying the §53.1 per-registry comparison-count rule.
3. The comparator emits findings only; it revokes nothing.

**SELF-VERIFY**

```bash
python -m reconciler.cli run --fixture fixture-a --only org_membership --summary; echo "exit=$?"
```

Expected output, exactly:

```
OK org_membership findings=1 compared=5
CANARY missing
exit=2
```

**STOP** — if `exit` is `0`, the Blocking class is not reaching the exit code; if `findings` is not `1`, `fixture-a` has been altered. Either way, file the blocker.

---

### L3-P1-03 — Comparator: capabilities vs team-implied authority

**Phase** 1 · **Size** M · **Deps** L3-P1-01 · **Spec** §53.1 row 2 (*"Alert"*); §11.2

**Files (create):** `reconciler/comparators/capability_authority.py`, `reconciler/tests/test_capability_authority.py`

Rule, exactly: Team membership implies Write (§11.2). For each person, if they appear in any product Team but hold no capability in `people.yaml` implying that authority (`code-review`, `verification`, `devops`, `platform-admin`, `escalation`), emit `AMBER`, `Level.WARN`. `compared` = number of people rows.

Follow the same branch/commit/push/PR sequence as L3-P1-02, with branch `lane/3/p1-03-capability-authority`.

**Commands**

```bash
set -euo pipefail
git checkout integration && git pull --ff-only origin integration && git checkout -b lane/3/p1-03-capability-authority
# write: reconciler/comparators/capability_authority.py, reconciler/tests/test_capability_authority.py
git add reconciler/comparators/capability_authority.py reconciler/tests/test_capability_authority.py
git commit -m "L3-P1-03: capability vs team-implied authority comparator"
git fetch origin && git rebase origin/integration && git push -u origin lane/3/p1-03-capability-authority
gh pr create --base integration --title "L3-P1-03: capability vs team-implied authority comparator" --body "Lane 3 task L3-P1-03."
```

**Acceptance** — all true:
1. On `fixture-a`, exactly one finding: `dev-2` (in team alpha, capabilities empty).
2. Class is `AMBER`, not `BLOCKING` — §53.1 row 2 says *Alert*, and inventing a stricter class than the table states is a spec violation.
3. `compared` equals 5.

**SELF-VERIFY**

```bash
python -m reconciler.cli run --fixture fixture-a --only capability_authority --summary; echo "exit=$?"
```

Expected output, exactly:

```
OK capability_authority findings=1 compared=5
CANARY missing
exit=0
```

**STOP** — if you believe this row should be Blocking, stop and file the blocker for L0. §53.4: class assignment *"lives in configuration and is reviewable; it is not decided ad hoc during an incident."*

---

### L3-P1-04 — Comparator: `product.yaml` assignments vs GitHub Team membership

**Phase** 1 · **Size** M · **Deps** L3-P1-01 · **Spec** §53.1 row 3 (*"Fail CI on the affected repository"*); §11.2

**Files (create):** `reconciler/comparators/team_membership.py`, `reconciler/tests/test_team_membership.py`

Rule, exactly: for each product, the declared Team is the set of logins holding any current assignment in that product's `assignments` block, plus any unexpired `temporary_assignments`. Any actual Team member outside that set, or any declared holder missing from the Team, is `BLOCKING`, `Level.BLOCK`. `compared` = number of products.

Branch `lane/3/p1-04-team-membership`; same git sequence.

**Commands**

```bash
set -euo pipefail
git checkout integration && git pull --ff-only origin integration && git checkout -b lane/3/p1-04-team-membership
# write: reconciler/comparators/team_membership.py, reconciler/tests/test_team_membership.py
git add reconciler/comparators/team_membership.py reconciler/tests/test_team_membership.py
git commit -m "L3-P1-04: product.yaml assignments vs GitHub Team membership comparator"
git fetch origin && git rebase origin/integration && git push -u origin lane/3/p1-04-team-membership
gh pr create --base integration --title "L3-P1-04: product.yaml assignments vs GitHub Team membership comparator" --body "Lane 3 task L3-P1-04."
```

**Acceptance** — all true:
1. On `fixture-a`, exactly one finding: team `alpha` contains `dev-2`, who holds no assignment.
2. `compared` equals 2.
3. Class is `BLOCKING` — §53.1 row 3 fails CI on the affected repository.

**SELF-VERIFY**

```bash
python -m reconciler.cli run --fixture fixture-a --only team_membership --summary; echo "exit=$?"
```

Expected output, exactly:

```
OK team_membership findings=1 compared=2
CANARY missing
exit=2
```

**STOP** — if a fix seems to require removing `dev-2` from the Team, stop: that is a Level-3 repair and Phase 6 has not started. Detect only (§98.2 Phase 3).

---

### L3-P1-05 — Comparator: assignments vs CODEOWNERS

**Phase** 1 · **Size** M · **Deps** L3-P1-01 · **Spec** §53.1 row 4 (*"Regenerate; alert if hand-edited"*); §11.3 (*"human identities only"*); §37.3

**Files (create):** `reconciler/comparators/codeowners.py`, `reconciler/tests/test_codeowners.py`

Rule, exactly: emit at most one finding per `(repo, reason)`. Reason `machine_identity_present` — any owner entry that is a machine identity (a login ending `[bot]`, or a login absent from `people.yaml`) — class `BLOCKING`, `Level.BLOCK`, because CODEOWNERS is half the machine-authority wall (§37.3, §11.3). Reason `hand_edited` — actual content differs from the content generated from assignments — class `AMBER`, `Level.WARN`. `compared` = number of repositories.

Branch `lane/3/p1-05-codeowners`; same git sequence.

**Commands**

```bash
set -euo pipefail
git checkout integration && git pull --ff-only origin integration && git checkout -b lane/3/p1-05-codeowners
# write: reconciler/comparators/codeowners.py, reconciler/tests/test_codeowners.py
git add reconciler/comparators/codeowners.py reconciler/tests/test_codeowners.py
git commit -m "L3-P1-05: assignments vs CODEOWNERS comparator"
git fetch origin && git rebase origin/integration && git push -u origin lane/3/p1-05-codeowners
gh pr create --base integration --title "L3-P1-05: assignments vs CODEOWNERS comparator" --body "Lane 3 task L3-P1-05."
```

**Acceptance** — all true:
1. On `fixture-a`, exactly two findings: `alpha` → `machine_identity_present` (`@ci-bot`), `beta` → `hand_edited`.
2. `compared` equals 2.
3. The comparator regenerates nothing in this phase.

**SELF-VERIFY**

```bash
python -m reconciler.cli run --fixture fixture-a --only codeowners --summary; echo "exit=$?"
```

Expected output, exactly:

```
OK codeowners findings=2 compared=2
CANARY missing
exit=2
```

**STOP** — if a machine identity in CODEOWNERS is classified below Blocking, stop: §11.3 makes human-only CODEOWNERS the mechanism preventing a machine approval from satisfying a gate. File the blocker.

---

### L3-P1-06 — Comparator: branch-protection template vs actual

**Phase** 1 · **Size** M · **Deps** L3-P1-01 · **Spec** §53.1 row 5 (*"Alert immediately; block deployment on the affected repository"*); §11.3; §53.3; §53.4

**Files (create):** `reconciler/comparators/branch_protection.py`, `reconciler/tests/test_branch_protection.py`

Rule, exactly: deep-compare actual protection against `declared/templates/branch-protection.json`. Any difference that **weakens** a control (a `true` becoming `false`, a required count decreasing, a required context disappearing) is `BLOCKING`, `Level.BLOCK`. Any difference making actual **stricter** than declared is `AMBER`, `Level.WARN`, and is never repaired — §53.3: *"Where actual state is stricter than declared state, reconciliation raises Level 2 for human judgment rather than relaxing the control."* Apply `security_floor()`. `compared` = number of repositories.

Branch `lane/3/p1-06-branch-protection`; same git sequence.

**Commands**

```bash
set -euo pipefail
git checkout integration && git pull --ff-only origin integration && git checkout -b lane/3/p1-06-branch-protection
# write: reconciler/comparators/branch_protection.py, reconciler/tests/test_branch_protection.py
git add reconciler/comparators/branch_protection.py reconciler/tests/test_branch_protection.py
git commit -m "L3-P1-06: branch-protection template vs actual comparator"
git fetch origin && git rebase origin/integration && git push -u origin lane/3/p1-06-branch-protection
gh pr create --base integration --title "L3-P1-06: branch-protection template vs actual comparator" --body "Lane 3 task L3-P1-06."
```

**Acceptance** — all true:
1. On `fixture-a`, exactly one finding: `beta` has `require_code_owner_reviews: false` against a template requiring `true`.
2. Class is `BLOCKING`.
3. A unit test proves the stricter-than-declared direction yields `AMBER` and never a repair proposal (AT-033).

**SELF-VERIFY**

```bash
python -m reconciler.cli run --fixture fixture-a --only branch_protection --summary; echo "exit=$?"
```

Expected output, exactly:

```
OK branch_protection findings=1 compared=2
CANARY missing
exit=2
```

**STOP** — if the stricter-direction test cannot be written because the comparator has no notion of direction, stop and file the blocker: direction is the whole of §53.3, and Phase 6 depends on it.

---

### L3-P1-07 — Comparator: workflow template version vs actual workflow file

**Phase** 1 · **Size** M · **Deps** L3-P1-01 · **Spec** §53.1 row 6 (*"Alert; flag `platform_compatibility` as drifted"*); §33.2

**Files (create):** `reconciler/comparators/workflow_version.py`, `reconciler/tests/test_workflow_version.py`

Rule, exactly: for each repository, compare each workflow file's `uses_tag` against the product's declared `workflow_tag`. A mismatch is `AMBER`, `Level.WARN`, and the finding's `evidence` must contain the literal token `platform_compatibility=drifted`. `compared` = number of repositories.

Branch `lane/3/p1-07-workflow-version`; same git sequence.

**Commands**

```bash
set -euo pipefail
git checkout integration && git pull --ff-only origin integration && git checkout -b lane/3/p1-07-workflow-version
# write: reconciler/comparators/workflow_version.py, reconciler/tests/test_workflow_version.py
git add reconciler/comparators/workflow_version.py reconciler/tests/test_workflow_version.py
git commit -m "L3-P1-07: workflow template version vs actual comparator"
git fetch origin && git rebase origin/integration && git push -u origin lane/3/p1-07-workflow-version
gh pr create --base integration --title "L3-P1-07: workflow template version vs actual comparator" --body "Lane 3 task L3-P1-07."
```

**Acceptance** — all true:
1. On `fixture-a`, exactly one finding: `beta` uses `workflows/v2` against declared `workflows/v3`.
2. The finding's evidence contains `platform_compatibility=drifted`.
3. `compared` equals 2.

**SELF-VERIFY**

```bash
python -m reconciler.cli run --fixture fixture-a --only workflow_version --summary; echo "exit=$?"
python -m reconciler.cli run --fixture fixture-a --only workflow_version --format json | grep -c 'platform_compatibility=drifted'
```

Expected output, exactly:

```
OK workflow_version findings=1 compared=2
CANARY missing
exit=0
1
```

**STOP** — none beyond the standing rule of §0.6.

---

### L3-P1-08 — Comparator: environments and deployment branch/tag policy

**Phase** 1 · **Size** M · **Deps** L3-P1-01 · **Spec** §53.1 rows 7 and 8; §33.4; §40.3

**Files (create):** `reconciler/comparators/environments.py`, `reconciler/tests/test_environments.py`

Rule, exactly: for each repository and each declared environment, compare against `declared/templates/environment.json`. A missing environment is `AMBER`, `Level.WARN` (row 7). A missing, null or widened **deployment branch and tag policy** on `staging` or `production` is `BLOCKING`, `Level.BLOCK` (row 8) — §33.4 and §40.3 make it the control that makes *"accessible only to the production deployment workflow"* true. `compared` = repositories × declared environments.

Branch `lane/3/p1-08-environments`; same git sequence.

**Commands**

```bash
set -euo pipefail
git checkout integration && git pull --ff-only origin integration && git checkout -b lane/3/p1-08-environments
# write: reconciler/comparators/environments.py, reconciler/tests/test_environments.py
git add reconciler/comparators/environments.py reconciler/tests/test_environments.py
git commit -m "L3-P1-08: environments and deployment branch/tag policy comparator"
git fetch origin && git rebase origin/integration && git push -u origin lane/3/p1-08-environments
gh pr create --base integration --title "L3-P1-08: environments and deployment branch/tag policy comparator" --body "Lane 3 task L3-P1-08."
```

**Acceptance** — all true:
1. On `fixture-a`, exactly one finding: `beta`/`production` has `deployment_branch_policy: null`.
2. Class is `BLOCKING`.
3. `compared` equals 4.

**SELF-VERIFY**

```bash
python -m reconciler.cli run --fixture fixture-a --only environments --summary; echo "exit=$?"
```

Expected output, exactly:

```
OK environments findings=1 compared=4
CANARY missing
exit=2
```

**STOP** — if `compared` is 2 rather than 4, the comparator is counting repositories instead of environment rows; §53.1's per-registry counts exist so that *"a silently narrowed comparison is itself visible drift."* Fix the count, do not adjust the expectation.

---

### L3-P1-09 — Comparator: assignment `end_date` vs current Team membership

**Phase** 1 · **Size** M · **Deps** L3-P1-01 · **Spec** §53.1 row 11 (*"Auto-revoke expired access"*); §10.1; §101 invariant 58; AT-008; AT-018

**Files (create):** `reconciler/comparators/expiry.py`, `reconciler/tests/test_expiry.py`

Rule, exactly: for each `temporary_assignments` entry, if `end_date < as_of` and the holder is still in the product Team, emit `BLOCKING`, `Level.BLOCK`, recording `repair_class="expiry_revoke"` on the finding for Phase 6 to consume. Additionally emit an `AMBER`, `Level.WARN` finding for any delegation-type assignment within 14 days of expiry — §10.1: *"Delegation expiry is warned, never silent."* `compared` = number of temporary and delegation assignment rows.

Branch `lane/3/p1-09-expiry`; same git sequence.

**Commands**

```bash
set -euo pipefail
git checkout integration && git pull --ff-only origin integration && git checkout -b lane/3/p1-09-expiry
# write: reconciler/comparators/expiry.py, reconciler/tests/test_expiry.py
git add reconciler/comparators/expiry.py reconciler/tests/test_expiry.py
git commit -m "L3-P1-09: assignment end_date vs current Team membership comparator"
git fetch origin && git rebase origin/integration && git push -u origin lane/3/p1-09-expiry
gh pr create --base integration --title "L3-P1-09: assignment end_date vs current Team membership comparator" --body "Lane 3 task L3-P1-09."
```

**Acceptance** — all true:
1. On `fixture-a` with `--as-of 2026-08-27`, exactly one finding: `dev-1`'s `temporary_contributor` on `alpha`, `end_date 2026-01-31`, still in the Team.
2. `compared` equals 1.
3. **This task revokes nothing.** The `repair_class` tag is metadata; the revocation lands in L3-P6-06.

**SELF-VERIFY**

```bash
python -m reconciler.cli run --fixture fixture-a --as-of 2026-08-27 --only expiry --summary; echo "exit=$?"
```

Expected output, exactly:

```
OK expiry findings=1 compared=1
CANARY missing
exit=2
```

**STOP** — if you are tempted to revoke here because §53.1 says *"Auto-revoke"*, stop. §98.2 Phase 3 says auto-repair is not built in this phase, and §99.4 item 6 defers it until detection has run clean for weeks. Detect now, revoke in Phase 6.

---

### L3-P1-10 — Comparator: `platform.yaml` workflow tag → resolved SHA

**Phase** 1 · **Size** M · **Deps** L3-P1-01 · **Spec** §53.1 row 13 (*"Blocking on any change — a moved tag reaches every consumer with no reviewable diff"*); §33.2

**Files (create):** `reconciler/comparators/workflow_tag_sha.py`, `reconciler/tests/test_workflow_tag_sha.py`

Rule, exactly: for each tag in `platform.yaml.workflow_tags`, compare the declared `sha` against `resolve_tag(tag)`. Any difference is `BLOCKING`, `Level.BLOCK`. There is no Amber form of this row. `compared` = number of declared tags.

Branch `lane/3/p1-10-workflow-tag-sha`; same git sequence.

**Commands**

```bash
set -euo pipefail
git checkout integration && git pull --ff-only origin integration && git checkout -b lane/3/p1-10-workflow-tag-sha
# write: reconciler/comparators/workflow_tag_sha.py, reconciler/tests/test_workflow_tag_sha.py
git add reconciler/comparators/workflow_tag_sha.py reconciler/tests/test_workflow_tag_sha.py
git commit -m "L3-P1-10: platform.yaml workflow tag to resolved SHA comparator"
git fetch origin && git rebase origin/integration && git push -u origin lane/3/p1-10-workflow-tag-sha
gh pr create --base integration --title "L3-P1-10: platform.yaml workflow tag to resolved SHA comparator" --body "Lane 3 task L3-P1-10."
```

**Acceptance** — all true:
1. On `fixture-a`, exactly one finding: `workflows/v3` declared `aaaa…`, resolving to `bbbb…`.
2. Class is `BLOCKING`, with no gradation by magnitude.
3. `compared` equals 1.

**SELF-VERIFY**

```bash
python -m reconciler.cli run --fixture fixture-a --only workflow_tag_sha --summary; echo "exit=$?"
```

Expected output, exactly:

```
OK workflow_tag_sha findings=1 compared=1
CANARY missing
exit=2
```

**STOP** — none beyond the standing rule of §0.6.

---

### L3-P1-11 — Comparator: Renovate bypass ruleset split

**Phase** 1 · **Size** M · **Deps** L3-P1-01 · **Spec** §53.1 row 14 (*"Blocking where that ruleset names any bypass actor"*); §33.2; D89

**Files (create):** `reconciler/comparators/renovate_bypass.py`, `reconciler/tests/test_renovate_bypass.py`

Rule, exactly: identify the ruleset carrying the `renovate-path-guard` required status check (ruleset B). If its `bypass_actors` list is non-empty, emit `BLOCKING`, `Level.BLOCK` — D89: *"a bypass actor is exempt from every rule in the ruleset it is listed on, so a compensator sitting inside the bypassed ruleset compensates for nothing."* Ruleset A, carrying the pull-request rules, may list the Renovate app and is not a finding. `compared` = number of rulesets examined.

Branch `lane/3/p1-11-renovate-bypass`; same git sequence.

**Commands**

```bash
set -euo pipefail
git checkout integration && git pull --ff-only origin integration && git checkout -b lane/3/p1-11-renovate-bypass
# write: reconciler/comparators/renovate_bypass.py, reconciler/tests/test_renovate_bypass.py
git add reconciler/comparators/renovate_bypass.py reconciler/tests/test_renovate_bypass.py
git commit -m "L3-P1-11: Renovate bypass ruleset split comparator"
git fetch origin && git rebase origin/integration && git push -u origin lane/3/p1-11-renovate-bypass
gh pr create --base integration --title "L3-P1-11: Renovate bypass ruleset split comparator" --body "Lane 3 task L3-P1-11."
```

**Acceptance** — all true:
1. On `fixture-a`, exactly one finding: `renovate-B` lists `renovate[bot]`.
2. `renovate-A` produces no finding.
3. `compared` equals 2.

**SELF-VERIFY**

```bash
python -m reconciler.cli run --fixture fixture-a --only renovate_bypass --summary; echo "exit=$?"
```

Expected output, exactly:

```
OK renovate_bypass findings=1 compared=2
CANARY missing
exit=2
```

**STOP** — if both rulesets produce findings, the comparator is not distinguishing the pull-request ruleset from the compensating-check ruleset. Fix the comparator; do not change the fixture.

---

### L3-P1-12 — Comparator: machine workflow-file change and bypass-branch authorship

**Phase** 1 · **Size** M · **Deps** L3-P1-01 · **Spec** §53.1 (both unnumbered paragraphs); §33.2; §40.3

**Files (create):** `reconciler/comparators/machine_authorship.py`, `reconciler/tests/test_machine_authorship.py`

Rule, exactly — two checks in one comparator:

* **A.** Any workflow file whose last push carries `pusher_is_machine: true` is `BLOCKING`, `Level.BLOCK`, *"regardless of the change's content: workflow files define the enforcement path itself, and no machine credential is authorised to alter it"* (§53.1).
* **B.** For each bypass branch, any commit author other than the branch's `declared_bypass_actor` is `BLOCKING`, `Level.BLOCK` — *"a bypass is a grant to one identity, and a branch merging under it must carry that identity's work only"* (§53.1, §33.2).

`compared` = number of workflow files examined plus number of bypass branches examined.

Branch `lane/3/p1-12-machine-authorship`; same git sequence.

**Commands**

```bash
set -euo pipefail
git checkout integration && git pull --ff-only origin integration && git checkout -b lane/3/p1-12-machine-authorship
# write: reconciler/comparators/machine_authorship.py, reconciler/tests/test_machine_authorship.py
git add reconciler/comparators/machine_authorship.py reconciler/tests/test_machine_authorship.py
git commit -m "L3-P1-12: machine workflow-file change and bypass-branch authorship comparator"
git fetch origin && git rebase origin/integration && git push -u origin lane/3/p1-12-machine-authorship
gh pr create --base integration --title "L3-P1-12: machine workflow-file change and bypass-branch authorship comparator" --body "Lane 3 task L3-P1-12."
```

**Acceptance** — all true:
1. On `fixture-a`, exactly two findings: `alpha/ci.yml` pushed by `ci-bot[bot]`; branch `renovate/dep-1` carries a commit by `dev-1`.
2. Both are `BLOCKING`.
3. `compared` equals 2 (one workflow-file row plus one bypass-branch row).

**SELF-VERIFY**

```bash
python -m reconciler.cli run --fixture fixture-a --only machine_authorship --summary; echo "exit=$?"
```

Expected output, exactly:

```
OK machine_authorship findings=2 compared=2
CANARY missing
exit=2
```

**STOP** — if check B is implemented as a warning because "the lockfile-only diff is harmless", stop: §33.2 states *"The authorship half is not optional."* File the blocker rather than downgrading.

---

### L3-P1-13 — Comparator: declared infrastructure boundary vs attestation window

**Phase** 1 · **Size** S · **Deps** L3-P1-01 · **Spec** §53.1 row 9 (*"Blocking past its attestation window"*); §40.2

**Files (create):** `reconciler/comparators/infra_attestation.py`, `reconciler/tests/test_infra_attestation.py`

Rule, exactly: for each product declaring an `infrastructure:` block, if `as_of - attestation_date > platform.yaml.attestation_window_days`, emit `BLOCKING`, `Level.BLOCK`. §40.2: the provider side is verified *"by attestation rather than reconciliation"* — this comparator checks the attestation's freshness and never contacts the provider. `compared` = number of products declaring the block.

Branch `lane/3/p1-13-infra-attestation`; same git sequence.

**Commands**

```bash
set -euo pipefail
git checkout integration && git pull --ff-only origin integration && git checkout -b lane/3/p1-13-infra-attestation
# write: reconciler/comparators/infra_attestation.py, reconciler/tests/test_infra_attestation.py
git add reconciler/comparators/infra_attestation.py reconciler/tests/test_infra_attestation.py
git commit -m "L3-P1-13: declared infrastructure boundary vs attestation window comparator"
git fetch origin && git rebase origin/integration && git push -u origin lane/3/p1-13-infra-attestation
gh pr create --base integration --title "L3-P1-13: declared infrastructure boundary vs attestation window comparator" --body "Lane 3 task L3-P1-13."
```

**Acceptance** — all true:
1. On `fixture-a` with `--as-of 2026-08-27`, exactly one finding: `beta`, attested `2026-06-01`, window 30 days.
2. `alpha` (attested `2026-08-05`, 22 days) produces no finding.
3. The comparator makes no provider-side call of any kind.

**SELF-VERIFY**

```bash
python -m reconciler.cli run --fixture fixture-a --as-of 2026-08-27 --only infra_attestation --summary; echo "exit=$?"
```

Expected output, exactly:

```
OK infra_attestation findings=1 compared=2
CANARY missing
exit=2
```

**STOP** — if implementing this seems to need cloud-provider credentials, stop: §40.2 says *"Reconciliation compares declared state against GitHub state and never leaves it."* File the blocker.

---

### L3-P1-14 — Comparator: record-store write freshness

**Phase** 1 · **Size** M · **Deps** L3-P1-01 · **Spec** §53.1 (*"Declared write-freshness window per record store"*); §97.2 (*"zero is the good value"*)

**Files (create):** `reconciler/comparators/write_freshness.py`, `reconciler/tests/test_write_freshness.py`

Rule, exactly: for each store in `os-health.yaml.write_freshness_max_hours`, compare `as_of` against `store_last_write()`. Past the interval the class is `AMBER` — except for `events/`, `records/deployments/` and `records/uat/`, which are `BLOCKING`, `Level.BLOCK` (§53.1, §97.2). `compared` = number of stores declared.

Branch `lane/3/p1-14-write-freshness`; same git sequence.

**Commands**

```bash
set -euo pipefail
git checkout integration && git pull --ff-only origin integration && git checkout -b lane/3/p1-14-write-freshness
# write: reconciler/comparators/write_freshness.py, reconciler/tests/test_write_freshness.py
git add reconciler/comparators/write_freshness.py reconciler/tests/test_write_freshness.py
git commit -m "L3-P1-14: record-store write freshness comparator"
git fetch origin && git rebase origin/integration && git push -u origin lane/3/p1-14-write-freshness
gh pr create --base integration --title "L3-P1-14: record-store write freshness comparator" --body "Lane 3 task L3-P1-14."
```

**Acceptance** — all true:
1. On `fixture-a` with `--as-of 2026-08-27`, exactly one finding: `records/deployments/`, last written `2026-08-01`, interval 168h.
2. Class is `BLOCKING`, not `AMBER` — `records/deployments/` is on the blocking list.
3. `compared` equals 3.

**SELF-VERIFY**

```bash
python -m reconciler.cli run --fixture fixture-a --as-of 2026-08-27 --only write_freshness --summary; echo "exit=$?"
```

Expected output, exactly:

```
OK write_freshness findings=1 compared=3
CANARY missing
exit=2
```

**STOP** — none beyond the standing rule of §0.6.

---

### L3-P1-15 — Comparator: `restore_tested` vs the restore-test records

**Phase** 1 · **Size** M · **Deps** L3-P1-01 · **Spec** §53.1 final row (*"Blocking: a declared date with no matching record is an unevidenced reliability claim, not a scheduling question"*); §101 invariants 3 and 4; §44.2

**Files (create):** `reconciler/comparators/restore_tested.py`, `reconciler/tests/test_restore_tested.py`

Rule, exactly: for each product, the declared `restore_tested` date must match a passing record in `restore_test_records()` for that product. No matching record is `BLOCKING`, `Level.BLOCK`. `compared` = number of products declaring `restore_tested`.

Branch `lane/3/p1-15-restore-tested`; same git sequence.

**Commands**

```bash
set -euo pipefail
git checkout integration && git pull --ff-only origin integration && git checkout -b lane/3/p1-15-restore-tested
# write: reconciler/comparators/restore_tested.py, reconciler/tests/test_restore_tested.py
git add reconciler/comparators/restore_tested.py reconciler/tests/test_restore_tested.py
git commit -m "L3-P1-15: restore_tested vs restore-test records comparator"
git fetch origin && git rebase origin/integration && git push -u origin lane/3/p1-15-restore-tested
gh pr create --base integration --title "L3-P1-15: restore_tested vs restore-test records comparator" --body "Lane 3 task L3-P1-15."
```

**Acceptance** — all true:
1. On `fixture-a`, exactly one finding: `beta` declares `2026-08-10` with no matching record.
2. `alpha` matches its `2026-08-01` passing record and produces no finding.
3. `compared` equals 2.

**SELF-VERIFY**

```bash
python -m reconciler.cli run --fixture fixture-a --as-of 2026-08-27 --only restore_tested --summary; echo "exit=$?"
```

Expected output, exactly:

```
OK restore_tested findings=1 compared=2
CANARY missing
exit=2
```

**STOP** — none beyond the standing rule of §0.6.

---

### L3-P1-16 — Per-registry comparison counts on the run record

**Phase** 1 · **Size** S · **Deps** L3-P1-02 … L3-P1-15 · **Spec** §53.1 (*"Every run additionally records its per-registry comparison counts … so that a silently narrowed comparison is itself visible drift"*)

**Files (edit):** `reconciler/runrecord.py` · **Files (create):** `reconciler/tests/test_counts.py`

Aggregate every comparator's `compared` value into `comparison_counts`, keyed by comparator id. Add `EXPECTED_MINIMUM_COUNTS` in `reconciler/runrecord.py` holding the nineteen values per FD-061 (L3-01 authoritative; was fourteen). <!-- 19 per FD-061. The fourteen entries from L3-P1-02 … L3-P1-15 are: --> `org_membership=5`, `capability_authority=5`, `team_membership=2`, `codeowners=2`, `branch_protection=2`, `workflow_version=2`, `environments=4`, `expiry=1`, `workflow_tag_sha=1`, `renovate_bypass=2`, `machine_authorship=2`, `infra_attestation=2`, `write_freshness=3`, `restore_tested=2`<!-- ; plus display_name=1 (L3-P1-17), checkrun_identity=2 (L3-P3-03), and three additional comparators per L3-01 CMP-15..CMP-19 reconciliation — values TBD when L3-01 and L3-06 plans are merged. -->. A run whose actual count for any comparator falls **below** its expected minimum sets `status="FAILED"`.

Branch `lane/3/p1-16-counts`; same git sequence.

**Commands**

```bash
set -euo pipefail
git checkout integration && git pull --ff-only origin integration && git checkout -b lane/3/p1-16-counts
# write: reconciler/runrecord.py, reconciler/tests/test_counts.py
git add reconciler/runrecord.py reconciler/tests/test_counts.py
git commit -m "L3-P1-16: per-registry comparison counts on the run record"
git fetch origin && git rebase origin/integration && git push -u origin lane/3/p1-16-counts
gh pr create --base integration --title "L3-P1-16: per-registry comparison counts on the run record" --body "Lane 3 task L3-P1-16."
```

**Acceptance** — all true:
1. A full `fixture-a` run records all nineteen counts. <!-- 19 per FD-061 (L3-01 authoritative); was fourteen -->
2. Artificially lowering one comparator's count in a test flips `status` to `FAILED` — a narrowed comparison is drift, not silence.
3. The expected-minimum table lives in code and is asserted by test, not written as a comment.

**SELF-VERIFY**

```bash
python -m pytest reconciler/tests/test_counts.py -q && python -m reconciler.cli run --fixture fixture-a --as-of 2026-08-27 --format json | python -c "import json,sys; d=json.load(sys.stdin); print('counts', len(d['comparison_counts']))"
```

Expected output, exactly:

```
3 passed
counts 19
```

<!-- 19 per FD-061 (L3-01 authoritative); was counts 14. The full 19 requires tasks through L3-P1-17, L3-P3-03, and three additional comparators per L3-01 reconciliation. -->

**STOP** — if `counts` is fewer than 19, one or more comparators are not yet merged to `integration`. Do not lower the table; complete the missing tasks first. <!-- Per FD-061 the target is 19, not 14. -->

---

### L3-P1-17 — Seeded canary and the zero-findings FAIL rule

**Phase** 1 · **Size** M · **Deps** L3-P1-16 · **Spec** §53.1 seeded-canary rule; **AT-102**; SIG-13; §95.4

**Files (create):** `reconciler/canary.py`, `reconciler/comparators/display_name.py`, `reconciler/tests/test_canary.py`

Implement the `display_name` comparator (Green class, §53.2 Level 1) reading `canary.yaml` and reporting the seeded mismatch. Implement `canary.py` with `assert_canary(findings) -> bool`, true only when a finding whose `id` equals the canary's `id` is present. Wire the run so that:

* the canary finding is **never** counted toward any drift budget and is **never** repairable;
* a run whose findings list is empty, **or which does not contain the canary**, sets `status="FAILED"` and exits `3`. AT-102: *"a reconciler that finds nothing is assumed broken, never assumed clean."*

Branch `lane/3/p1-17-canary`; same git sequence.

**Commands**

```bash
set -euo pipefail
git checkout integration && git pull --ff-only origin integration && git checkout -b lane/3/p1-17-canary
# write: reconciler/canary.py, reconciler/comparators/display_name.py, reconciler/tests/test_canary.py
git add reconciler/canary.py reconciler/comparators/display_name.py reconciler/tests/test_canary.py
git commit -m "L3-P1-17: seeded canary and zero-findings FAIL rule"
git fetch origin && git rebase origin/integration && git push -u origin lane/3/p1-17-canary
gh pr create --base integration --title "L3-P1-17: seeded canary and zero-findings FAIL rule" --body "Lane 3 task L3-P1-17."
```

**Acceptance** — all true:
1. A normal `fixture-a` run prints `CANARY found`.
2. A test suppressing the canary produces `status=FAILED` and exit code `3`, **even though other findings exist**.
3. A test suppressing all findings produces `status=FAILED` and exit code `3`.

**SELF-VERIFY**

```bash
python -m pytest reconciler/tests/test_canary.py -q && python -m reconciler.cli run --fixture fixture-a --as-of 2026-08-27 --summary | tail -1
```

Expected output, exactly:

```
4 passed
CANARY found
```

**STOP** — if it seems reasonable to treat a canary-missing run as merely Amber, stop: AT-102 makes it a **failed run**. File the blocker rather than softening it.

---

### L3-P1-18 — Run annotations: `external-cause`, `acknowledged_by/at`, clean-run record

**Phase** 1 · **Size** S · **Deps** L3-P1-17 · **Spec** §53.1 (all three annotation paragraphs)

**Files (create):** `reconciler/annotations.py`, `reconciler/tests/test_annotations.py`

Implement: `annotate_external_cause(run, outage_ref)` setting `run.external_cause`, naming the outage, suppressing raw Red escalation for that run, and marking it for re-execution once the dependency recovers; `acknowledge(finding, by, at)` writing `acknowledged_by`/`acknowledged_at` and refusing to overwrite an existing acknowledgement, so a second responder sees the interrupt is already claimed; `record_clean(run)` producing a full run record for a run with no findings beyond the canary.

Branch `lane/3/p1-18-annotations`; same git sequence.

**Commands**

```bash
set -euo pipefail
git checkout integration && git pull --ff-only origin integration && git checkout -b lane/3/p1-18-annotations
# write: reconciler/annotations.py, reconciler/tests/test_annotations.py
git add reconciler/annotations.py reconciler/tests/test_annotations.py
git commit -m "L3-P1-18: run annotations: external-cause, acknowledged_by/at, clean-run record"
git fetch origin && git rebase origin/integration && git push -u origin lane/3/p1-18-annotations
gh pr create --base integration --title "L3-P1-18: run annotations: external-cause, acknowledged_by/at, clean-run record" --body "Lane 3 task L3-P1-18."
```

**Acceptance** — all true:
1. An `external-cause` run names the outage and is marked for re-execution.
2. A second `acknowledge()` on an already-claimed finding raises rather than overwrites.
3. A clean run still produces a record — §53.1: *"a clean run is recorded as clean."*

**SELF-VERIFY**

```bash
python -m pytest reconciler/tests/test_annotations.py -q
```

Expected output, exactly:

```
5 passed
```

**STOP** — none beyond the standing rule of §0.6.

---

### L3-P1-19 — Fail-closed matrix for Blocking-class checks

**Phase** 1 · **Size** M · **Deps** L3-P1-17 · **Spec** §64.2 (*"Reconciliation: fail closed for Blocking-class checks; fail open with an alert for Green-class checks"*); §101 invariant 80

**Files (create):** `reconciler/failmode.py`, `reconciler/tests/test_failmode.py`

Implement `FAIL_MODE: dict[DriftClass, str]` = `{BLOCKING: "closed", RED: "closed", AMBER: "open_with_alert", GREEN: "open_with_alert"}`, and `on_comparator_error(comparator_id, drift_class, exc)`: for a fail-closed class, a comparator's inability to execute is itself a `BLOCKING` finding (§64.2: *"Detection failure must not silently permit drift"*); for a fail-open class, emit an `AMBER` finding naming the alert path and continue. Every comparator must declare its class in the registry; an undeclared comparator fails (§64.2: *"Unclassified controls fail CI"*; §101 invariant 80).

Branch `lane/3/p1-19-failmode`; same git sequence.

**Commands**

```bash
set -euo pipefail
git checkout integration && git pull --ff-only origin integration && git checkout -b lane/3/p1-19-failmode
# write: reconciler/failmode.py, reconciler/tests/test_failmode.py
git add reconciler/failmode.py reconciler/tests/test_failmode.py
git commit -m "L3-P1-19: fail-closed matrix for Blocking-class checks"
git fetch origin && git rebase origin/integration && git push -u origin lane/3/p1-19-failmode
gh pr create --base integration --title "L3-P1-19: fail-closed matrix for Blocking-class checks" --body "Lane 3 task L3-P1-19."
```

**Acceptance** — all true:
1. A comparator raising an exception in a fail-closed class yields a `BLOCKING` finding, never a silent skip.
2. A comparator with no declared class makes `python -m reconciler.cli list` exit non-zero.
3. `FAIL_MODE` matches the §64.2 reconciliation row exactly.

**SELF-VERIFY**

```bash
python -m pytest reconciler/tests/test_failmode.py -q && python -c "
from reconciler.failmode import FAIL_MODE
from reconciler.model import DriftClass
print(FAIL_MODE[DriftClass.BLOCKING], FAIL_MODE[DriftClass.GREEN])"
```

Expected output, exactly:

```
6 passed
closed open_with_alert
```

**STOP** — none beyond the standing rule of §0.6.

---

### L3-P1-20 — SIG-13 emission on a failed run

**Phase** 1 · **Size** S · **Deps** L3-P1-17, L3-P1-18 · **Spec** §52.2 SIG-13 (*"Reconciliation job failures, or unresolved findings older than their class response time"* — source Reconciliation, default class Red, owner Team Lead); §52.4 (SIG-13 is P0); AT-032; AT-102

**Files (create):** `reconciler/signals.py`, `reconciler/tests/test_signals.py`

Implement `emit_signals(run) -> list[dict]` producing a SIG-13 entry when `run.status == "FAILED"`, and a further SIG-13 entry for any finding older than the §53.4 response time of its class (`RED` → 2 business days, `BLOCKING` → immediate). Each entry carries `signal_id="SIG-13"`, `drift_class="Red"` and `owner="team_lead"`, transcribed from the §52.2 row. **Emit only** — routing belongs to Lane 5 (`notify/**`).

Branch `lane/3/p1-20-signals`; same git sequence.

**Commands**

```bash
set -euo pipefail
git checkout integration && git pull --ff-only origin integration && git checkout -b lane/3/p1-20-signals
# write: reconciler/signals.py, reconciler/tests/test_signals.py
git add reconciler/signals.py reconciler/tests/test_signals.py
git commit -m "L3-P1-20: SIG-13 emission on a failed run"
git fetch origin && git rebase origin/integration && git push -u origin lane/3/p1-20-signals
gh pr create --base integration --title "L3-P1-20: SIG-13 emission on a failed run" --body "Lane 3 task L3-P1-20."
```

**Acceptance** — all true:
1. A `FAILED` run emits exactly one SIG-13 for the failure itself.
2. An overdue `RED` finding emits a SIG-13 carrying its age in the evidence.
3. No notification, webhook or message is sent from this lane.

**SELF-VERIFY**

```bash
python -m pytest reconciler/tests/test_signals.py -q && grep -rcE "requests\.|urllib|smtplib|webhook" reconciler/signals.py
```

Expected output, exactly:

```
4 passed
0
```

**STOP** — if delivering the signal appears to require a notification call, stop: `notify/**` is Lane 5's exclusive path. File the blocker requesting a contract-mediated handoff.

---

## 5. Phase 2 — Orphan detection at blocking severity

§98.2 Phase 3 ships *"orphan detection at blocking severity"* alongside the detect-only reconciler. The catalogue is the sixteen-row table in §12.2; transcribe it, do not summarise it.

> **DECISION REQUIRED — L3-D4: drift class for orphan severities `High` and `Medium`**
> **Question.** §12.2 grades the sixteen orphan types `Blocking`, `High` and `Medium`. §53.4 states there is exactly one drift severity scale — Green / Amber / Red / Blocking — and retires older vocabulary *"exactly once, here"*, a paragraph that does not cover `High` or `Medium`. §52.2 fixes SIG-05 (orphan risk) at `Blocking`. The mapping for `High` and `Medium` is therefore undefined and must not be guessed.
> **Why L0.** §53.4: *"Class assignment lives in configuration and is reviewable; it is not decided ad hoc."*
> **Interim behaviour, binding until L0 answers:** every orphan finding carries `orphan_severity` transcribed verbatim from §12.2. Findings whose `orphan_severity` is `Blocking` also carry `drift_class=BLOCKING`. Findings graded `High` or `Medium` carry `drift_class=None`, are reported, and are **excluded from every drift-budget count** until L0 answers — the D77 arming discipline applied to a class with no declared home.
> **Blocks:** nothing. Every count in Phase 2 below holds either way.

---

### L3-P2-01 — Orphan framework and the sixteen-type severity map

**Phase** 2 · **Size** M · **Deps** L3-P1-01 · **Spec** §12.2 (the sixteen-row orphan table); §52.2 SIG-05; §101 invariant 57

**Files (create):** `reconciler/orphans/__init__.py`, `reconciler/orphans/types.py`, `reconciler/tests/test_orphan_types.py`

Write `types.py` containing `ORPHAN_TYPES`: an ordered list of exactly sixteen entries, each a frozen dataclass with `index` (1–16), `name`, `detection_source` and `orphan_severity`, transcribed **verbatim** from the §12.2 table in the order printed there:

| # | name | detection_source | orphan_severity |
| --- | --- | --- | --- |
| 1 | Product with no Primary Owner | Assignment registry | Blocking |
| 2 | Product with no Cross-Reviewer | Assignment registry | Blocking |
| 3 | Product with no Backup Owner | Assignment registry | High |
| 4 | Product with no Primary Responder | Contract operations block | Blocking |
| 5 | Shared service with no owner | Service registry | Blocking |
| 6 | Certificate with no owner | Asset inventory | High |
| 7 | Domain with no owner | Asset inventory | Blocking |
| 8 | Vendor relationship with no owner | Asset inventory | Medium |
| 9 | Operational asset with no owner | Asset inventory | Medium |
| 10 | Customer commitment with no owner | Contract operations block | Blocking |
| 11 | Platform migration with no owner | Compatibility state | High |
| 12 | Verification responsibility unassigned | Assignment registry | High |
| 13 | In-flight H1 work with no assignee | Board | High |
| 14 | Temporary person expired with open gate-relevant work | Assignment registry + open reviews and gate items at expiry | High |
| 15 | Policy with no owner | Policy register | Blocking |
| 16 | Open exception whose requester or authority has departed | Exception registry | High |

Groups, used by `--group`: `ownership` = 1–5, `assets` = 6–10, `governance` = 11–16.

Tests assert: exactly sixteen entries; the six `Blocking` rows are exactly indices 1, 2, 4, 5, 7, 10, 15 — count them: seven; the three groups partition 1–16 with no overlap and no gap.

**Commands**

```bash
set -euo pipefail
git checkout integration && git pull --ff-only origin integration && git checkout -b lane/3/p2-01-orphan-types
# write the three files
python -m pytest reconciler/tests/test_orphan_types.py -q
git add reconciler/orphans reconciler/tests/test_orphan_types.py
git commit -m "L3-P2-01: orphan framework and sixteen-type severity map"
git fetch origin && git rebase origin/integration && git push -u origin lane/3/p2-01-orphan-types
gh pr create --base integration --title "L3-P2-01: orphan framework and severity map" --body "Lane 3 task L3-P2-01."
```

**Acceptance** — all true:
1. `len(ORPHAN_TYPES) == 16`.
2. Exactly seven entries carry `orphan_severity == "Blocking"` (indices 1, 2, 4, 5, 7, 10, 15).
3. Names are transcribed verbatim; no row is reworded, merged or renumbered.

**SELF-VERIFY**

```bash
python -m pytest reconciler/tests/test_orphan_types.py -q && python -c "
from reconciler.orphans.types import ORPHAN_TYPES
print('types', len(ORPHAN_TYPES), 'blocking', sum(1 for t in ORPHAN_TYPES if t.orphan_severity=='Blocking'))"
```

Expected output, exactly:

```
3 passed
types 16 blocking 7
```

**STOP** — if your count of `Blocking` rows is not 7, re-read §12.2 rather than adjusting the code. If §12.2 genuinely disagrees with the seven indices above, file the blocker quoting the table.

---

### L3-P2-02 — Orphan detectors 1–5 (ownership slots and shared services)

**Phase** 2 · **Size** M · **Deps** L3-P2-01 · **Spec** §12.2 rows 1–5; §52.2 SIG-05; §101 invariant 7

**Files (create):** `reconciler/orphans/ownership.py`, `reconciler/tests/test_orphan_ownership.py`

Rule, exactly: a slot is orphaned when it is empty **or** held by a person whose `availability` is `departed` or whose `access_status` is `revoked`. `availability: departing` is **not** yet an orphan — it is the trigger for prospective mode (L3-P2-05). `compared` = number of products plus number of shared services.

<!-- BLOCKED pending DR-L3-05-A through E Founder decisions: fixture-a people.yaml (File 1) is a CONTESTED(DR-L3-05-A) placeholder. Counts below assume the placeholder values and will change when DR-L3-05-A is resolved. -->

**Acceptance** — all true:
1. On `fixture-a`, exactly four findings: `beta` no Cross-Reviewer (type 2), `beta` no Backup Owner (type 3), `beta` no Primary Responder (type 4), `auth-service` no owner (type 5).
2. `alpha` produces no ownership orphan, and `beta`'s Primary Owner (`dev-1`) produces none.
3. `compared` equals 3.

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p2-02-orphan-ownership

# Write reconciler/orphans/ownership.py (detectors for types 1-5: empty or departed/revoked slots)
# Write reconciler/tests/test_orphan_ownership.py

git add reconciler/orphans/ownership.py reconciler/tests/test_orphan_ownership.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P2-02: orphan detectors 1-5 for ownership slots and shared services"
git push -u origin lane/3/p2-02-orphan-ownership
gh pr create --title "L3-P2-02: orphan detectors 1-5 for ownership slots and shared services" --base integration --body "Closes L3-P2-02"
```

**SELF-VERIFY**

```bash
python -m reconciler.cli orphans --fixture fixture-a --group ownership --summary; echo "exit=$?"
```

Expected output, exactly:

```
OK orphans.ownership findings=4 compared=3
exit=2
```

**STOP** — if `qa-1` (availability `departing`) is treated as inactive here, the prospective/current distinction of §12.2 is collapsed. Fix the predicate; do not change the fixture.

---

### L3-P2-03 — Orphan detectors 6–10 (assets and customer commitments)

**Phase** 2 · **Size** M · **Deps** L3-P2-01 · **Spec** §12.2 rows 6–10; §49.1 (*"Asset owners participate in orphan detection"*); §21.1

**Files (create):** `reconciler/orphans/assets.py`, `reconciler/tests/test_orphan_assets.py`

Rule, exactly: an asset row (`certificate`, `domain`, `vendor`, `operational`) with an empty `owner`, or an owner who is `departed`/`revoked`, is an orphan of the matching type. A `commitments` entry with an empty `owner` is type 10. `compared` = number of asset rows plus number of commitment rows.

<!-- BLOCKED pending DR-L3-05-A through E Founder decisions: fixture-a assets.yaml (File 6) is a CONTESTED(DR-L3-05-A) placeholder and alpha.yaml COM-alpha-001 (File 2) is a CONTESTED(DR-L3-05-E) placeholder. Finding counts and field names below assume the placeholder values and will change when DR-L3-05-A and DR-L3-05-E are resolved. -->

**Acceptance** — all true:
1. On `fixture-a`, exactly three findings: `domain-1` (type 7, Blocking), `vendor-1` (type 8, Medium), `COM-alpha-001` (type 10, Blocking).
2. `cert-1` produces **no** finding: its owner `qa-1` is `departing`, which is still active.
3. `compared` equals 5.

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p2-03-orphan-assets

# Write reconciler/orphans/assets.py (detectors for types 6-10: asset and commitment owners)
# Write reconciler/tests/test_orphan_assets.py

git add reconciler/orphans/assets.py reconciler/tests/test_orphan_assets.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P2-03: orphan detectors 6-10 for assets and customer commitments"
git push -u origin lane/3/p2-03-orphan-assets
gh pr create --title "L3-P2-03: orphan detectors 6-10 for assets and customer commitments" --base integration --body "Closes L3-P2-03"
```

**SELF-VERIFY**

```bash
python -m reconciler.cli orphans --fixture fixture-a --group assets --summary; echo "exit=$?"
```

Expected output, exactly:

```
OK orphans.assets findings=3 compared=5
exit=2
```

**STOP** — none beyond the standing rule.

---

### L3-P2-04 — Orphan detectors 11–16 (migration, verification, H1, temporary expiry, policy, exception)

**Phase** 2 · **Size** M · **Deps** L3-P2-01 · **Spec** §12.2 rows 11–16; §12.2 (*"Temporary-person expiry is an exit"*); §54; §55

**Files (create):** `reconciler/orphans/governance.py`, `reconciler/tests/test_orphan_governance.py`

Rule, exactly, one detector per type: migration with empty `owner`; product with empty `verification_responsibility`; board item at `horizon: H1` with empty `assignee`; an expired temporary assignment whose holder still appears in `open_gate_items` (type 14 — §12.2 names this *"the fourteenth orphan type"*); policy with empty `owner`; open exception whose `requester` or `authority` is `departed`. `compared` = 6, one per type examined.

<!-- BLOCKED pending DR-L3-05-A through E Founder decisions: fixture-a board.yaml (File 10) is CONTESTED(DR-L3-05-C) and CONTESTED(DR-L3-05-D) placeholders. WI-101 (H1 assignee, type 13) and REV-9 (open gate item, type 14) reference pre-decided fields that are pending DR-L3-05-C and DR-L3-05-D Founder decisions. Finding counts below will change when those decisions are resolved. -->

**Acceptance** — all true:
1. On `fixture-a` with `--as-of 2026-08-27`, exactly five findings: `beta` verification unassigned (12), `WI-101` H1 unassigned (13), `dev-1` expired temporary holding open `REV-9` (14), `POL-001` no owner (15), `EXC-001` requester `dev-2` departed (16).
2. `MIG-1` produces no finding — it has owner `lead-1` (type 11 clean).
3. `compared` equals 6.

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p2-04-orphan-governance

# Write reconciler/orphans/governance.py (detectors for types 11-16: migration, verification, H1, expiry, policy, exception)
# Write reconciler/tests/test_orphan_governance.py

git add reconciler/orphans/governance.py reconciler/tests/test_orphan_governance.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P2-04: orphan detectors 11-16 for migration, verification, H1, expiry, policy, exception"
git push -u origin lane/3/p2-04-orphan-governance
gh pr create --title "L3-P2-04: orphan detectors 11-16 for migration, verification, H1, expiry, policy, exception" --base integration --body "Closes L3-P2-04"
```

**SELF-VERIFY**

```bash
python -m reconciler.cli orphans --fixture fixture-a --group governance --as-of 2026-08-27 --summary; echo "exit=$?"
```

Expected output, exactly:

```
OK orphans.governance findings=5 compared=6
exit=2
```

**STOP** — none beyond the standing rule.

---

### L3-P2-05 — Prospective orphan mode on `availability: departing`

**Phase** 2 · **Size** M · **Deps** L3-P2-02, L3-P2-03, L3-P2-04 · **Spec** §12.2 (*"Orphan detection runs immediately when `availability` becomes `departing`, in prospective mode against the declared `end_date`: it emits the transfer worklist"*); AT-017

**Files (create):** `reconciler/orphans/prospective.py`, `reconciler/tests/test_orphan_prospective.py`

Rule, exactly: for each person whose `availability` is `departing`, re-run every detector with that person treated as inactive **as of their `end_date`**, and emit the resulting findings as a **transfer worklist**, each carrying `prospective=True` and `orphans_on=<end_date>`. Prospective findings never enter drift-budget counts and never block; they are a generated worklist for the knowledge-transfer window. `compared` = number of people rows examined.

**Acceptance** — all true:
1. On `fixture-a` with `--prospective --as-of 2026-08-27`, exactly two findings, both `prospective=True` and both `orphans_on=2026-09-30`: `alpha` verification responsibility (type 12) and `cert-1` (type 6), both held by `qa-1`.
2. No prospective finding sets exit code `2` — the run's exit code is `0` when only prospective findings exist.
3. `compared` equals 5.

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p2-05-orphan-prospective

# Write reconciler/orphans/prospective.py (re-run detectors with departing person treated as inactive at end_date)
# Write reconciler/tests/test_orphan_prospective.py

git add reconciler/orphans/prospective.py reconciler/tests/test_orphan_prospective.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P2-05: prospective orphan mode on availability: departing"
git push -u origin lane/3/p2-05-orphan-prospective
gh pr create --title "L3-P2-05: prospective orphan mode on availability: departing" --base integration --body "Closes L3-P2-05"
```

**SELF-VERIFY**

```bash
python -m reconciler.cli orphans --fixture fixture-a --prospective --as-of 2026-08-27 --summary; echo "exit=$?"
```

Expected output, exactly:

```
OK orphans.prospective findings=2 compared=5
exit=0
```

**STOP** — if prospective findings block the deployment path, stop: they describe a future state and blocking on them would freeze the estate for every notice period. File the blocker.

---

### L3-P2-06 — Blocking orphans are non-dismissible; SIG-05 emission

**Phase** 2 · **Size** S · **Deps** L3-P2-05 · **Spec** §12.2 (*"Blocking orphans … cannot be dismissed without resolution"*); §101 invariant 57; §52.2 SIG-05 (Blocking, owner Team Lead)

**Files (create):** `reconciler/orphans/dismissal.py`, `reconciler/tests/test_orphan_dismissal.py`

Implement `dismiss(finding, actor, reason)` which **raises** `NonDismissibleOrphan` for any finding whose `orphan_severity` is `Blocking`, regardless of actor or reason, and permits dismissal only with a linked resolution reference for other severities. Extend `emit_signals()` to raise SIG-05 with `drift_class="Blocking"` and `owner="team_lead"` when any product's Primary Owner, Cross-Reviewer or named responder slot is orphaned — transcribed from the §52.2 SIG-05 row and its disjointness note (*"Orphan risk (SIG-05) is a product-structure condition"*).

**Acceptance** — all true:
1. `dismiss()` raises on every `Blocking` orphan, including when the actor holds `platform-admin`.
2. SIG-05 fires for `beta` on `fixture-a` and does not fire for `alpha`.
3. SIG-05 is not conflated with SIG-26 or SIG-27 — a test asserts only SIG-05 is emitted for a product-structure orphan (§52.2 disjoint definitions).

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p2-06-orphan-dismissal

# Write reconciler/orphans/dismissal.py (NonDismissibleOrphan for Blocking severity; SIG-05 emission)
# Write reconciler/tests/test_orphan_dismissal.py

git add reconciler/orphans/dismissal.py reconciler/tests/test_orphan_dismissal.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P2-06: blocking orphans non-dismissible and SIG-05 emission"
git push -u origin lane/3/p2-06-orphan-dismissal
gh pr create --title "L3-P2-06: blocking orphans non-dismissible and SIG-05 emission" --base integration --body "Closes L3-P2-06"
```

**SELF-VERIFY**

```bash
python -m pytest reconciler/tests/test_orphan_dismissal.py -q
```

Expected output, exactly:

```
5 passed
```

**STOP** — if a stakeholder asks for a dismissal override path for Blocking orphans, stop: invariant 57 forbids it. File the blocker addressed to L0.

---

## 6. Phase 3 — The Level 4 block surface

This phase turns findings into the one thing that stops work: the `control-plane/blocking-drift` required status check named in §11.3.

---

### L3-P3-01 — Drift-class configuration loader from `os-health.yaml`

**Phase** 3 · **Size** M · **Deps** L3-P1-19 · **Spec** §53.4 (*"Class assignment lives in configuration and is reviewable"*); §52.2; §53.6

**Files (create):** `reconciler/driftclass.py`, `reconciler/tests/test_driftclass.py`

Implement `load_classes(os_health_path) -> dict[str, DriftClass]` mapping comparator id → configured class, with the code's own default used only where the file declares none, and `security_floor()` applied last so that *"Security drift and production environment drift are never classified below Red"* (§53.4) cannot be configured away. `os-health.yaml` lives in `registries/**` and is owned by Lane 1: **read it, never write it.**

**Acceptance** — all true:
1. A configured class overrides the code default for a non-security comparator.
2. A configuration attempting to set a security or production-environment comparator below `RED` is refused, and the refusal is itself a finding.
3. No write occurs to `registries/**` or any file outside the three owned roots.

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p3-01-driftclass

# Write reconciler/driftclass.py (load_classes from os-health.yaml; security_floor enforcement)
# Write reconciler/tests/test_driftclass.py

git add reconciler/driftclass.py reconciler/tests/test_driftclass.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P3-01: drift-class configuration loader from os-health.yaml"
git push -u origin lane/3/p3-01-driftclass
gh pr create --title "L3-P3-01: drift-class configuration loader from os-health.yaml" --base integration --body "Closes L3-P3-01"
```

**SELF-VERIFY**

```bash
python -m pytest reconciler/tests/test_driftclass.py -q && bash reconciler/scripts/check-ownership.sh
```

Expected output, exactly:

```
5 passed
OWNERSHIP OK
```

**STOP** — if a needed field is absent from `os-health.yaml`, do not add it: that file is Lane 1's. File a Contract Change Request blocker (`PARTITION.md` rule 2).

---

### L3-P3-02 — `control-plane/blocking-drift` check-run publisher

**Phase** 3 · **Size** M · **Deps** L3-P3-01 · **Spec** §11.3 (the required status check *"the reconciler holds at failure while Blocking-class drift is open against the product"*); §40.1 (*"the reconciler credential additionally holds check-run write on product repositories, used for exactly one named check"*); §53.2 Level 4

**Files (create):** `reconciler/checkrun.py`, `reconciler/tests/test_checkrun.py`

Implement `publish(repo, findings, dry_run=True)` producing a check run named **exactly** `control-plane/blocking-drift` with conclusion `failure` while any Blocking-class finding is open against that product, and `success` otherwise. Constraints, enforced in code and by test:

* The publisher may emit **only** that one check name. Any other name raises.
* A check run carries status only: it writes no repository content, approves nothing, and satisfies no gate a human is required to satisfy (§40.1).
* `dry_run=True` is the default; the live path is reached only with an explicit flag.

**Acceptance** — all true:
1. Publishing under any name other than `control-plane/blocking-drift` raises.
2. With one Blocking finding against `beta`, the conclusion is `failure`; with none, `success`.
3. The module contains no call that writes repository content, secrets, environments or workflow files (safety rule 4).

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p3-02-checkrun

# Write reconciler/checkrun.py (publish() for control-plane/blocking-drift; dry_run=True default)
# Write reconciler/tests/test_checkrun.py

git add reconciler/checkrun.py reconciler/tests/test_checkrun.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P3-02: control-plane/blocking-drift check-run publisher"
git push -u origin lane/3/p3-02-checkrun
gh pr create --title "L3-P3-02: control-plane/blocking-drift check-run publisher" --base integration --body "Closes L3-P3-02"
```

**SELF-VERIFY**

```bash
python -m pytest reconciler/tests/test_checkrun.py -q && grep -rniE "put_contents|create_file|update_file|secrets|environments/|workflows/" reconciler/checkrun.py | wc -l
```

Expected output, exactly:

```
6 passed
0
```

**STOP** — if a second check name seems useful, stop: §40.1 authorises *"exactly one named check"*. File the blocker.

---

### L3-P3-03 — Check-run identity assertion

**Phase** 3 · **Size** S · **Deps** L3-P3-02 · **Spec** §40.1 (*"A check run published under that name by any identity other than the reconciler is Blocking drift"*)

**Files (create):** `reconciler/comparators/checkrun_identity.py`, `reconciler/tests/test_checkrun_identity.py`

Rule, exactly: for each repository, read `check_runs(repo)`; if `control-plane/blocking-drift` exists and `published_by` is not the declared reconciler identity, emit `BLOCKING`, `Level.BLOCK`. `compared` = number of repositories.

**Acceptance** — all true:
1. On `fixture-a`, exactly one finding: `alpha`'s check published by `other-bot`.
2. `beta`'s check, published by `reconciler`, produces no finding.
3. `compared` equals 2.

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p3-03-checkrun-identity

# Write reconciler/comparators/checkrun_identity.py (detect non-reconciler publisher of control-plane/blocking-drift)
# Write reconciler/tests/test_checkrun_identity.py

git add reconciler/comparators/checkrun_identity.py reconciler/tests/test_checkrun_identity.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P3-03: check-run identity assertion"
git push -u origin lane/3/p3-03-checkrun-identity
gh pr create --title "L3-P3-03: check-run identity assertion" --base integration --body "Closes L3-P3-03"
```

**SELF-VERIFY**

```bash
python -m reconciler.cli run --fixture fixture-a --only checkrun_identity --summary; echo "exit=$?"
```

Expected output, exactly:

```
OK checkrun_identity findings=1 compared=2
CANARY n/a
exit=2
```

**STOP** — none beyond the standing rule.

---

### L3-P3-04 — Drift budget counters

**Phase** 3 · **Size** M · **Deps** L3-P3-01 · **Spec** §53.4 budget rules (Amber up to 2 per product; Red flat 3 portfolio-wide; Green unlimited; Blocking has no budget)

**Files (create):** `reconciler/budget.py`, `reconciler/tests/test_budget.py`

Implement `evaluate(findings, product_count, config)` returning per-class open counts, ceilings and breach flags. Rules, transcribed:

* **Amber ceiling = `amber_per_product` × product_count.** It scales with the portfolio *"because Amber is routine remediation debt and a fixed ceiling would tighten silently as products are added"*.
* **Red ceiling = `red_portfolio_flat`, and does not scale**, *"because Red is the volume of material unremediated risk the team can actually hold in attention at once; that number is a property of the team, not of the portfolio."*
* **Green unlimited. Blocking has no budget.**
* Exceeding the Amber tolerance emits an Amber signal **about the operating system**, not about any product (§53.4).
* Canary findings and prospective orphan findings are excluded from all counts.

**Acceptance** — all true:
1. With `amber_per_product: 2` and 2 products, the Amber ceiling computes as 4; with 8 products, 16; with 20 products, 40 (the three figures §53.4 states).
2. The Red ceiling stays 3 at every product count.
3. An Amber breach is attributed to the operating system, not to a product.

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p3-04-drift-budget

# Write reconciler/budget.py (evaluate() with Amber/Red/Green/Blocking ceiling rules)
# Write reconciler/tests/test_budget.py

git add reconciler/budget.py reconciler/tests/test_budget.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P3-04: drift budget counters"
git push -u origin lane/3/p3-04-drift-budget
gh pr create --title "L3-P3-04: drift budget counters" --base integration --body "Closes L3-P3-04"
```

**SELF-VERIFY**

```bash
python -m pytest reconciler/tests/test_budget.py -q && python -c "
from reconciler.budget import ceilings
print(ceilings(2)['amber'], ceilings(8)['amber'], ceilings(20)['amber'], ceilings(20)['red'])"
```

Expected output, exactly:

```
7 passed
4 16 40 3
```

**STOP** — if the Red ceiling is made to scale with product count, stop: §53.4 makes the non-scaling deliberate (*"A growing portfolio therefore makes the Red budget bind harder, and that is the intended pressure"*).

---

### L3-P3-05 — Reclassification gate

**Phase** 3 · **Size** S · **Deps** L3-P3-01 · **Spec** §53.5 (*"Reclassifying a finding downward requires the same authority as approving an exception for it, and is recorded as a decision. There is no informal path from Red to Amber."*)

**Files (create):** `reconciler/reclassify.py`, `reconciler/tests/test_reclassify.py`

Implement `reclassify(finding, to_class, actor, decision_record_id)`. Downward reclassification (`BLOCKING`→lower, `RED`→lower, `AMBER`→`GREEN`) **raises** unless a non-empty `decision_record_id` is supplied and the actor holds exception-approval authority per the §54.3 authority mapping. Upward reclassification is always permitted and recorded. Every reclassification writes an audit entry; none is silent.

**Acceptance** — all true:
1. Downward reclassification without a decision-record id raises.
2. Downward reclassification by an actor lacking exception authority raises even with an id.
3. Upward reclassification succeeds and is recorded.

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p3-05-reclassify

# Write reconciler/reclassify.py (reclassify() gated on decision_record_id and actor authority)
# Write reconciler/tests/test_reclassify.py

git add reconciler/reclassify.py reconciler/tests/test_reclassify.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P3-05: reclassification gate"
git push -u origin lane/3/p3-05-reclassify
gh pr create --title "L3-P3-05: reclassification gate" --base integration --body "Closes L3-P3-05"
```

**SELF-VERIFY**

```bash
python -m pytest reconciler/tests/test_reclassify.py -q
```

Expected output, exactly:

```
5 passed
```

**STOP** — none beyond the standing rule.

---

### L3-P3-06 — Closure-quality audit sampler

**Phase** 3 · **Size** M · **Deps** L3-P3-04 · **Spec** §53.6 (*"a finding closed without evidence of remediation, or a finding that recurs in the same scope shortly after closure, is reopened and counted as a closure-quality defect, not as new drift"*)

**Files (create):** `reconciler/closure_audit.py`, `reconciler/tests/test_closure_audit.py`

Implement `audit(closed_findings, open_findings, recurrence_window_days)` returning: closures with no linked remediation evidence, and findings recurring in the same `scope` inside the recurrence window. Both are **reopened** and tagged `closure_quality_defect=True` so they are not double-counted as new drift.

**Acceptance** — all true:
1. A closure with no evidence link is reopened and tagged.
2. A same-scope recurrence inside the window is reopened and tagged, and does not increment the new-drift count.
3. `recurrence_window_days` is configuration, not a literal in the algorithm (§53.6: tolerances are calibration-reviewed).

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p3-06-closure-audit

# Write reconciler/closure_audit.py (audit() for evidence-less closures and same-scope recurrences)
# Write reconciler/tests/test_closure_audit.py

git add reconciler/closure_audit.py reconciler/tests/test_closure_audit.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P3-06: closure-quality audit sampler"
git push -u origin lane/3/p3-06-closure-audit
gh pr create --title "L3-P3-06: closure-quality audit sampler" --base integration --body "Closes L3-P3-06"
```

**SELF-VERIFY**

```bash
python -m pytest reconciler/tests/test_closure_audit.py -q
```

Expected output, exactly:

```
6 passed
```

**STOP** — none beyond the standing rule.

---

## 7. Phase 4 — Provisioning and scaffolding v0

§98.2 Phase 3 ships *"Scaffolding v0 — `create-product` and `add-person`, generating repository, Teams, CODEOWNERS, branch protection and registry entries with zero hand-editing"*. §12.6: *"No ordinary personnel or product change should require hand-editing files across twenty repositories. If it does, the scaffolding is incomplete and that is a platform defect."*

**Dry-run summary format, used by every operation in this phase:**

```
PLAN <operation> steps=<int> writes=<int> manual=<int>
```

`writes` is the count of mutations actually performed; in `--dry-run` it is always `0`. `manual` is the count of manual-step issues the operation would emit (§19.1: *"where the provider offers no automation, tracked manual steps emitted as issues so neither is silently missing"*).

---

### L3-P4-01 — `provision` CLI skeleton, dry-run by default

**Phase** 4 · **Size** M · **Deps** L3-P0-06 · **Spec** §12.6; §64.1 (*"a configuration error must never grant excess authority"*); §101 invariant 79

**Files (create):** `tools/provision/cli.py`, `tools/provision/plan.py`, `tools/provision/tests/test_cli.py`

`plan.py`: a `Step` dataclass (`id`, `description`, `kind` ∈ {`write`, `manual`, `read`}) and a `Plan` holding an ordered list of steps with `summary_line(operation)` rendering the format above. `cli.py`: subcommands `create-product`, `add-person`, `change-role`, `remove-person`, each requiring `--fixture` or `--live`, with `--dry-run` **on by default**; performing real writes requires the explicit flag `--apply`.

**Acceptance** — all true:
1. Omitting `--apply` performs zero writes, for every subcommand.
2. `--apply` without `--live` is refused (you cannot mutate a fixture).
3. Safe defaults are the default: nothing this CLI creates is public, pre-approved, or granted an environment (§64.1).

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p4-01-provision-cli

# Create tools/provision/cli.py, plan.py, tests/test_cli.py

git add tools/provision/cli.py tools/provision/plan.py tools/provision/tests/test_cli.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P4-01: provision CLI skeleton, dry-run by default"
git push -u origin lane/3/p4-01-provision-cli
gh pr create --title "L3-P4-01: provision CLI skeleton, dry-run by default" --base integration --body "Closes L3-P4-01"
```

**SELF-VERIFY**

```bash
python -m tools.provision.cli --help | grep -c -- "--apply" && python -m tools.provision.cli create-product --fixture fixture-a --product gamma 2>&1 | grep -c "dry-run"
```

Expected output, exactly:

```
1
1
```

**STOP** — if `--apply` is ever made the default for convenience, stop: safe defaults are P0 (§64.1) and this CLI holds the provisioning credential.

---

### L3-P4-02 — CODEOWNERS generator, human identities only

**Phase** 4 · **Size** M · **Deps** L3-P4-01 · **Spec** §11.3 (*"CODEOWNERS is generated to contain human identities only — no machine account ever appears in it"*); §37.3; §98.2 Phase 1 completion check

**Files (create):** `tools/provision/codeowners.py`, `tools/provision/tests/test_codeowners.py`

Implement `generate(product, registries) -> str` producing, in this order and no other: product source paths owned by the product Team; `verification/` owned by the holder of `verification_responsibility`; `product.yaml`, migration directories and CI workflow files owned by the Team Lead role (all four rules transcribed from §11.3). The generator **filters every candidate against `people.yaml`** and raises `MachineIdentityInCodeowners` if any output line names a login absent from `people.yaml` or matching a machine-identity pattern.

**Acceptance** — all true:
1. Generated output for `alpha` contains no `@ci-bot` and no `[bot]` suffix.
2. Injecting a machine login into the assignment input raises, rather than emitting it.
3. The four ownership rules of §11.3 each appear in the output, in the order listed.

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p4-02-codeowners-generator

# Create tools/provision/codeowners.py, tests/test_codeowners.py

git add tools/provision/codeowners.py tools/provision/tests/test_codeowners.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P4-02: CODEOWNERS generator, human identities only"
git push -u origin lane/3/p4-02-codeowners-generator
gh pr create --title "L3-P4-02: CODEOWNERS generator, human identities only" --base integration --body "Closes L3-P4-02"
```

**SELF-VERIFY**

```bash
python -m pytest tools/provision/tests/test_codeowners.py -q && python -c "
from tools.provision.codeowners import generate
out = generate('alpha', 'fixture-a')
print('botlines', sum(1 for l in out.splitlines() if 'bot' in l))"
```

Expected output, exactly:

```
6 passed
botlines 0
```

**STOP** — if a machine identity must appear in CODEOWNERS for any workflow to function, stop: that would let a machine approval satisfy a gate (§11.3, §37.3, D53). File the blocker.

---

### L3-P4-03 — Branch-protection applier from template

**Phase** 4 · **Size** M · **Deps** L3-P4-01 · **Spec** §11.3 (the ten-bullet checklist); §98.2 Phase 1 (*"The required-status-check list starts empty per repository"*); §64.1

**Files (create):** `tools/provision/protection.py`, `tools/provision/tests/test_protection.py`

Implement `plan_protection(repo, template)` emitting one step per §11.3 bullet: require a pull request; require at least 1 approving review; require review from Code Owners; require approval of the most recent reviewable push; dismiss stale approvals; require status checks to pass; require branches up to date; block force pushes and deletions on the default branch; apply rules to administrators; and apply the environment deployment branch and tag policy. **The `contexts` list is applied empty at creation** and populated only as each check comes into existence — §98.2 Phase 1: *"A required check no workflow emits blocks every pull request indefinitely; a list that silently stays empty is a gate that reads armed and is not."* Emit a `manual` step recording which contexts the repository still owes.

**Acceptance** — all true:
1. All ten §11.3 bullets appear as steps, in the order printed there.
2. At creation, `required_status_checks.contexts` is empty and a manual step records the owed contexts.
3. No step ever removes or weakens an existing protection setting (safety rule 2).

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p4-03-branch-protection

# Create tools/provision/protection.py, tests/test_protection.py

git add tools/provision/protection.py tools/provision/tests/test_protection.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P4-03: branch-protection applier from template"
git push -u origin lane/3/p4-03-branch-protection
gh pr create --title "L3-P4-03: branch-protection applier from template" --base integration --body "Closes L3-P4-03"
```

**SELF-VERIFY**

```bash
python -m pytest tools/provision/tests/test_protection.py -q && python -c "
from tools.provision.protection import plan_protection
p = plan_protection('gamma','fixture-a')
print('steps', len(p.steps), 'contexts', p.contexts)"
```

Expected output, exactly:

```
7 passed
steps 10 contexts []
```

**STOP** — if a caller asks for the contexts list to be pre-populated at creation, stop and file the blocker quoting §98.2 Phase 1.

---

### L3-P4-04 — Environments and deployment branch/tag policy applier

**Phase** 4 · **Size** M · **Deps** L3-P4-01 · **Spec** §33.4; §19.1; §64.1 (*"production environment created without secrets and without approvers until explicitly configured"*)

**Files (create):** `tools/provision/environments.py`, `tools/provision/tests/test_environments.py`

Implement `plan_environments(repo, template)` creating `development`, `staging` and `production`, applying to `staging` and `production` a deployment branch and tag policy accepting the default branch and protected release tags **and no other ref** (§33.4). The plan **never** creates a secret and never sets an approver — §64.1.

**Acceptance** — all true:
1. Three environments are planned; `staging` and `production` each carry the branch/tag policy.
2. Zero steps of kind `write` touch a secret (safety rule 2 and AT-110 negative attempt 1).
3. A test asserts a plan containing a secret step raises.

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p4-04-environments

# Create tools/provision/environments.py, tests/test_environments.py

git add tools/provision/environments.py tools/provision/tests/test_environments.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P4-04: environments and deployment branch/tag policy applier"
git push -u origin lane/3/p4-04-environments
gh pr create --title "L3-P4-04: environments and deployment branch/tag policy applier" --base integration --body "Closes L3-P4-04"
```

**SELF-VERIFY**

```bash
python -m pytest tools/provision/tests/test_environments.py -q && grep -rniE "secret|token|password" tools/provision/environments.py | grep -vc "never\|raise\|assert\|#"
```

Expected output, exactly:

```
6 passed
0
```

**STOP** — none beyond the standing rule.

---

### L3-P4-05 — Team creator derived from the registries

**Phase** 4 · **Size** M · **Deps** L3-P4-01 · **Spec** §11.2 (*"One Team per product … Two organisation-wide Teams grant Write to the Team Lead role and the QA role. Team membership is derived from the registries"*); §98.2 Phase 1

**Files (create):** `tools/provision/teams.py`, `tools/provision/tests/test_teams.py`

Implement `plan_teams(registries)` producing: one Team per product named for the product, containing every holder of a current assignment on it; plus exactly two organisation-wide Teams, one for the Team Lead role and one for the QA role. Membership is **derived**, never passed in by the caller; a caller-supplied member list raises.

**Acceptance** — all true:
1. On `fixture-a`, two product Teams (`alpha`, `beta`) and two org-wide Teams are planned.
2. `alpha`'s planned membership is exactly the four current assignment holders — `dev-2` is absent, because it holds no assignment.
3. A caller-supplied membership list raises.

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p4-05-teams

# Create tools/provision/teams.py, tests/test_teams.py

git add tools/provision/teams.py tools/provision/tests/test_teams.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P4-05: team creator derived from the registries"
git push -u origin lane/3/p4-05-teams
gh pr create --title "L3-P4-05: team creator derived from the registries" --base integration --body "Closes L3-P4-05"
```

**SELF-VERIFY**

```bash
python -m pytest tools/provision/tests/test_teams.py -q && python -c "
from tools.provision.teams import plan_teams
t = plan_teams('fixture-a')
print('teams', len(t), 'alpha', len(t['alpha']))"
```

Expected output, exactly:

```
6 passed
teams 4 alpha 4
```

**STOP** — none beyond the standing rule.

---

### L3-P4-06 — Repo-from-template and required-file assertion

**Phase** 4 · **Size** M · **Deps** L3-P4-01 · **Spec** §33.1 (the eight commands and the required-file list); §11.3 (*"New repositories are created private"*); §64.1

**Files (create):** `tools/provision/repo.py`, `tools/provision/tests/test_repo.py`

Implement `plan_repo(product)` creating the repository **private**, from `product-template`, with no environment access and no third-party app access (§11.3, §64.1), then asserting the presence of every required file of §33.1: `.env.example`, `docker-compose.dev.yml`, `Makefile`, seed data, migration directory, `verification/`, `AGENTS.md`, and either `product.yaml` or a pointer to the product it belongs to — eight items — plus the eight local-environment-contract commands (`setup`, `dev`, `test`, `uat-local`, `migrate`, `reset`, `health`, `parity`). A missing item is a hard failure of the plan, not a warning (§33.1: *"Required-file presence is checked, not assumed"*).

**Acceptance** — all true:
1. The repository is planned private with no app access and no environment access.
2. All eight required files and all eight commands are asserted.
3. A template missing any one of them fails the plan.

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p4-06-repo

# Create tools/provision/repo.py, tests/test_repo.py

git add tools/provision/repo.py tools/provision/tests/test_repo.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P4-06: repo-from-template and required-file assertion"
git push -u origin lane/3/p4-06-repo
gh pr create --title "L3-P4-06: repo-from-template and required-file assertion" --base integration --body "Closes L3-P4-06"
```

**SELF-VERIFY**

```bash
python -m pytest tools/provision/tests/test_repo.py -q && python -c "
from tools.provision.repo import REQUIRED_FILES, REQUIRED_COMMANDS
print('files', len(REQUIRED_FILES), 'commands', len(REQUIRED_COMMANDS))"
```

Expected output, exactly:

```
6 passed
files 8 commands 8
```

**STOP** — none beyond the standing rule.

---

### L3-P4-07 — `create-product` orchestrator

**Phase** 4 · **Size** L · **Deps** L3-P4-02, L3-P4-03, L3-P4-04, L3-P4-05, L3-P4-06 · **Spec** §19.1 (the CREATE PRODUCT block); §12.6; AT-001

**Files (create):** `tools/provision/create_product.py`, `tools/provision/tests/test_create_product.py`

Compose the plan in **exactly** the §19.1 order, thirteen automated steps:

| # | Step id | §19.1 line |
| --- | --- | --- |
| 1 | `repo_from_template` | repository or repository set from the standard template |
| 2 | `product_yaml` | `product.yaml` at current `contract_version` |
| 3 | `team` | GitHub Team |
| 4 | `codeowners` | CODEOWNERS generated from assignments |
| 5 | `branch_protection` | branch protection from template |
| 6 | `environments` | environments: development, staging, production |
| 7 | `ci_workflows_pinned_tag` | CI workflows consuming reusable workflows by pinned tag |
| 8 | `verification_skeleton` | `verification/` skeleton |
| 9 | `local_environment_contract` | local environment contract — the eight commands |
| 10 | `required_endpoints` | health, version and metrics endpoints |
| 11 | `register_portfolio_board` | registered: portfolio board |
| 12 | `register_grafana_scorecard_devlake` | registered: Grafana · Scorecard · DevLake |
| 13 | `register_dependency_graph` | registered: dependency graph |

Plus **two manual steps**: `alert_channel` and `support_intake_mailbox` — §19.1: *"or, where the provider offers no automation, tracked manual steps emitted as issues so neither is silently missing."*

Steps 11–13 must enumerate from the product registry; a hard-coded product list anywhere in this module fails the task (§101 invariants 52 and 53; AT-001).

**Acceptance** — all true:
1. `PLAN create-product steps=13 writes=0 manual=2` on a dry run.
2. `grep -rn "alpha\|beta" tools/provision/create_product.py` returns nothing — no product name is hard-coded.
3. Every step id above appears exactly once, in the order listed.

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p4-07-create-product

# Create tools/provision/create_product.py, tests/test_create_product.py

git add tools/provision/create_product.py tools/provision/tests/test_create_product.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P4-07: create-product orchestrator"
git push -u origin lane/3/p4-07-create-product
gh pr create --title "L3-P4-07: create-product orchestrator" --base integration --body "Closes L3-P4-07"
```

**SELF-VERIFY**

```bash
python -m tools.provision.cli create-product --fixture fixture-a --product gamma --dry-run --summary; echo "hardcoded=$(grep -rc 'alpha\|beta' tools/provision/create_product.py)"
```

Expected output, exactly:

```
PLAN create-product steps=13 writes=0 manual=2
hardcoded=0
```

**STOP** — if any of steps 11–13 requires editing a dashboard by hand, stop: §19.1 says *"If a human must edit a dashboard to add a product, that is a defect in the operating system, not a task."* File the blocker.

---

### L3-P4-08 — CONFIGURE checklist and manual-step issue emitter

**Phase** 4 · **Size** S · **Deps** L3-P4-07 · **Spec** §19.1 (*"the scaffold emits a CONFIGURE checklist issue enumerating every item below"*)

**Files (create):** `tools/provision/checklists.py`, `tools/provision/tests/test_checklists.py`

Implement `configure_checklist(product)` rendering an issue body enumerating exactly the §19.1 CONFIGURE items: environments · verification contract · observability · backups · classification · budget band · support intake — seven items, with the budget-band line noting it is *"set by the Founder as a provisional estimate, refined at the first cost review"*. Implement `manual_step_issue(step)` rendering one issue per manual step from L3-P4-07.

**Acceptance** — all true:
1. The checklist enumerates exactly seven CONFIGURE items, verbatim.
2. Two manual-step issues are rendered for a `create-product` plan.
3. Nothing is posted to GitHub without `--apply --live`.

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p4-08-checklists

# Create tools/provision/checklists.py, tests/test_checklists.py

git add tools/provision/checklists.py tools/provision/tests/test_checklists.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P4-08: CONFIGURE checklist and manual-step issue emitter"
git push -u origin lane/3/p4-08-checklists
gh pr create --title "L3-P4-08: CONFIGURE checklist and manual-step issue emitter" --base integration --body "Closes L3-P4-08"
```

**SELF-VERIFY**

```bash
python -m pytest tools/provision/tests/test_checklists.py -q && python -c "
from tools.provision.checklists import CONFIGURE_ITEMS
print('configure', len(CONFIGURE_ITEMS))"
```

Expected output, exactly:

```
5 passed
configure 7
```

**STOP** — none beyond the standing rule.

---

### L3-P4-09 — `add-person` orchestrator

**Phase** 4 · **Size** L · **Deps** L3-P4-02, L3-P4-05 · **Spec** §12.6 (`add person`); §12.1; §36.4 (`ai_restrictions`); AT-002

**Files (create):** `tools/provision/add_person.py`, `tools/provision/tests/test_add_person.py`

Compose the plan in **exactly** the §12.6 order, seven automated steps: `people_yaml_entry`, `org_invitation` (base Read only), `team_membership_per_assignments`, `capability_grants` (explicit, never inherited wholesale — §12.1, §64.1), `ai_runtime_assignment` honouring the product's declared `ai_restrictions` (§36.4), `onboarding_checklist_issue`, `register_review_network_view`. Plus **one manual step**: `self_view_key_exchange` — §12.1: *"the encryption key for their self-view document, handed once, in person."*

The onboarding checklist issue must name the external conduct adviser and the fairness rules (§12.1: *"every joiner learns, in writing and on day one, who the conduct adviser is"*) and render the §12.7 milestone bands.

**Acceptance** — all true:
1. `PLAN add-person steps=7 writes=0 manual=1` on a dry run.
2. The invitation step grants base Read only; no step grants Write outside Team membership derived from assignments (§11.2).
3. A product declaring `ai_restrictions` constrains the runtime step at onboarding, not later (§36.4).

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p4-09-add-person

# Create tools/provision/add_person.py, tests/test_add_person.py

git add tools/provision/add_person.py tools/provision/tests/test_add_person.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P4-09: add-person orchestrator"
git push -u origin lane/3/p4-09-add-person
gh pr create --title "L3-P4-09: add-person orchestrator" --base integration --body "Closes L3-P4-09"
```

**SELF-VERIFY**

```bash
python -m tools.provision.cli add-person --fixture fixture-a --login dev-3 --dry-run --summary
```

Expected output, exactly:

```
PLAN add-person steps=7 writes=0 manual=1
```

**STOP** — if the plan needs to grant Write directly rather than through a Team, stop: §11.2 makes Write Teams-derived. File the blocker.

---

### L3-P4-10 — Pre-provisioning (T-minus-one-week) checklist emitter

**Phase** 4 · **Size** S · **Deps** L3-P4-09 · **Spec** §12.1 (*"At one week before the start date the operator works a pre-provisioning checklist"*); §49

**Files (create):** `tools/provision/preprovision.py`, `tools/provision/tests/test_preprovision.py`

Implement `preprovision_checklist(login, start_date)` rendering exactly the six §12.1 items: GitHub account confirmed; hardware ready; email account created; AI-runtime choice asked of the joiner; the runtime seat purchased; an asset-inventory entry recorded for issued hardware. The issue is dated `start_date - 7 days`.

**Acceptance** — all true:
1. Exactly six items, verbatim from §12.1.
2. The due date is exactly seven days before `start_date`.
3. The asset-inventory item names §49 as its destination and is not written by this lane.

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p4-10-preprovision

# Create tools/provision/preprovision.py, tests/test_preprovision.py

git add tools/provision/preprovision.py tools/provision/tests/test_preprovision.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P4-10: pre-provisioning checklist emitter"
git push -u origin lane/3/p4-10-preprovision
gh pr create --title "L3-P4-10: pre-provisioning checklist emitter" --base integration --body "Closes L3-P4-10"
```

**SELF-VERIFY**

```bash
python -m pytest tools/provision/tests/test_preprovision.py -q && python -c "
from tools.provision.preprovision import PREPROVISION_ITEMS
print('items', len(PREPROVISION_ITEMS))"
```

Expected output, exactly:

```
4 passed
items 6
```

**STOP** — none beyond the standing rule.

---

## 8. Phase 5 — The independent control verifier and the credential bound

§53.1: *"Reconciliation regenerates CODEOWNERS and re-applies branch protection, and is also the only thing that checks them — an instrument that can rewrite the wall it inspects and then report the wall intact."* This phase builds the second verifier. It is a **separate program under a separate credential**, and Lane 3 builds the program only: Lane 2 schedules it as a workflow in the control-plane repository (§0.4).

**Verifier summary format:**

```
VERIFY <assertion_id> result=<pass|fail> checked=<int>
VERIFIER result=<pass|fail> assertions=<int>
```

---

### L3-P5-01 — Independent verifier skeleton under a separate credential

**Phase** 5 · **Size** M · **Deps** L3-P4-02 · **Spec** §53.1 (*"A second verifier therefore runs off the operations VM and under a different credential … holding its own read-only fine-grained credential"*); §37.3

**Files (create):** `validators/drift/__init__.py`, `validators/drift/verifier.py`, `validators/drift/tests/test_verifier.py`

Implement an assertion registry (`@assertion("<id>")`) and a `__main__` entry with `--fixture`, `--only`, `--summary`, `--live`. Hard constraints, enforced by test:

* The verifier **imports nothing from `reconciler/**`**. It must not share code with the instrument it audits — a verifier that reuses the reconciler's comparison logic inherits the reconciler's blind spots.
* It reads a credential from a distinct environment variable, `DRIFT_VERIFIER_TOKEN`, and never from the reconciler's variable.
* It performs no write of any kind. §53.1: *"It writes its result to a surface the operations VM cannot write to"* — that surface is Lane 2's workflow output, not this lane's to create.

**Acceptance** — all true:
1. `grep -rn "^from reconciler\|^import reconciler" validators/drift/` returns nothing.
2. The verifier reads only `DRIFT_VERIFIER_TOKEN`.
3. With no assertions registered, `--summary` prints `VERIFIER result=pass assertions=0` and exits 0.

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p5-01-verifier

# Create validators/drift/__init__.py, verifier.py, tests/test_verifier.py

git add validators/drift/__init__.py validators/drift/verifier.py validators/drift/tests/test_verifier.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P5-01: independent verifier skeleton under a separate credential"
git push -u origin lane/3/p5-01-verifier
gh pr create --title "L3-P5-01: independent verifier skeleton under a separate credential" --base integration --body "Closes L3-P5-01"
```

**SELF-VERIFY**

```bash
python -m pytest validators/drift/tests/test_verifier.py -q && grep -rc "import reconciler" validators/drift/ | grep -c ":0" && python -m validators.drift.verifier --fixture fixture-a --summary
```

Expected output, exactly:

```
4 passed
3
VERIFIER result=pass assertions=0
```

**STOP** — if sharing a helper with `reconciler/**` seems tempting to avoid duplication, stop. §53.1: *"no control that can be rewritten by the credential it is checking is a control."* Duplicate the logic deliberately and file no blocker; if you cannot, file one.

---

### L3-P5-02 — Verifier assertion A: no machine identity in any CODEOWNERS

**Phase** 5 · **Size** M · **Deps** L3-P5-01 · **Spec** §53.1 (*"asserting that no machine identity appears in any CODEOWNERS file in any repository"*); §11.3; §37.3

**Files (create):** `validators/drift/assert_codeowners.py`, `validators/drift/tests/test_assert_codeowners.py`

Assertion id `codeowners_human_only`. For every repository, read the actual CODEOWNERS and fail if any owner entry is a machine identity — a login ending `[bot]`, or absent from `people.yaml`. `checked` = number of repositories.

**Acceptance** — all true:
1. On `fixture-a`, `result=fail` because `alpha` names `@ci-bot`.
2. `checked` equals 2.
3. The assertion re-reads CODEOWNERS from the actual state; it never compares against the generator's output (that would be the reconciler checking its own wall).

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p5-02-codeowners-assertion

# Create validators/drift/assert_codeowners.py, tests/test_assert_codeowners.py

git add validators/drift/assert_codeowners.py validators/drift/tests/test_assert_codeowners.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P5-02: verifier assertion A: no machine identity in CODEOWNERS"
git push -u origin lane/3/p5-02-codeowners-assertion
gh pr create --title "L3-P5-02: verifier assertion A: no machine identity in CODEOWNERS" --base integration --body "Closes L3-P5-02"
```

**SELF-VERIFY**

```bash
python -m validators.drift.verifier --fixture fixture-a --only codeowners_human_only --summary; echo "exit=$?"
```

Expected output, exactly:

```
VERIFY codeowners_human_only result=fail checked=2
VERIFIER result=fail assertions=1
exit=2
```

**STOP** — none beyond the standing rule.

---

### L3-P5-03 — Verifier assertion B: branch protection and ruleset JSON match the committed template

**Phase** 5 · **Size** M · **Deps** L3-P5-01 · **Spec** §53.1 (*"that branch protection and ruleset JSON match the committed template"*); §11.3

**Files (create):** `validators/drift/assert_protection.py`, `validators/drift/tests/test_assert_protection.py`

Assertion id `protection_matches_template`. Compare actual protection and ruleset JSON against the **committed** template file, byte-normalised, for every repository. Any difference in either direction fails — this assertion is not the reconciler's stricter-only comparison; it asks only whether the wall matches the committed template. `checked` = number of repositories.

**Acceptance** — all true:
1. On `fixture-a`, `result=fail` because `beta` has `require_code_owner_reviews: false`.
2. `checked` equals 2.
3. The template is read from the committed file, never from the reconciler's in-memory copy.

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p5-03-protection-assertion

# Create validators/drift/assert_protection.py, tests/test_assert_protection.py

git add validators/drift/assert_protection.py validators/drift/tests/test_assert_protection.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P5-03: verifier assertion B: branch protection matches committed template"
git push -u origin lane/3/p5-03-protection-assertion
gh pr create --title "L3-P5-03: verifier assertion B: branch protection matches committed template" --base integration --body "Closes L3-P5-03"
```

**SELF-VERIFY**

```bash
python -m validators.drift.verifier --fixture fixture-a --only protection_matches_template --summary; echo "exit=$?"
```

Expected output, exactly:

```
VERIFY protection_matches_template result=fail checked=2
VERIFIER result=fail assertions=1
exit=2
```

**STOP** — none beyond the standing rule.

---

### L3-P5-04 — Verifier assertion C: the bypass-actor list is exactly as declared

**Phase** 5 · **Size** M · **Deps** L3-P5-01 · **Spec** §53.1 (*"that the ruleset bypass-actor list is exactly the set Sections 40.1 and 33.2 declare, with their declared scopes"*); §40.1 (D89: *"no machine identity is a bypass actor"* on the control plane); §33.2

**Files (create):** `validators/drift/assert_bypass.py`, `validators/drift/tests/test_assert_bypass.py`

Assertion id `bypass_actors_exact`. The declared set, transcribed:

* **Control-plane repository:** the bypass-actor list is **empty**. §40.1: *"No bypass actor exists"*; D89 makes this *"literally true rather than true-by-convention"*.
* **Records repository:** the force-push/deletion ruleset has **no bypass actor** (D107).
* **`workflows/*` tag ruleset:** **empty** bypass-actor list (§33.2).
* **Renovate ruleset A** (pull-request rules): may list the Renovate app and nothing else.
* **Renovate ruleset B** (the `renovate-path-guard` check): **no bypass actor at all** (§33.2, D89).

Any actor outside this set, in either direction, fails. `checked` = number of rulesets examined.

**Acceptance** — all true:
1. On `fixture-a`, `result=fail` because `renovate-B` lists `renovate[bot]`.
2. `checked` equals 2.
3. The declared set is a literal table in the module, each row citing its spec section — not inferred from the actual state.

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p5-04-bypass-assertion

# Create validators/drift/assert_bypass.py, tests/test_assert_bypass.py

git add validators/drift/assert_bypass.py validators/drift/tests/test_assert_bypass.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P5-04: verifier assertion C: bypass-actor list exactly as declared"
git push -u origin lane/3/p5-04-bypass-assertion
gh pr create --title "L3-P5-04: verifier assertion C: bypass-actor list exactly as declared" --base integration --body "Closes L3-P5-04"
```

**SELF-VERIFY**

```bash
python -m validators.drift.verifier --fixture fixture-a --only bypass_actors_exact --summary; echo "exit=$?"
```

Expected output, exactly:

```
VERIFY bypass_actors_exact result=fail checked=2
VERIFIER result=fail assertions=1
exit=2
```

**STOP** — if any live ruleset names a bypass actor not in the table above, do **not** widen the table. That is exactly the finding. File the blocker.

---

### L3-P5-05 — Verifier absence for one cycle is Level 5

**Phase** 5 · **Size** S · **Deps** L3-P5-01 · **Spec** §53.1 (*"its own absence for one cycle is Level 5"*); §53.2 Level 5; AT-032

**Files (create):** `validators/drift/liveness.py`, `validators/drift/tests/test_liveness.py`

Implement `check_liveness(last_verifier_result_at, as_of, cycle_hours)` returning a `Level.ESCALATE` finding when the gap exceeds one cycle. The check runs **inside the reconciler's run as well**, so that a dead verifier is visible from both sides; expose it as a plain function that `reconciler/signals.py` may import.

**Acceptance** — all true:
1. A gap of one cycle plus one minute yields `Level.ESCALATE`.
2. A gap inside one cycle yields no finding.
3. The function has no side effect and issues no notification.

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p5-05-liveness

# Create validators/drift/liveness.py, tests/test_liveness.py

git add validators/drift/liveness.py validators/drift/tests/test_liveness.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P5-05: verifier absence for one cycle is Level 5"
git push -u origin lane/3/p5-05-liveness
gh pr create --title "L3-P5-05: verifier absence for one cycle is Level 5" --base integration --body "Closes L3-P5-05"
```

**SELF-VERIFY**

```bash
python -m pytest validators/drift/tests/test_liveness.py -q
```

Expected output, exactly:

```
4 passed
```

**STOP** — none beyond the standing rule.

---

### L3-P5-06 — AT-110 credential-bounds probe: six negative attempts

**Phase** 5 · **Size** L · **Deps** L3-P3-02 · **Spec** **AT-110** verbatim; §40.1; §99.6 risk 6

L3-P5-06 --mode live is the single credential probe for live system access. `L3-07` T10's `AT-110.sh` is reduced to `GATE.md` + `RESULT.template.md` invoking it.

**Files (create):** `validators/drift/credential_bounds.py`, `validators/drift/tests/test_credential_bounds.py`

AT-110, transcribed: *"From the reconciler's own credential, six attempts are made — a write to a GitHub Actions secret, a write to an environment, a workflow-file change, an organisation-settings change, a `records/**` write, and any Layer B access — and all six fail; the credential then still completes a normal reconciliation run."*

Implement `probe(credential, mode)` performing exactly those six attempts in that order, each returning `blocked` or `PERMITTED`, followed by a normal reconciliation run that must still complete. Two modes: `fixture` (a fixture credential simulating the declared permission set, used by every acceptance command here) and `live` (used only at the phase that builds the reconciler and at every rotation — §40.1: *"After any rotation, a manual reconciliation run must complete clean before the rotation is recorded as done"*).

Any attempt returning `PERMITTED` is a **security incident under §43**, not a test failure: the probe must say so in its output and exit `3`.

**Acceptance** — all true:
1. All six attempts are present, in AT-110's order, each named in the output.
2. In fixture mode, all six report `blocked` and the follow-on reconciliation run completes.
3. A single `PERMITTED` result exits `3` and prints the §43 escalation line.

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p5-06-credential-bounds

# Create validators/drift/credential_bounds.py, tests/test_credential_bounds.py

git add validators/drift/credential_bounds.py validators/drift/tests/test_credential_bounds.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P5-06: AT-110 credential-bounds probe: six negative attempts"
git push -u origin lane/3/p5-06-credential-bounds
gh pr create --title "L3-P5-06: AT-110 credential-bounds probe: six negative attempts" --base integration --body "Closes L3-P5-06"
```

**SELF-VERIFY**

```bash
python -m pytest validators/drift/tests/test_credential_bounds.py -q && python -m validators.drift.credential_bounds --mode fixture --summary
```

Expected output, exactly:

```
7 passed
PROBE actions_secret_write=blocked
PROBE environment_write=blocked
PROBE workflow_file_change=blocked
PROBE org_settings_change=blocked
PROBE records_write=blocked
PROBE layer_b_access=blocked
PROBE reconciliation_after=complete
AT-110 result=pass attempts=6
```

**STOP** — if any attempt returns `PERMITTED` in **live** mode, stop everything: open a security incident under §43 before any further Lane 3 work, and file the blocker referencing §99.6 risk 6 (*"the reconciler's own credential in the top secrets tier with its compromise treated as a security incident"*).

---

### L3-P5-07 — Behavioural-envelope checks

**Phase** 5 · **Size** L · **Deps** L3-P1-18 · **Spec** §40.1 *"The behavioural envelope"* (all four controls); §40.3

**Files (create):** `reconciler/envelope.py`, `reconciler/tests/test_envelope.py`

Implement the four controls §40.1 names, and only those four:

| Control | Rule |
| --- | --- |
| `signed_run_record` | every run names its scheduled trigger; a run with no matching trigger record raises immediately |
| `run_count_ceiling` | calibrated configuration, initial value **twice the scheduled run count per day**, recalibrated whenever the schedule changes |
| `expected_source_host` | a run from any other host is out of envelope |
| `per_run_api_call_counts` | published per run, so read-side abuse surfaces as a volume anomaly |

A run outside the envelope is `BLOCKING` drift. §40.1 explains why time alone is not the boundary: *"an alert that cannot fire is a gate that appears to be working and is not."*

**Acceptance** — all true:
1. All four controls exist; a run breaching any one produces a `BLOCKING` finding naming which control.
2. The ceiling is configuration, not a literal, and its initial value is twice the scheduled run count.
3. The API-call count is published on every run, including clean ones.

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p5-07-envelope

# Create reconciler/envelope.py, tests/test_envelope.py

git add reconciler/envelope.py reconciler/tests/test_envelope.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P5-07: behavioural-envelope checks"
git push -u origin lane/3/p5-07-envelope
gh pr create --title "L3-P5-07: behavioural-envelope checks" --base integration --body "Closes L3-P5-07"
```

**SELF-VERIFY**

```bash
python -m pytest reconciler/tests/test_envelope.py -q && python -c "
from reconciler.envelope import CONTROLS
print('controls', len(CONTROLS), sorted(CONTROLS))"
```

Expected output, exactly:

```
8 passed
controls 4 ['expected_source_host', 'per_run_api_call_counts', 'run_count_ceiling', 'signed_run_record']
```

**STOP** — if the envelope is reduced to a scheduled-window check, stop: §40.1 rejects that explicitly (*"the complement is nearly empty, an attacker simply acts inside the hour"*).

---

### L3-P5-08 — Records-repository head SHA anchor

**Phase** 5 · **Size** M · **Deps** L3-P1-18 · **Spec** §40.1 *"History is anchored where it cannot be rewritten"* (D107); §53.2 Level 5; §101 invariant 47

**Files (create):** `reconciler/anchor.py`, `reconciler/tests/test_anchor.py`

Implement `anchor(records_head_sha, commit_count, previous_anchor)`: once per reconciliation run, record the records repository's default-branch head SHA and commit count. If the new head does **not descend** from the last anchored SHA, that is **Blocking drift at Level 5** — D107: *"a head that does not descend from the last anchored SHA is proof of rewriting rather than evidence of it."*

The anchor value is produced here and handed to the control-plane write path; this lane does **not** write it into `records/**` (that repository is Lane 4's, and the reconciler credential cannot reach it — AT-110 attempt 5).

**Acceptance** — all true:
1. A descendant head anchors cleanly.
2. A non-descendant head yields `Level.ESCALATE` and `DriftClass.BLOCKING`.
3. The module performs no write to `records/**` or `events/**`.

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p5-08-anchor

# Create reconciler/anchor.py, tests/test_anchor.py

git add reconciler/anchor.py reconciler/tests/test_anchor.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P5-08: records-repository head SHA anchor"
git push -u origin lane/3/p5-08-anchor
gh pr create --title "L3-P5-08: records-repository head SHA anchor" --base integration --body "Closes L3-P5-08"
```

**SELF-VERIFY**

```bash
python -m pytest reconciler/tests/test_anchor.py -q && grep -rc "records/" reconciler/anchor.py | head -1
```

Expected output, exactly:

```
6 passed
reconciler/anchor.py:0
```

**STOP** — none beyond the standing rule.

---

## 9. Phase 6 — Auto-repair (Level 3), one class at a time

**Do not start this phase until detection has run clean for the period L0 records.** §99.4 item 6: *"Auto-repair is deferred until detection has run clean for weeks; auto-repair is the riskiest code in the system, and its stricter-only rule is enforced in code and tested."* §99.6 risk 6: *"Detect-only first; repair classes enabled one at a time."* Literal detect-clean period: 30 days (as required by REG-027).

Every repair class in this phase is written against the same three-part contract: it consumes a finding produced in Phase 1 or 2, it asks `stricter.py` for permission, and it writes a repair record. No repair class may bypass any of the three.

---

### L3-P6-01 — Stricter-only predicate and its proof suite

**Phase** 6 · **Size** L · **Deps** L3-P1-19 · **Spec** §53.3 verbatim; §101 invariant 81; **AT-033**

**Files (create):** `reconciler/repair/__init__.py`, `reconciler/repair/stricter.py`, `reconciler/tests/test_stricter.py`

Implement `permitted(declared, actual, control_kind) -> tuple[bool, str]` returning `(True, "")` only when **both** hold: the repair moves actual toward declared, **and** declared is at least as restrictive as actual. Otherwise return `(False, reason)`. Four absolute refusals, returning `False` unconditionally regardless of direction: production runtime configuration, data, secrets, and any control the repair would loosen (§53.3).

The proof suite is the point of this task. Write at least twelve cases covering: declared stricter and actual loose (permit); declared loose and actual stricter (refuse, and emit Level 2 for human judgment — AT-033); equal (no repair); each of the four absolute refusals; a boolean flag in both directions; a numeric threshold in both directions; a list of required contexts in both directions.

**Acceptance** — all true:
1. Every one of the twelve cases passes, and the actual-stricter case emits `Level.WARN`, never a repair.
2. The four absolute refusals return `False` even when the direction is toward declared.
3. `permitted()` is the **only** gate: no repair module may write without calling it (asserted in L3-P6-09).

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p6-01-stricter

# Create reconciler/repair/__init__.py, repair/stricter.py, tests/test_stricter.py

git add reconciler/repair/__init__.py reconciler/repair/stricter.py reconciler/tests/test_stricter.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P6-01: stricter-only predicate and its proof suite"
git push -u origin lane/3/p6-01-stricter
gh pr create --title "L3-P6-01: stricter-only predicate and its proof suite" --base integration --body "Closes L3-P6-01"
```

**SELF-VERIFY**

```bash
python -m pytest reconciler/tests/test_stricter.py -q && python -c "
from reconciler.repair.stricter import permitted
print(permitted({'require_code_owner_reviews':True},{'require_code_owner_reviews':False},'branch_protection')[0])
print(permitted({'require_code_owner_reviews':False},{'require_code_owner_reviews':True},'branch_protection')[0])
print(permitted({'x':1},{'x':0},'secret')[0])"
```

Expected output, exactly:

```
12 passed
True
False
False
```

**STOP** — if a repair class needs an exemption from `permitted()`, stop. Invariant 81 admits no exemption. File the blocker addressed to L0.

---

### L3-P6-02 — Repair enablement registry, every class default-off

**Phase** 6 · **Size** M · **Deps** L3-P6-01 · **Spec** §99.6 risk 6 (*"repair classes enabled one at a time"*); §98.3; §64.1

**Files (create):** `reconciler/repair/enablement.py`, `reconciler/tests/test_enablement.py`

Implement `REPAIR_CLASSES`: the five §53.2 Level-3 classes, transcribed — `team_sync` (Team membership sync from registries), `codeowners_regen` (CODEOWNERS regeneration), `label_sync` (label and board field sync), `protection_reapply` (re-applying declared branch protection), `expiry_revoke` (removing expired assignments and expired access). Each carries `enabled: False` as its **declared default**, an `enabled_on` date, and an `enabled_by` decision-record id. Enabling requires all three; enabling more than one class in a single change **raises**.

`python -m reconciler.cli repair-classes --summary` prints one line per class: `CLASS <id> enabled=<true|false>`, then `REPAIR_CLASSES total=5 enabled=<int>`.

**Acceptance** — all true:
1. All five classes exist, and all five default to `enabled=false`.
2. Enabling a class without a decision-record id raises.
3. Enabling two classes in one change raises.

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p6-02-repair-enablement

# Create reconciler/repair/enablement.py, tests/test_enablement.py

git add reconciler/repair/enablement.py reconciler/tests/test_enablement.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P6-02: repair enablement registry, every class default-off"
git push -u origin lane/3/p6-02-repair-enablement
gh pr create --title "L3-P6-02: repair enablement registry, every class default-off" --base integration --body "Closes L3-P6-02"
```

**SELF-VERIFY**

```bash
python -m reconciler.cli repair-classes --summary
```

Expected output, exactly:

```
CLASS codeowners_regen enabled=false
CLASS expiry_revoke enabled=false
CLASS label_sync enabled=false
CLASS protection_reapply enabled=false
CLASS team_sync enabled=false
REPAIR_CLASSES total=5 enabled=0
```

**STOP** — if a class ships enabled *"because detection has been clean"*, stop: enabling is a recorded decision, not an implementation default. File the blocker.

---

### L3-P6-03 — Repair class: Team membership sync from the registries

**Phase** 6 · **Size** M · **Deps** L3-P6-02 · **Spec** §53.2 Level 3; §11.2; §26.4 (*"reconciliation Level-3 auto-repairs … write directly under the reconciler credential, logged as repair records"*)

**Files (create):** `reconciler/repair/team_sync.py`, `reconciler/tests/test_repair_team_sync.py`

Consume `team_membership` findings. For each, call `permitted()`; on approval, add missing declared holders and remove members holding no assignment. **Removal is the stricter direction and is permitted; addition of a member is permitted only where the registry declares the assignment.** No membership is ever added from actual state.

**Acceptance** — all true:
1. On `fixture-a` with the class enabled, exactly one repair: `dev-2` removed from team `alpha`.
2. With the class disabled (the default), zero repairs and the finding remains open.
3. Every repair calls `permitted()` first; a test asserts the call.

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p6-03-team-sync

# Create reconciler/repair/team_sync.py, tests/test_repair_team_sync.py

git add reconciler/repair/team_sync.py reconciler/tests/test_repair_team_sync.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P6-03: repair class: team membership sync from the registries"
git push -u origin lane/3/p6-03-team-sync
gh pr create --title "L3-P6-03: repair class: team membership sync from the registries" --base integration --body "Closes L3-P6-03"
```

**SELF-VERIFY**

```bash
python -m pytest reconciler/tests/test_repair_team_sync.py -q
```

Expected output, exactly:

```
7 passed
```

**STOP** — none beyond the standing rule.

---

### L3-P6-04 — Repair class: CODEOWNERS regeneration

**Phase** 6 · **Size** M · **Deps** L3-P6-02, L3-P4-02 · **Spec** §53.1 row 4; §53.2 Level 3; §11.3

**Files (create):** `reconciler/repair/codeowners_regen.py`, `reconciler/tests/test_repair_codeowners.py`

Consume `codeowners` findings. Regenerate through `tools.provision.codeowners.generate` — one generator, never two — and write the result. The generator's machine-identity refusal (L3-P4-02) therefore applies to the repair path too: a regeneration that would emit a machine identity **raises rather than writes**.

**Acceptance** — all true:
1. Regeneration for `alpha` removes `@ci-bot` and produces a human-only file.
2. A generation attempt that would emit a machine identity raises and writes nothing.
3. The module imports the provisioning generator rather than reimplementing it.

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p6-04-codeowners-regen

# Create reconciler/repair/codeowners_regen.py, tests/test_repair_codeowners.py

git add reconciler/repair/codeowners_regen.py reconciler/tests/test_repair_codeowners.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P6-04: repair class: CODEOWNERS regeneration"
git push -u origin lane/3/p6-04-codeowners-regen
gh pr create --title "L3-P6-04: repair class: CODEOWNERS regeneration" --base integration --body "Closes L3-P6-04"
```

**SELF-VERIFY**

```bash
python -m pytest reconciler/tests/test_repair_codeowners.py -q && grep -c "from tools.provision.codeowners import generate" reconciler/repair/codeowners_regen.py
```

Expected output, exactly:

```
6 passed
1
```

**STOP** — none beyond the standing rule.

---

### L3-P6-05 — Repair class: re-apply declared branch protection

**Phase** 6 · **Size** M · **Deps** L3-P6-02, L3-P4-03 · **Spec** §53.2 Level 3 (*"re-applying declared branch protection"*); §53.3; AT-033

**Files (create):** `reconciler/repair/protection_reapply.py`, `reconciler/tests/test_repair_protection.py`

Consume `branch_protection` findings. Re-apply the declared template **only** where `permitted()` approves. Where actual is stricter than declared, do nothing and leave the Level 2 finding standing — this is AT-033 in code: *"Reconciliation presented with a stricter-than-declared production control raises it for human review and does not relax it."*

**Acceptance** — all true:
1. `beta`'s `require_code_owner_reviews: false` is repaired to `true`.
2. A repository with a stricter-than-declared setting is **not** touched, and its Level 2 finding remains.
3. The required-status-check `contexts` list is never shortened by a repair.

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p6-05-protection-reapply

# Create reconciler/repair/protection_reapply.py, tests/test_repair_protection.py

git add reconciler/repair/protection_reapply.py reconciler/tests/test_repair_protection.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P6-05: repair class: re-apply declared branch protection"
git push -u origin lane/3/p6-05-protection-reapply
gh pr create --title "L3-P6-05: repair class: re-apply declared branch protection" --base integration --body "Closes L3-P6-05"
```

**SELF-VERIFY**

```bash
python -m pytest reconciler/tests/test_repair_protection.py -q
```

Expected output, exactly:

```
8 passed
```

**STOP** — if a repair would shorten the `contexts` list to make a repository green, stop: that loosens a control. File the blocker.

---

### L3-P6-06 — Repair class: expired assignment and expired access removal

**Phase** 6 · **Size** M · **Deps** L3-P6-02 · **Spec** §53.1 row 11; §53.2 Level 3; §101 invariant 58; **AT-008**, **AT-018**, **AT-036**

**Files (create):** `reconciler/repair/expiry_revoke.py`, `reconciler/tests/test_repair_expiry.py`

Consume `expiry` findings and expired exception entries. Remove the expired assignment and revoke the access it conferred, **without human action** — AT-018: *"Reconciliation removes it without human action; access is revoked and capacity recalculated."* AT-036: *"Reconciliation revokes it with no human action."* An exception that cannot be auto-revoked becomes **Blocking drift on its expiry date** (AT-037).

Per §26.4, this class writes directly under the reconciler credential and bypasses the human owner-review lane, *"routing these machine-derived transitions through human reviewers would queue the 'no human action required' expiry guarantees behind the very people they are designed not to need."*

**Acceptance** — all true:
1. `dev-1`'s expired `temporary_contributor` on `alpha` is removed and Team access revoked.
2. An exception past expiry that cannot be revoked yields a `BLOCKING` finding rather than a silent skip (AT-037).
3. A temporary assignment never becomes a permanent one through inaction (§10.2).

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p6-06-expiry-revoke

# Create reconciler/repair/expiry_revoke.py, tests/test_repair_expiry.py

git add reconciler/repair/expiry_revoke.py reconciler/tests/test_repair_expiry.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P6-06: repair class: expired assignment and expired access removal"
git push -u origin lane/3/p6-06-expiry-revoke
gh pr create --title "L3-P6-06: repair class: expired assignment and expired access removal" --base integration --body "Closes L3-P6-06"
```

**SELF-VERIFY**

```bash
python -m pytest reconciler/tests/test_repair_expiry.py -q
```

Expected output, exactly:

```
8 passed
```

**STOP** — none beyond the standing rule.

---

### L3-P6-07 — Repair class: label and board field sync

**Phase** 6 · **Size** M · **Deps** L3-P6-02 · **Spec** §53.2 Level 3 (*"label and board field sync"*)

**Files (create):** `reconciler/repair/label_sync.py`, `reconciler/tests/test_repair_labels.py`

Consume label and board-field drift findings and sync them to declared state. This is the lowest-risk class in the set and confers no authority; it still goes through `permitted()` and still writes a repair record, because the contract is uniform.

**Acceptance** — all true:
1. Labels and board fields sync to declared values.
2. The class touches no permission, no protection, no membership.
3. It calls `permitted()` and writes a repair record like every other class.

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p6-07-label-sync

# Create reconciler/repair/label_sync.py, tests/test_repair_labels.py

git add reconciler/repair/label_sync.py reconciler/tests/test_repair_labels.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P6-07: repair class: label and board field sync"
git push -u origin lane/3/p6-07-label-sync
gh pr create --title "L3-P6-07: repair class: label and board field sync" --base integration --body "Closes L3-P6-07"
```

**SELF-VERIFY**

```bash
python -m pytest reconciler/tests/test_repair_labels.py -q
```

Expected output, exactly:

```
5 passed
```

**STOP** — none beyond the standing rule.

---

### L3-P6-08 — Repair record emitter

**Phase** 6 · **Size** M · **Deps** L3-P6-02 · **Spec** §26.4 (*"logged as repair records and visible on the drift view"*); §53.2 Level 3 (*"then record the repair"*); §53.7

**Files (create):** `reconciler/repair/records.py`, `reconciler/tests/test_repair_records.py`

Emit one repair record per repair, shaped to the `repair_record` contract from `contracts_map`, carrying at minimum: `repair_class`, `finding_id`, `scope`, `before`, `after`, `permitted_reason`, `performed_at`, `run_id`, and the **compensating action** the change plan was required to name and test (§53.7, §28.1) — without that field, §53.7's revert branch has nothing to revert against.

Records are handed to the control-plane write path; this lane does not write them into `records/**` (Lane 4, AT-110 attempt 5).

**Acceptance** — all true:
1. Every repair produces exactly one record, with `before` and `after` both populated.
2. A record missing `compensating_action` raises at emit time.
3. No write reaches `records/**` or `events/**` from this module.

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p6-08-repair-records

# Create reconciler/repair/records.py, tests/test_repair_records.py

git add reconciler/repair/records.py reconciler/tests/test_repair_records.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P6-08: repair record emitter"
git push -u origin lane/3/p6-08-repair-records
gh pr create --title "L3-P6-08: repair record emitter" --base integration --body "Closes L3-P6-08"
```

**SELF-VERIFY**

```bash
python -m pytest reconciler/tests/test_repair_records.py -q
```

Expected output, exactly:

```
7 passed
```

**STOP** — none beyond the standing rule.

---

### L3-P6-09 — Prohibited-repair guards

**Phase** 6 · **Size** M · **Deps** L3-P6-01 · **Spec** §53.3 (*"never modifies production runtime configuration, never modifies data, and never rotates or writes secrets"*); §40.1; AT-110

**Files (create):** `reconciler/repair/guards.py`, `reconciler/tests/test_repair_guards.py`

Implement an import-time guard asserting, for every module under `reconciler/repair/**`: it calls `permitted()` before any write; it contains no call that writes a secret, an environment, a workflow file, an organisation setting, or `records/**`. Run the guard as a test over the package, so adding a sixth repair class in future cannot skip it.

**Acceptance** — all true:
1. The guard enumerates every module under `reconciler/repair/**` — it does not use a hard-coded module list.
2. A deliberately non-compliant test module fails the guard.
3. All five shipped classes pass.

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p6-09-repair-guards

# Create reconciler/repair/guards.py, tests/test_repair_guards.py

git add reconciler/repair/guards.py reconciler/tests/test_repair_guards.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P6-09: prohibited-repair guards"
git push -u origin lane/3/p6-09-repair-guards
gh pr create --title "L3-P6-09: prohibited-repair guards" --base integration --body "Closes L3-P6-09"
```

**SELF-VERIFY**

```bash
python -m pytest reconciler/tests/test_repair_guards.py -q && python -c "
from reconciler.repair.guards import audit_package
print('modules', len(audit_package()), 'violations', sum(1 for m in audit_package() if m.violations))"
```

Expected output, exactly:

```
6 passed
modules 5 violations 0
```

**STOP** — if `modules` is not 5, a repair class from L3-P6-03…07 is unmerged, or a sixth class was added without a task in this file. Either way, file the blocker.

---

### L3-P6-10 — Repeated failed repair escalates to Level 5

**Phase** 6 · **Size** S · **Deps** L3-P6-08 · **Spec** §53.2 Level 5 (*"repeated failed auto-repair"*, *"a repair class discovered to have written incorrect state"*)

**Files (create):** `reconciler/repair/escalation.py`, `reconciler/tests/test_repair_escalation.py`

Implement `evaluate(repair_history, threshold)` raising `Level.ESCALATE` when a repair class fails repeatedly against the same scope. The threshold is configuration with an initial value of 3 consecutive failures. Escalation creates an incident and notifies the escalation role — **emit the escalation object only**; routing belongs to Lane 5 (`notify/**`).

**Acceptance** — all true:
1. Three consecutive failures on one scope produce `Level.ESCALATE`.
2. Two failures do not.
3. No notification call exists in this lane.

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p6-10-repair-escalation

# Create reconciler/repair/escalation.py, tests/test_repair_escalation.py

git add reconciler/repair/escalation.py reconciler/tests/test_repair_escalation.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P6-10: repeated failed repair escalates to Level 5"
git push -u origin lane/3/p6-10-repair-escalation
gh pr create --title "L3-P6-10: repeated failed repair escalates to Level 5" --base integration --body "Closes L3-P6-10"
```

**SELF-VERIFY**

```bash
python -m pytest reconciler/tests/test_repair_escalation.py -q && grep -rcE "requests\.|urllib|webhook" reconciler/repair/escalation.py
```

Expected output, exactly:

```
5 passed
0
```

**STOP** — none beyond the standing rule.

---

## 10. Phase 7 — Lifecycle operations and registry-edit staging

§98.3 places `change-role`, `remove-person` and template evolution in early hardening: *"Scaffolding v0 (`create-product`, `add-person`) ships in Phase 3 … the rest follow the first role change and the first departure."*

---

### L3-P7-01 — `change-role` operation

**Phase** 7 · **Size** L · **Deps** L3-P4-09 · **Spec** §12.6 (`change role`); §12.3; §101 invariant 56; AT-005

**Files (create):** `tools/provision/change_role.py`, `tools/provision/tests/test_change_role.py`

Compose the plan in **exactly** the §12.6 order, seven steps: `role_update`, `capability_recalculation`, `permission_recalculation`, `reviewer_matrix_reassessment`, `ownership_reassessment_prompt`, `incident_responder_reassessment`, `dashboard_update`. Every step is **declarative**: the operation edits registry state and lets reconciliation apply it (§101 invariant 55: *"Ownership changes are declarative and take effect through reconciliation"*).

Two hard rules, both from §74 and §101 invariants 36–38: `ownership_reassessment_prompt` is a **prompt**, never an automatic reassignment; and this operation must contain **no code path** to a formal people decision — promotion, compensation, warning, improvement plan or exit (AT-071: *"No code path exists to an automated improvement plan, termination, promotion, compensation change or formal warning"*).

**Acceptance** — all true:
1. `PLAN change-role steps=7 writes=0 manual=0` on a dry run.
2. `ownership_reassessment_prompt` emits a prompt, and a test asserts no automatic reassignment occurs.
3. `grep -riE "promotion|termination|compensation|improvement_plan|formal_warning" tools/provision/change_role.py` returns nothing outside a refusal guard.

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p7-01-change-role

# Create tools/provision/change_role.py, tests/test_change_role.py

git add tools/provision/change_role.py tools/provision/tests/test_change_role.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P7-01: change-role operation"
git push -u origin lane/3/p7-01-change-role
gh pr create --title "L3-P7-01: change-role operation" --base integration --body "Closes L3-P7-01"
```

**SELF-VERIFY**

```bash
python -m tools.provision.cli change-role --fixture fixture-a --login dev-1 --to-role qa --dry-run --summary
```

Expected output, exactly:

```
PLAN change-role steps=7 writes=0 manual=0
```

**STOP** — if any request asks this operation to finalise a personnel action, stop: AT-071 requires that no such code path exist, and *"attempted configuration of one fails validation."* File the blocker.

---

### L3-P7-02 — `remove-person` operation

**Phase** 7 · **Size** L · **Deps** L3-P2-05, L3-P4-09 · **Spec** §12.2 (the RECONCILIATION EXECUTES block); §12.6 (`remove person`); §101 invariant 57; AT-017

**Files (create):** `tools/provision/remove_person.py`, `tools/provision/tests/test_remove_person.py`

Compose the plan in **exactly** the §12.2 order, eleven steps:

| # | Step id | §12.2 line |
| --- | --- | --- |
| 1 | `remove_from_organisation` | remove from organisation |
| 2 | `remove_from_every_team` | remove from every GitHub Team |
| 3 | `revoke_every_environment_access` | revoke every environment access |
| 4 | `revoke_production_capability` | revoke production capability |
| 5 | `deactivate_ai_runtime` | deactivate AI runtime |
| 6 | `stop_self_view_and_retire_key` | stop self-view generation and retire the registered self-view key material (§90.6) |
| 7 | `remove_from_reviewer_matrix` | remove from reviewer matrix |
| 8 | `recalculate_ownership` | recalculate ownership |
| 9 | `recalculate_incident_responders` | recalculate incident responder assignments |
| 10 | `orphan_detection` | ORPHAN DETECTION RUNS |
| 11 | `exit_record` | EXIT RECORD COMPLETED |

Two further rules, both transcribed: the person record is **retained, never deleted, and the identifier is never reused** (§12.2 final line); and a departing succession designate in `topology.yaml` is **flagged immediately** so succession is never left vacant by a departure (§12.2).

**Acceptance** — all true:
1. `PLAN remove-person steps=11 writes=0 manual=0` on a dry run.
2. No step deletes a person record, and a test asserts the identifier is not released for reuse.
3. Step 10 invokes the Phase 2 orphan detector, and Blocking orphans returned by it cannot be dismissed (L3-P2-06, invariant 57).

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p7-02-remove-person

# Create tools/provision/remove_person.py, tests/test_remove_person.py

git add tools/provision/remove_person.py tools/provision/tests/test_remove_person.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P7-02: remove-person operation"
git push -u origin lane/3/p7-02-remove-person
gh pr create --title "L3-P7-02: remove-person operation" --base integration --body "Closes L3-P7-02"
```

**SELF-VERIFY**

```bash
python -m tools.provision.cli remove-person --fixture fixture-a --login dev-1 --dry-run --summary
```

Expected output, exactly:

```
PLAN remove-person steps=11 writes=0 manual=0
```

**STOP** — if a step would delete the person record to satisfy a data-deletion request, stop: that is the §91.8 ex-employee data-rights path, not this operation. File the blocker.

---

### L3-P7-03 — Registry-edit canary staging

**Phase** 7 · **Size** L · **Deps** L3-P6-02 · **Spec** §26.4 *"Registry edits stage before they reach the fleet"* (both rules); §61.5

**Files (create):** `reconciler/staging.py`, `reconciler/tests/test_staging.py`

Rule one, transcribed: *"a merged registry change is applied by the next reconciliation run to the declared canary set only; the remainder of the fleet is held for one reconciliation cycle and applied only after the canary cycle records a clean run."*

Implement `stage(change, canary_set, last_canary_run)` returning the set of products a run may apply the change to. The fleet is released **only** when the immediately preceding canary cycle recorded a clean run — and a canary cycle whose run was `FAILED`, including a canary-missing run (L3-P1-17), is **not** clean.

**Acceptance** — all true:
1. The first run after a merged registry change applies to the canary set only.
2. The fleet is released only after a clean canary cycle; a `FAILED` canary cycle holds the fleet.
3. Staging binds in bootstrap mode too (§26.4: *"Both rules remain binding in bootstrap"*) — a test asserts the bootstrap flag does not bypass it.

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p7-03-staging

# Create reconciler/staging.py, tests/test_staging.py

git add reconciler/staging.py reconciler/tests/test_staging.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P7-03: registry-edit canary staging"
git push -u origin lane/3/p7-03-staging
gh pr create --title "L3-P7-03: registry-edit canary staging" --base integration --body "Closes L3-P7-03"
```

**SELF-VERIFY**

```bash
python -m pytest reconciler/tests/test_staging.py -q
```

Expected output, exactly:

```
8 passed
```

**STOP** — if a caller asks for an urgent fleet-wide registry application skipping the canary cycle, stop: §101 invariant 72 forbids fleet rollout without a canary. File the blocker.

---

### L3-P7-04 — Authority-delta detector

**Phase** 7 · **Size** M · **Deps** L3-P7-03 · **Spec** §26.4 rule two (*"an authority delta — a diff that adds a capability, adds an assignment type conferring Write, or changes `access_status` — fails CI without a linked decision record ID in the same commit"*)

**Files (create):** `validators/drift/authority_delta.py`, `validators/drift/tests/test_authority_delta.py`

Implement `detect(diff) -> list[AuthorityDelta]` recognising exactly the three deltas §26.4 names: a capability added; an assignment type conferring Write added (`primary_owner`, `cross_reviewer`, `backup_owner`, `temporary_contributor` — §11.2); `access_status` changed. Each delta without a linked decision-record ID in the same commit fails.

§26.4 gives the reason, and it belongs in the module docstring: *"where a wrong revocation is caught by orphan risk (SIG-05), a wrong grant has no detector at all."*

**Acceptance** — all true:
1. All three delta kinds are detected; a diff touching only a display name is not a delta.
2. A delta with a decision-record ID in the same commit passes; without one it fails.
3. The detector lives in `validators/drift/**` and imports nothing from `reconciler/**` (it guards the registry, not the instrument).

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p7-04-authority-delta

# Create validators/drift/authority_delta.py, tests/test_authority_delta.py

git add validators/drift/authority_delta.py validators/drift/tests/test_authority_delta.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P7-04: authority-delta detector"
git push -u origin lane/3/p7-04-authority-delta
gh pr create --title "L3-P7-04: authority-delta detector" --base integration --body "Closes L3-P7-04"
```

**SELF-VERIFY**

```bash
python -m pytest validators/drift/tests/test_authority_delta.py -q && grep -rc "import reconciler" validators/drift/authority_delta.py
```

Expected output, exactly:

```
7 passed
0
```

**STOP** — none beyond the standing rule of §0.6.

---

### L3-P7-05 — Temporary-person expiry treated as an exit

**Phase** 7 · **Size** M · **Deps** L3-P7-02 · **Spec** §12.2 (*"Temporary-person expiry is an exit. Expiry of a temporary specialist or contractor triggers the same exit record and orphan scan as `remove person`"*); §12.4; AT-008

**Files (create):** `tools/provision/temp_expiry.py`, `tools/provision/tests/test_temp_expiry.py`

Implement `on_expiry(person, as_of)` invoking the **same** eleven-step `remove-person` plan, not a reduced variant, and additionally raising orphan type 14 where the expiring person holds open gate-relevant work — §12.2 names it *"the fourteenth orphan type."*

**Acceptance** — all true:
1. An expiring temporary person produces the identical eleven-step plan as `remove-person`.
2. Orphan type 14 is raised when the person holds an open gate item at expiry.
3. Expiry requires no human action to execute (AT-008: *"reconciliation revokes on the end date without human action"*).

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p7-05-temp-expiry

# Create tools/provision/temp_expiry.py, tests/test_temp_expiry.py

git add tools/provision/temp_expiry.py tools/provision/tests/test_temp_expiry.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P7-05: temporary-person expiry treated as an exit"
git push -u origin lane/3/p7-05-temp-expiry
gh pr create --title "L3-P7-05: temporary-person expiry treated as an exit" --base integration --body "Closes L3-P7-05"
```

**SELF-VERIFY**

```bash
python -m pytest tools/provision/tests/test_temp_expiry.py -q && python -c "
from tools.provision.temp_expiry import on_expiry
print('steps', len(on_expiry('dev-1','2026-08-27').steps))"
```

Expected output, exactly:

```
6 passed
steps 11
```

**STOP** — if a shortened expiry path is proposed for contractors, stop: §12.2 makes expiry the same exit. File the blocker.

---

## 11. Phase 8 — The control-loop gap procedure and lane closure

§53.7: *"The control loop can fail in two directions. It can go dark … It can also run and repair against a wrongly-computed declared state, which completes, records clean, and is therefore invisible to every check that asks only whether the loop ran."* This phase builds both branches.

---

### L3-P8-01 — Gap detector and expiry replay

**Phase** 8 · **Size** M · **Deps** L3-P6-06 · **Spec** §53.7 bullets 1 and 3; §46.1

**Files (create):** `reconciler/gap/__init__.py`, `reconciler/gap/detect.py`, `reconciler/tests/test_gap_detect.py`

Implement `detect_gap(run_history, expected_interval, as_of)` returning the gap window when a reconciliation, export or health-report cycle was missed, and `replay_expiries(window)` — §53.7 bullet 1: *"Replay expiries that should have fired during the gap — assignment `end_date`s, temporary access, exception expiries — and revoke or revert anything now overdue."* Then re-run all standing checks and confirm clean results, **including the seeded canary** (bullet 3).

Recording the gap as a Level 5 incident (bullet 4) is emitted here and routed by Lane 5.

**Acceptance** — all true:
1. A missed cycle produces a gap window with explicit start and end.
2. Every expiry falling inside the window is replayed; none is skipped as "already past".
3. The re-run confirmation fails if the canary is missing (L3-P1-17).

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p8-01-gap-detect

# Create reconciler/gap/__init__.py, gap/detect.py, tests/test_gap_detect.py

git add reconciler/gap/__init__.py reconciler/gap/detect.py reconciler/tests/test_gap_detect.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P8-01: gap detector and expiry replay"
git push -u origin lane/3/p8-01-gap-detect
gh pr create --title "L3-P8-01: gap detector and expiry replay" --base integration --body "Closes L3-P8-01"
```

**SELF-VERIFY**

```bash
python -m pytest reconciler/tests/test_gap_detect.py -q
```

Expected output, exactly:

```
7 passed
```

**STOP** — none beyond the standing rule of §0.6.

---

### L3-P8-02 — Gap diff-audit of the gap window

**Phase** 8 · **Size** L · **Deps** L3-P8-01 · **Spec** §53.7 bullet 2 (*"Diff-audit every access grant, merge and production approval made during the gap window against declared state, treating the gap window as unverified rather than presumed clean"*)

**Files (create):** `reconciler/gap/audit.py`, `reconciler/tests/test_gap_audit.py`

Implement `diff_audit(window, declared, actual)` enumerating every access grant, merge and production approval inside the window and comparing each against declared state. The default posture is **unverified**, not clean: an item the audit cannot evidence is reported as unverified, never as passing.

**Acceptance** — all true:
1. All three classes — access grants, merges, production approvals — are audited.
2. An item with no evidence is reported `unverified`, and a test asserts it is never reported `clean`.
3. The audit produces a list, not a boolean: a gap window that "looks fine" still enumerates what it checked.

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p8-02-gap-audit

# Create reconciler/gap/audit.py, tests/test_gap_audit.py

git add reconciler/gap/audit.py reconciler/tests/test_gap_audit.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P8-02: gap diff-audit of the gap window"
git push -u origin lane/3/p8-02-gap-audit
gh pr create --title "L3-P8-02: gap diff-audit of the gap window" --base integration --body "Closes L3-P8-02"
```

**SELF-VERIFY**

```bash
python -m pytest reconciler/tests/test_gap_audit.py -q
```

Expected output, exactly:

```
8 passed
```

**STOP** — none beyond the standing rule of §0.6.

---

### L3-P8-03 — `gap-window` marking

**Phase** 8 · **Size** M · **Deps** L3-P8-01 · **Spec** §53.7 bullet 5 (*"Every record produced during the gap window carries the `gap-window` mark until re-verified; a gap-window record is not evidence for any gate until re-verification clears the mark"*)

**Files (create):** `reconciler/gap/marking.py`, `reconciler/tests/test_gap_marking.py`

Implement `mark(records, window)` setting `gap_window=True` on every record produced inside the window, `clear(record, verifier, at)` clearing it only on explicit re-verification, and `is_gate_evidence(record)` returning `False` while the mark stands.

**Acceptance** — all true:
1. Every record inside the window is marked.
2. `is_gate_evidence()` returns `False` for a marked record, whatever its content.
3. The mark clears only through explicit re-verification, never by time passing.

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p8-03-gap-marking

# Create reconciler/gap/marking.py, tests/test_gap_marking.py

git add reconciler/gap/marking.py reconciler/tests/test_gap_marking.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P8-03: gap-window marking"
git push -u origin lane/3/p8-03-gap-marking
gh pr create --title "L3-P8-03: gap-window marking" --base integration --body "Closes L3-P8-03"
```

**SELF-VERIFY**

```bash
python -m pytest reconciler/tests/test_gap_marking.py -q
```

Expected output, exactly:

```
6 passed
```

**STOP** — if the mark is made to expire on a timer, stop: §53.7 clears it by re-verification only. File the blocker.

---

### L3-P8-04 — Wrong-repair freeze and revert branch

**Phase** 8 · **Size** L · **Deps** L3-P6-08 · **Spec** §53.7 *"When the loop ran wrong"* (verbatim); §53.2 Level 5; §28.1

**Files (create):** `reconciler/gap/wrong_repair.py`, `reconciler/tests/test_wrong_repair.py`

§53.7, transcribed: *"A repair class discovered to have written incorrect state is a Level 5 escalation in its own right … freeze that repair class, enumerate its repairs in the affected window from the repair records of Section 26.4, revert or human-confirm each against the compensating action its change plan was required to name and test (Section 28.1), and mark every record produced in the window `gap-window` until re-verified."*

Implement `on_wrong_repair(repair_class, window)` performing exactly those four actions in that order: **freeze** (set `enabled=False` in the enablement registry and refuse re-enable without a decision record), **enumerate** from the L3-P6-08 repair records, **revert or human-confirm** each against its recorded `compensating_action`, **mark** the window per L3-P8-03.

**Acceptance** — all true:
1. Freezing sets the class disabled and blocks re-enable without a decision record.
2. Enumeration reads the repair records, not the live state — the live state is what is suspect.
3. A repair record lacking `compensating_action` halts the revert and escalates, rather than guessing a reversal.

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p8-04-wrong-repair

# Create reconciler/gap/wrong_repair.py, tests/test_wrong_repair.py

git add reconciler/gap/wrong_repair.py reconciler/tests/test_wrong_repair.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P8-04: wrong-repair freeze and revert branch"
git push -u origin lane/3/p8-04-wrong-repair
gh pr create --title "L3-P8-04: wrong-repair freeze and revert branch" --base integration --body "Closes L3-P8-04"
```

**SELF-VERIFY**

```bash
python -m pytest reconciler/tests/test_wrong_repair.py -q && python -c "
from reconciler.gap.wrong_repair import ACTIONS
print(' '.join(ACTIONS))"
```

Expected output, exactly:

```
9 passed
freeze enumerate revert_or_confirm mark_gap_window
```

**STOP** — if a revert cannot be derived because no compensating action was recorded, stop and escalate at Level 5. §53.7: *"A loop that completed is not thereby a loop that was right."* File the blocker.

---

### L3-P8-05 — Lane acceptance-matrix runner

**Phase** 8 · **Size** M · **Deps** every task above · **Spec** §100 (the eleven acceptance tests this lane owns)

**Files (create):** `reconciler/acceptance/__init__.py`, `reconciler/acceptance/run_matrix.py`, `reconciler/tests/test_acceptance_matrix.py`

Implement a runner executing, against `fixture-a`, exactly the eleven Section 100 tests Lane 3 is responsible for, each mapped to the task that implements it:

| AT | Test (§100) | Implemented by |
| --- | --- | --- |
| AT-002 | Add a person — *"Reconciliation grants access … No workflow, architecture or dashboard change"* | L3-P4-09 |
| AT-008 | Temporary specialist joins — *"reconciliation revokes on the end date without human action"* | L3-P1-09, L3-P6-06, L3-P7-05 |
| AT-017 | A person leaves — *"Reconciliation revokes access; orphan detection surfaces every unowned responsibility; blocking orphans cannot be dismissed unresolved"* | L3-P7-02, L3-P2-06 |
| AT-018 | A temporary assignment expires — *"Reconciliation removes it without human action"* | L3-P6-06 |
| AT-032 | Self-observability — *"detects and reports a failure in its own reconciliation"* | L3-P1-20, L3-P5-05 |
| AT-033 | No auto-loosening — *"raises it for human review and does not relax it"* | L3-P6-01, L3-P6-05 |
| AT-036 | A temporary access exception expires — *"with no human action"* | L3-P6-06 |
| AT-037 | A failed exception is visible — *"becomes Blocking drift on its expiry date"* | L3-P6-06 |
| AT-102 | The seeded reconciliation canary — *"A run reporting zero findings … is a failed run"* | L3-P1-17 |
| AT-110 | The reconciler credential is provably bounded — six attempts | L3-P5-06 |
| AT-001 | Add product 21 — *"No dashboard, workflow or script contains a product list"* | L3-P4-07 |

Output: one line per test, `AT <id> result=<pass|fail>`, then `MATRIX passed=<int> total=11`.

**Acceptance** — all true:
1. All eleven run and pass against `fixture-a`.
2. Each row names the task implementing it; an unmapped AT id fails the runner.
3. The runner touches no live GitHub organisation.

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p8-05-acceptance-matrix

# Create reconciler/acceptance/__init__.py, acceptance/run_matrix.py, tests/test_acceptance_matrix.py

git add reconciler/acceptance/__init__.py reconciler/acceptance/run_matrix.py reconciler/tests/test_acceptance_matrix.py
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P8-05: lane acceptance-matrix runner"
git push -u origin lane/3/p8-05-acceptance-matrix
gh pr create --title "L3-P8-05: lane acceptance-matrix runner" --base integration --body "Closes L3-P8-05"
```

**SELF-VERIFY**

```bash
python -m reconciler.acceptance.run_matrix --summary | tail -1
```

Expected output, exactly:

```
MATRIX passed=11 total=11
```

**STOP** — if any AT fails, do **not** adjust the test to match the code. Find the task that owns that AT in the table above, reopen it, and file the blocker naming both the AT and the task id.

---

### L3-P8-06 — Lane handoff manifest

**Phase** 8 · **Size** S · **Deps** L3-P8-05 · **Spec** §0.4 above; `PARTITION.md` rules 2 and 4

**Files (create):** `reconciler/HANDOFF.md`, `reconciler/scripts/check-handoff.sh`

Write `reconciler/HANDOFF.md` stating, for each of the three consumers, what Lane 3 hands over and what it does **not** build:

| Consumer | Lane 3 hands over | Lane 3 does not build |
| --- | --- | --- |
| **L5** (`ops-vm/**`) | `python -m reconciler.cli run --live` as the scheduled entry point, its exit-code contract (§0.5), its expected source host and run-count ceiling (L3-P5-07) | the systemd timer or any ops-VM configuration |
| **L2** (`.github/workflows/**`) | `python -m validators.drift.verifier --live` as the scheduled entry point, and the requirement that it run under `DRIFT_VERIFIER_TOKEN`, a credential distinct from the reconciler's (§53.1) | the workflow YAML, or the surface it writes its result to |
| **L4** (`records/**`, `schemas/records/**`) | run records, drift findings and repair records as contract-shaped objects, handed over for writing | any write to `records/**` or `events/**` — AT-110 attempt 5 forbids it |

`check-handoff.sh` asserts the file exists, names all three consumers, and that no Lane 3 module writes to `records/`, `events/`, `.github/workflows/` or `ops-vm/`.

**Acceptance** — all true:
1. All three consumers are named with their entry point and their boundary.
2. The script finds zero writes from Lane 3 code into any foreign path.
3. `reconciler/scripts/check-ownership.sh` still passes on the final branch.

**Commands**

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

git fetch origin
git checkout integration
git checkout -b lane/3/p8-06-handoff

# Create reconciler/HANDOFF.md, scripts/check-handoff.sh

git add reconciler/HANDOFF.md reconciler/scripts/check-handoff.sh
bash lane-guard.sh && echo "LG OK"
git commit -m "L3-P8-06: lane handoff manifest"
git push -u origin lane/3/p8-06-handoff
gh pr create --title "L3-P8-06: lane handoff manifest" --base integration --body "Closes L3-P8-06"
```

**SELF-VERIFY**

```bash
bash reconciler/scripts/check-handoff.sh && bash reconciler/scripts/check-ownership.sh
```

Expected output, exactly:

```
HANDOFF OK consumers=3 foreign-writes=0
OWNERSHIP OK
```

**STOP** — if any consumer's entry point does not yet exist, stop: it means a task above is unmerged. Do not write a placeholder. File the blocker naming the missing task id.

---

## 12. Pending mutation script deliverables

The tasks in this section create the mutation scripts listed as `MUTATION-NEEDED` in `protocol/03-invariant-tests.md` §8.5 and §9.3. Each script mutates the fixture so the named negative test flips from PASS to FAIL, proving the test is not vacuous. Safety rule SR-2 (§1): mutations happen only in disposable fixture repositories — never in a live reconciler tree.

### L3-IT537-N1 — Create IT-537-N1.mutation.sh

**Size:** S  **Depends on:** L3-P6 repair-class tasks  **Branch slug:** `lane/3/it537-n1-mutation`

**Creates:** `reconciler/invariant-tests/mutations/IT-537-N1.mutation.sh`

**Spec:** `protocol/03-invariant-tests.md` §8.5 (`# MUTATION-NEEDED: create IT-537-N1.mutation.sh`). The mutation suppresses the freeze signal emitted by a repair class when it detects it has written incorrect state. The class continues running rather than halting and raising a Level 5 escalation. Under the mutation IT-537-N1 must flip from PASS to FAIL.

**Commands**

```bash
set -euo pipefail
: "${CONTROL_PLANE_ROOT:?STOP: CONTROL_PLANE_ROOT is not exported}"
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/3/it537-n1-mutation
mkdir -p reconciler/invariant-tests/mutations

cat > reconciler/invariant-tests/mutations/IT-537-N1.mutation.sh << 'EOF'
#!/usr/bin/env bash
# Mutation: suppress the freeze signal in the repair class so that when a
# repair class writes incorrect state it continues running instead of halting
# and raising a Level 5 escalation.
# Expected result: IT-537-N1 flips from PASS to FAIL.
# Spec: protocol/03-invariant-tests.md §8.5 (MUTATION-NEEDED IT-537-N1).
set -euo pipefail
REPAIR_CLASS="${FIXTURE_REPO_ROOT:?}/reconciler/repair/repair-class.sh"
# No-op the freeze signal emission so the class does not halt on bad state.
sed -i 's/\(emit_freeze_signal\|raise_level_5\|freeze_class\)/: # MUTATED-SUPPRESSED/g' \
  "$REPAIR_CLASS"
echo "IT-537-N1 mutation applied: freeze signal suppressed in repair class at $REPAIR_CLASS"
EOF
chmod +x reconciler/invariant-tests/mutations/IT-537-N1.mutation.sh
git add reconciler/invariant-tests/mutations/IT-537-N1.mutation.sh
git commit -m "L3-IT537-N1: create IT-537-N1.mutation.sh (suppress freeze signal in repair class)"
bash lane-guard.sh && echo "LG OK"
```

**SELF-VERIFY**

```bash
test -f reconciler/invariant-tests/mutations/IT-537-N1.mutation.sh && \
test -x reconciler/invariant-tests/mutations/IT-537-N1.mutation.sh && \
echo "IT-537-N1.mutation.sh present and executable"
```

Expected output, exactly: `IT-537-N1.mutation.sh present and executable`

**STOP rule:** If applying the mutation does not cause IT-537-N1 to exit non-zero, the test is vacuous. File a blocker titled `VACUOUS-TEST IT-537-N1` and stop the lane immediately.

---

### L3-IT537-N3 — Create IT-537-N3.mutation.sh

**Size:** S  **Depends on:** L3-P6 repair-class tasks  **Branch slug:** `lane/3/it537-n3-mutation`

**Creates:** `reconciler/invariant-tests/mutations/IT-537-N3.mutation.sh`

**Spec:** `protocol/03-invariant-tests.md` §8.5 (`# MUTATION-NEEDED: create IT-537-N3.mutation.sh`). The mutation makes the gap-close procedure skip re-running expiries whose `end_date` fell inside the gap window, so an expired assignment remains provisioned. Under the mutation IT-537-N3 must flip from PASS to FAIL.

**Commands**

```bash
set -euo pipefail
: "${CONTROL_PLANE_ROOT:?STOP: CONTROL_PLANE_ROOT is not exported}"
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/3/it537-n3-mutation
mkdir -p reconciler/invariant-tests/mutations

cat > reconciler/invariant-tests/mutations/IT-537-N3.mutation.sh << 'EOF'
#!/usr/bin/env bash
# Mutation: on gap close, skip re-running expiries whose end_date fell inside
# the gap window. Assignments that expired during the gap remain provisioned
# instead of being revoked on gap close.
# Expected result: IT-537-N3 flips from PASS to FAIL.
# Spec: protocol/03-invariant-tests.md §8.5 (MUTATION-NEEDED IT-537-N3).
set -euo pipefail
GAP_CLOSE="${FIXTURE_REPO_ROOT:?}/reconciler/gap-close.sh"
# Remove the expiry-replay loop that processes end_dates inside the gap window.
sed -i '/replay.*gap.*expir\|expir.*gap.*replay\|gap_window.*end_date\|end_date.*gap_window/Id' \
  "$GAP_CLOSE"
echo "IT-537-N3 mutation applied: gap-window expiry replay skipped in gap-close at $GAP_CLOSE"
EOF
chmod +x reconciler/invariant-tests/mutations/IT-537-N3.mutation.sh
git add reconciler/invariant-tests/mutations/IT-537-N3.mutation.sh
git commit -m "L3-IT537-N3: create IT-537-N3.mutation.sh (skip expiry replay in gap-close)"
bash lane-guard.sh && echo "LG OK"
```

**SELF-VERIFY**

```bash
test -f reconciler/invariant-tests/mutations/IT-537-N3.mutation.sh && \
test -x reconciler/invariant-tests/mutations/IT-537-N3.mutation.sh && \
echo "IT-537-N3.mutation.sh present and executable"
```

Expected output, exactly: `IT-537-N3.mutation.sh present and executable`

**STOP rule:** If applying the mutation does not cause IT-537-N3 to exit non-zero, the test is vacuous. File a blocker titled `VACUOUS-TEST IT-537-N3` and stop the lane immediately.

---

### L3-IT111-R-N2 — Create IT-111-R-N2.mutation.sh

**Size:** S  **Depends on:** none within this lane (IT-111-R invariant test owned by L4; mutation script is an L3 lane deliverable per `protocol/03-invariant-tests.md` §9.3)  **Branch slug:** `lane/3/it111-r-n2-mutation`

**Creates:** `reconciler/invariant-tests/mutations/IT-111-R-N2.mutation.sh`

**Spec:** `protocol/03-invariant-tests.md` §9.3 (`# MUTATION-NEEDED: create IT-111-R-N2.mutation.sh`). The mutation allows a free-text `reproduction_notes` field in the fixture records schema so an incident record carrying a non-synthetic reproduction fixture passes schema validation. Under the mutation IT-111-R-N2 must flip from PASS to FAIL.

**Commands**

```bash
set -euo pipefail
: "${CONTROL_PLANE_ROOT:?STOP: CONTROL_PLANE_ROOT is not exported}"
cd "$CONTROL_PLANE_ROOT"
git fetch origin && git checkout integration && git pull --ff-only origin integration
git checkout -b lane/3/it111-r-n2-mutation
mkdir -p reconciler/invariant-tests/mutations

cat > reconciler/invariant-tests/mutations/IT-111-R-N2.mutation.sh << 'EOF'
#!/usr/bin/env bash
# Mutation: allow a free-text 'reproduction_notes' field in the fixture records
# schema so an incident record with a non-synthetic reproduction fixture passes
# schema validation (violating §38.3).
# Expected result: IT-111-R-N2 flips from PASS to FAIL.
# Spec: protocol/03-invariant-tests.md §9.3 (MUTATION-NEEDED IT-111-R-N2).
set -euo pipefail
SCHEMA="${FIXTURE_REPO_ROOT:?}/tools/records/schema/incident-record.yaml"
python3 - "$SCHEMA" << 'PY'
import sys, yaml
schema = yaml.safe_load(open(sys.argv[1]))
# Allow the prohibited free-text field by adding it to the schema properties
# and removing the additionalProperties: false guard that would block it.
schema.setdefault('properties', {})['reproduction_notes'] = {'type': 'string'}
schema.pop('additionalProperties', None)
yaml.dump(schema, open(sys.argv[1], 'w'), allow_unicode=True)
print('reproduction_notes added to schema')
PY
echo "IT-111-R-N2 mutation applied: free-text reproduction_notes field allowed in incident record schema at $SCHEMA"
EOF
chmod +x reconciler/invariant-tests/mutations/IT-111-R-N2.mutation.sh
git add reconciler/invariant-tests/mutations/IT-111-R-N2.mutation.sh
git commit -m "L3-IT111-R-N2: create IT-111-R-N2.mutation.sh (free-text field in incident record schema)"
bash lane-guard.sh && echo "LG OK"
```

**SELF-VERIFY**

```bash
test -f reconciler/invariant-tests/mutations/IT-111-R-N2.mutation.sh && \
test -x reconciler/invariant-tests/mutations/IT-111-R-N2.mutation.sh && \
echo "IT-111-R-N2.mutation.sh present and executable"
```

Expected output, exactly: `IT-111-R-N2.mutation.sh present and executable`

**STOP rule:** If applying the mutation does not cause IT-111-R-N2 to exit non-zero, the test is vacuous. File a blocker titled `VACUOUS-TEST IT-111-R-N2` and stop the lane immediately.

---

## 13. Closing notes for the executor

1. **Order is not advisory.** Phase 6 exists after Phase 5 because §99.6 risk 6 requires detect-only first and repair classes enabled one at a time. Reordering to "get repairs working sooner" is the exact failure mode the risk names.
2. **Every number in this file is derived from `fixture-a` (L3-P0-04).** If a SELF-VERIFY number is wrong, the fixture changed. Restore the fixture; do not edit the expectation.
3. **Five decisions belong to L0**, not to you: L3-D1 (runtime), L3-D2 (contract paths), L3-D3 (credential form), L3-D4 (orphan severity mapping), and every reclassification under §53.5. If a task seems to require a sixth, that is a STOP.
4. **You never write outside `reconciler/**`, `tools/provision/**`, `validators/drift/**`.** Not once, not for a one-line fix, not for a test fixture.
5. **The reconciler is the highest-privilege identity in the system** (§99.6 risk 6). When a shortcut and a safety rule disagree in this lane, the safety rule wins and the shortcut becomes a blocker issue.
