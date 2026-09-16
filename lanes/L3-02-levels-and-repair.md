> **[SUPERSEDED — FD-B1-L3 2026-09-02]**
> This file has been superseded by L3-06-tasks.md. Do not execute tasks from this file.
> Authoritative plan: Code/implementation/lanes/L3-06-tasks.md

# L3 — PHASE 2: THE FIVE RESPONSE LEVELS AND AUTO-REPAIR

> **REFERENCE ONLY** — FD-098 (2026-09-09): Task bodies superseded by L3-06-tasks.md. This file is a design-note reference. Do not execute task bodies from this file.

**Lane:** L3 Reconciler & Provisioning (subsystems C and D of spec §99.2)
**Branch prefix:** `lane/3/*` (PARTITION.md, "The five build lanes")
**Paths this lane owns exclusively:** `reconciler/**`, `tools/provision/**`, `validators/drift/**`
**Repository:** `control-plane`
**Phase:** 2 of the L3 sequence. Phase 1 (detect-only reconciliation) must be merged to `integration` before any task here starts.

---

## 0. Why this phase is written the way it is

Spec §99.6 risk 6 names this code exactly:

> Reconciliation auto-repair as the most dangerous code — a write-scope, org-admin automation whose bug loosens security or locks everyone out; the reconciler is the highest-privilege identity in the system — **Mitigation:** Detect-only first; repair classes enabled one at a time; stricter-only rule enforced in code and tested; the reconciler's own credential in the top secrets tier with its compromise treated as a security incident

Spec §99.4 item 6 says the same thing from the delivery side: *"Auto-repair is deferred until detection has run clean for weeks; auto-repair is the riskiest code in the system, and its stricter-only rule is enforced in code and tested."* Spec §98.3 places Level 3 in early hardening, after Phase 3's detect-and-block reconciliation.

Three consequences bind every task below:

1. **The stricter-only comparator is built and tested before any repair executor exists** (T05 precedes T08). Invariant 81: *"Auto-repair may only move the system toward the declared, stricter state."*
2. **Every repair class ships disabled.** Enablement is a separate, one-class-per-cycle operation (T07).
3. **The reconciler's own write scope is narrowed to `derived/**` (D93)** so that a machine write to a registry is *detectable Blocking drift rather than an in-scope write*.

---

## 1. Spec anchors used by this phase — all verified present

| Anchor | Where | What it fixes for this phase |
| --- | --- | --- |
| §53.1 | Declared versus actual; comparison rows; blocking rows are P0 | Which comparisons produce findings |
| §53.2 | The five reconciliation levels (Detect / Warn / Auto-repair / Block / Escalate) with the exact "Applies to" scope of each | T02–T13 |
| §53.3 | The auto-repair rule (stricter-only, never loosens, never touches production runtime config, data or secrets) | T05, T08 |
| §53.4 | Drift classes Green / Amber / Red / Blocking, response times, actor, blocks-work; the three retirement mappings | T02 |
| §53.7 | The control-loop gap procedure; "When the loop ran wrong" — repair-class freeze | T13 |
| §26.4 | The registry-change lane; Level-3 repairs "write directly under the reconciler credential, logged as repair records"; registry edits stage to the canary set first | T08, T09 |
| §40.1 | Five secret tiers; the reconciler's check-run scope; the behavioural envelope | T09, T10, T11, T12 |
| §28.1 | Reversibility classification and the named, tested compensating action | T08, T13 |
| §12.2 | The 16 orphan types with severities | T11 |
| §99.6 risk 6 | Detect-only first; one repair class at a time; stricter-only in code and tested | T05, T06, T07 |
| D92 | The reconciler holds check-run write and posts a named required check on every affected repository, failing while a Blocking finding is open against that product | T11, T12 |
| D93 | The reconciler's own write scope is narrowed to generated `derived/**` files the registries reference | T09 |
| D89 | No machine identity is a bypass actor on the control-plane repository | T09, T10 |
| D107 | The reconciler anchors the records-repository head SHA into the control-plane repository each run; a non-descendant head is Blocking drift at Level 5 | T13 (consumer only) |
| Invariant 81 | "Auto-repair may only move the system toward the declared, stricter state." | T05 |
| Invariant 44 | "Declared state is reconciled against actual platform state, and silent drift is not permitted." | T03 |
| Invariant 57 | "Departures trigger orphan detection, and blocking orphans cannot be dismissed unresolved." | T11 |
| AT-033 | "No auto-loosening — Reconciliation presented with a stricter-than-declared production control raises it for human review and does not relax it" | T05 |
| AT-110 | "The reconciler credential is provably bounded" — six attempts, all six fail, then a normal run still completes | T10 |
| AT-102 | The seeded reconciliation canary — a run reporting zero findings is a **failed** run | T14 (regression guard only; the canary itself is Phase 1) |
| AT-017 / AT-018 / AT-036 / AT-037 | Departure orphans; expiring assignments; expiring access exceptions; an exception that cannot be auto-revoked becomes Blocking drift | T08, T11 |
| SIG-03 | Permission drift — Red; **Blocking if it weakens a security control** | T11 |
| SIG-13 | Failed reconciliations — Red | T13 |
| SIG-05 | Orphan risk — Blocking | T11 |
| SIG-17 | Restore-test currency — Amber approaching, **Blocking past** | T11 |

---

## 2. DECISION REQUIRED — hand to L0 before the named tasks start

These four values are not derivable from the spec by this lane. They are cross-lane contract values (L2's workflows and the product repositories consume two of them), so under PARTITION rule 2 they are authored by L0 into `contracts/**` and this lane codes against them. **There is no default and no placeholder. A task blocked on one of these STOPs.**

### DECISION REQUIRED — DEC-L3-02-01: Red-class drift has no declared response level

- **What is missing:** §53.4 defines the Red class (material risk; 2 business days; Owner plus Team Lead; *"No, but visible on the Founder view"*). §53.2's five levels declare an "Applies to" scope for Green-class (Level 1), Amber-class (Level 2), and Blocking-class (Level 4). No level's "Applies to" names Red-class drift.
- **Why this lane cannot decide:** choosing between "Red behaves as Level 2 plus Founder-view surfacing" and "Red is its own response level" changes notification routing, the drift budget arithmetic of §53.4, and the Founder view (§93) which L3 does not own.
- **Requested output:** `contracts/reconciler/level-map.yaml`, key `red_class_level`, one of the five level identifiers declared in §53.2, plus the surfacing target.
- **Blocks:** T02, T04, T14.

### ~~DECISION REQUIRED~~ RESOLVED — DEC-L3-02-02: the literal name of the blocking check run (D92)

> **RESOLVED: check-run name = `control-plane/blocking-drift` per spec §11.3 line 867**
> The spec of record (MasterSpec v4.0 §11.3, line 867) names this string explicitly: *"a required status check named `control-plane/blocking-drift`"*. This decision is retired. Tasks T11, T12, and T14 use `control-plane/blocking-drift` directly without waiting for a contract file. The residual question — at which phase the context is added to the required-status-check list in branch protection — is L5's and does not block L3 tasks.

- ~~**What is missing:** D92 says *"posts a named required check on every affected repository"* and §40.1 says the check-run scope is *"used for exactly one named check"* and that *"a check run published under that name by any identity other than the reconciler is Blocking drift."* The spec never writes the name string.~~
- ~~**Why this lane cannot decide:** the same string must be configured as a required status check in branch protection (L5 `access/**`) and referenced by the reusable workflow library (L2 `.github/workflows/**`). A name chosen inside L3 would be a shared mutable value invented in one lane, which PARTITION rule 4 forbids.~~
- ~~**Requested output:** `contracts/l3-reconciler.yaml`, key `blocking_check_name` (exact string, GitHub check-run name), plus `expected_app_slug` (the reconciler App identity that alone may publish it). Note: path is at contracts root — FD-013 did not freeze a `reconciler/` subdirectory.~~
- ~~**Blocks:** T11, T12, T14.~~ **UNBLOCKED** — use `control-plane/blocking-drift` per spec §11.3.

### DECISION REQUIRED — DEC-L3-02-03: the record store path and schema id for run records and repair records

- **What is missing:** §53.1 requires *"Every reconciliation run writes its result, and a clean run is recorded as clean"* and §26.4 requires Level-3 repairs to be *"logged as repair records."* The canonical record-store table of §97.2 lists no reconciliation-run store and no repair store.
- **Why this lane cannot decide:** `records/**` and `schemas/records/**` are owned exclusively by L4 (PARTITION). L3 emits into that store and must not name it.
- **Requested output:** `contracts/reconciler/records.yaml` with keys `run_record_path`, `run_record_schema_id`, `repair_record_path`, `repair_record_schema_id`, and the `record_schema_version` value to stamp (per §97.2, "every record carries `record_schema_version`").
- **Blocks:** T03, T04, T08, T13.

### DECISION REQUIRED — DEC-L3-02-04: does §53.1's "auto-repair where safe" row create a sixth repair class?

- **What is missing:** §53.2's Level 3 cell enumerates the permitted repairs as a closed list of five. §53.1 carries a separate row — *"`product.yaml` lifecycle | Renovate, monitoring and CI configuration | Auto-repair where safe; alert otherwise"* — which is not one of the five.
- **Why this lane cannot decide:** admitting a sixth class widens the highest-privilege automation in the system; §99.6 risk 6 makes that an explicit governance act, not an implementation reading.
- **Requested output:** `contracts/reconciler/repair-classes.yaml`, key `lifecycle_config_class`, either `not-a-repair-class` (the §53.1 row raises Level 2 and stops) or a sixth class id with its own stricter-only predicate.
- **Blocks:** T06.

---

## 3. Standing rules for the executor — read once, apply to every task

**R1. Additive-only.** PARTITION rule 5: *"Prefer new files over editing existing ones."* Every file named in this phase is a **new** file. If a task tells you to create a file that already exists, do **not** edit it — STOP and file the blocker. This is how the phase stays free of collisions with Phase 1.

**R2. Owned paths only.** You may create or edit files only under `reconciler/`, `tools/provision/`, `validators/drift/`. Every task's SELF-VERIFY contains the lane-guard command; it must print `0`.

**R3. No judgment.** If a task's inputs are absent, ambiguous, or contradict what you find in the repository, STOP. Do not choose. Do not invent a value. Do not "make it work for now".

**R4. Runtime inherited from Phase 1.** This phase adds Python modules to the package Phase 1 established. T01 verifies that. If T01's verification fails, no other task in this phase may start.

**R5. One branch per task**, named `lane/3/02-<taskid-lowercase>-<slug>`, rebased on `origin/integration` before the PR, per PARTITION "Branch & merge model".

**R6. Blocker-issue template.** Every STOP uses this exact command shape, with the task's own trigger substituted:

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
cat > /tmp/blocker-body.md <<'EOF'
## Blocked task
<TASK_ID> — <TASK TITLE>

## Lane
L3 Reconciler & Provisioning — Phase 2 (levels and auto-repair)
Plan file: Code/implementation/lanes/L3-02-levels-and-repair.md

## Trigger that fired
<paste the exact STOP trigger text from the task>

## Observed
<paste the exact command you ran and its exact output>

## Expected per plan
<paste the expected output from the task's SELF-VERIFY block>

## Spec references
<paste the task's "Spec basis" row verbatim>

## What I need to proceed
A decision or a value from L0. I have made no change and chosen no value.

## Branch state
Branch: <branch name>
HEAD: <git rev-parse HEAD>
Files changed so far: <git diff --name-only origin/integration...HEAD>
EOF
gh issue create \
  --title "BLOCKER L3-02 <TASK_ID>: <one-line trigger>" \
  --label "blocker,lane-3,phase-2" \
  --body-file /tmp/blocker-body.md
```

Then stop working. Do not open the PR. Do not proceed to the next task.

**R7. Deterministic verification idiom.** Test counts are asserted with this idiom so the expected output is exact and time-independent:

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
python -m pytest <path> -q 2>&1 | grep -oE '^[0-9]+ passed'
```

---

## 4. Task manifest

| Task id | Title | Size | Depends on |
| --- | --- | --- | --- |
| L3-02-01 | Phase entry gate and Phase-2 package skeleton | S | — (phase entry) |
| L3-02-02 | Drift class and response-level tables as data | M | T01, DEC-L3-02-01 |
| L3-02-03 | Level 1 — Detect | M | T02, DEC-L3-02-03 |
| L3-02-04 | Level 2 — Warn | M | T02, T03, DEC-L3-02-01, DEC-L3-02-03 |
| L3-02-05 | The stricter-only comparator (§53.3, inv. 81, AT-033) | L | T02 |
| L3-02-06 | The permitted repair-class registry — closed list of five | M | T05, DEC-L3-02-04 |
| L3-02-07 | Enable-one-class-at-a-time discipline (§99.6 risk 6) | M | T06 |
| L3-02-08 | Level 3 — Auto-repair executor | L | T05, T06, T07, DEC-L3-02-03 |
| L3-02-09 | Reconciler write scope narrowed to `derived/**` (D93) | M | T02 |
| L3-02-10 | AT-110 credential-boundedness harness | M | T09 |
| L3-02-11 | Level 4 — Block, via the blocking check run (D92) | L | T02, T09, DEC-L3-02-02 |
| L3-02-12 | Check-run identity guard (§40.1) | S | T11, DEC-L3-02-02 |
| L3-02-13 | Level 5 — Escalate, and the repair-class freeze (§53.7) | M | T08, T11, DEC-L3-02-03 |
| L3-02-14 | Level-ordering integration test and phase exit gate | M | T03, T04, T08, T11, T12, T13 |

Dependency shape: `T01 → T02 → {T03 → T04, T05 → T06 → T07 → T08, T09 → {T10, T11 → T12}} → T13 → T14`.

---

## L3-02-01 — Phase entry gate and Phase-2 package skeleton

**Size:** S **Depends on:** none (phase entry)
**Spec basis:** PARTITION.md "Branch & merge model" and rule 5; §99.4 item 6 (auto-repair follows detection).

### Files created (all owned by L3)

- `reconciler/levels/__init__.py`
- `reconciler/repair/__init__.py`
- `reconciler/checkrun/__init__.py`
- `reconciler/credential/__init__.py`
- `reconciler/levels/tests/__init__.py`
- `reconciler/repair/tests/__init__.py`
- `reconciler/credential/tests/__init__.py`
- `validators/drift/tests/__init__.py`
- `reconciler/PHASE2-ENTRY.md`

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
git fetch origin
git checkout integration
git pull --ff-only
git checkout -b lane/3/02-t01-entry-gate
```

Entry gate — Phase 1 must already be present. Run all four checks and read the output before creating anything:

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
test -d reconciler && echo "GATE-1 reconciler-dir OK" || echo "GATE-1 FAIL"
test -d validators/drift && echo "GATE-2 drift-dir OK" || echo "GATE-2 FAIL"
test -f reconciler/pyproject.toml && echo "GATE-3 python-package OK" || echo "GATE-3 FAIL"
python -c "import sys; print('GATE-4 python OK' if sys.version_info[:2] >= (3,12) else 'GATE-4 FAIL')"
```

Contract gate — the four L0 decisions must be published:

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
for f in contracts/reconciler/level-map.yaml contracts/l3-reconciler.yaml contracts/reconciler/records.yaml contracts/reconciler/repair-classes.yaml; do
  test -f "$f" && echo "CONTRACT OK $f" || echo "CONTRACT MISSING $f"
done
```

Collision gate — no Phase-2 path may already exist:

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
for p in reconciler/levels reconciler/repair reconciler/checkrun reconciler/credential validators/drift/tests; do
  test -e "$p" && echo "COLLISION $p" || echo "CLEAR $p"
done
```

Create the skeleton:

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
mkdir -p reconciler/levels/tests reconciler/repair/tests reconciler/checkrun reconciler/credential/tests validators/drift/tests validators/drift/fixtures
for f in reconciler/levels/__init__.py reconciler/repair/__init__.py reconciler/checkrun/__init__.py reconciler/credential/__init__.py reconciler/levels/tests/__init__.py reconciler/repair/tests/__init__.py reconciler/credential/tests/__init__.py validators/drift/tests/__init__.py; do
  printf '' > "$f"
done
cat > reconciler/PHASE2-ENTRY.md <<'EOF'
# L3 Phase 2 entry record

Phase 2 (the five response levels and auto-repair) builds on the detect-only
reconciler delivered in L3 Phase 1.

Binding constraints carried into every module in this phase:

- Spec 53.3: a repair is permitted only when it moves the system toward the
  declared state AND the declared state is at least as restrictive as the
  actual state. Reconciliation never loosens a control automatically, never
  modifies production runtime configuration, never modifies data, and never
  rotates or writes secrets.
- Invariant 81: auto-repair may only move the system toward the declared,
  stricter state.
- Spec 99.6 risk 6: detect-only first; repair classes enabled one at a time;
  stricter-only rule enforced in code and tested.
- D93: the reconciler's own write scope is narrowed to generated derived/**
  files the registries reference.
- D92: Blocking-class drift holds a product repository closed through a named
  check run, not through a status check that last ran green.

Every repair class in reconciler/repair/classes.yaml ships with
enabled: false. Enabling one is a separate governed operation (L3-02-07).
EOF
git add reconciler/levels reconciler/repair reconciler/checkrun reconciler/credential validators/drift/tests reconciler/PHASE2-ENTRY.md
git commit -m "L3-02-01: Phase 2 package skeleton and entry record"
git rebase origin/integration
git push -u origin lane/3/02-t01-entry-gate
```

### Acceptance criteria

| # | Criterion | Proving command | Required output |
| --- | --- | --- | --- |
| A1 | All four entry gates pass | `cd "$(git rev-parse --show-toplevel)" && test -d reconciler && test -d validators/drift && test -f reconciler/pyproject.toml && python -c "import sys;assert sys.version_info[:2]>=(3,12)" && echo GATES-PASS` | `GATES-PASS` |
| A2 | All four contract files present | `cd "$(git rev-parse --show-toplevel)" && ls contracts/reconciler/level-map.yaml contracts/l3-reconciler.yaml contracts/reconciler/records.yaml contracts/reconciler/repair-classes.yaml \| wc -l` | `4` |
| A3 | Eight package markers exist | `cd "$(git rev-parse --show-toplevel)" && git ls-files 'reconciler/levels/__init__.py' 'reconciler/repair/__init__.py' 'reconciler/checkrun/__init__.py' 'reconciler/credential/__init__.py' 'reconciler/levels/tests/__init__.py' 'reconciler/repair/tests/__init__.py' 'reconciler/credential/tests/__init__.py' 'validators/drift/tests/__init__.py' \| wc -l` | `8` |
| A4 | No foreign path touched | see SELF-VERIFY | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler|tools/provision|validators/drift)/'
```

Expected output:

```
0
```

### STOP rule

STOP and file the R6 blocker if any of: any `GATE-n` line prints `FAIL`; any `CONTRACT MISSING` line appears; any `COLLISION` line appears; the lane-guard number is not `0`.
Do not create `pyproject.toml`. Do not author the missing contract files. Do not delete or edit a colliding path.

---

## L3-02-02 — Drift class and response-level tables as data

**Size:** M **Depends on:** T01, DEC-L3-02-01
**Spec basis:** §53.2 (the five levels, with each level's exact "Applies to" scope); §53.4 (the four drift classes with response time, actor, blocks-work, and the three retirement mappings: *dangerous* → Blocking, *correctable* → auto-repairable Level 3, *informational* → Level 1).

> **Red output is Level 2 (BLOCKER) and raises a Founder-view flag per FD-007.**

The tables are **data, not code**, because §53.4 binds: *"Class assignment lives in configuration and is reviewable; it is not decided ad hoc during an incident."*

### Files created

- `validators/drift/class_map.yaml`
- `validators/drift/levels.py`
- `validators/drift/tests/test_levels.py`

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
git fetch origin && git checkout integration && git pull --ff-only
git checkout -b lane/3/02-t02-class-map
cat > validators/drift/class_map.yaml <<'EOF'
# Drift classes and response levels, transcribed verbatim from the spec.
# Section 53.4: "There is exactly one drift severity scale, used everywhere."
# Section 53.4: "Class assignment lives in configuration and is reviewable;
# it is not decided ad hoc during an incident."
# DO NOT add, rename or reword a class or a level. Both tables are closed.
map_version: 1
spec_sections: ["53.2", "53.4"]

# Section 53.4 — the one drift severity scale
drift_classes:
  - id: green
    meaning: "Within tolerance; recorded only"
    response_time: "None"
    who_acts: "Nobody"
    blocks_work: false
  - id: amber
    meaning: "Real but non-urgent; scheduled remediation"
    response_time: "Next planning cycle, H2"
    who_acts: "Owner"
    blocks_work: false
  - id: red
    meaning: "Material risk to security, reliability or continuity"
    response_time: "Within 2 business days"
    who_acts: "Owner plus Team Lead"
    blocks_work: false
  - id: blocking
    meaning: "Unsafe to proceed"
    response_time: "Immediate"
    who_acts: "Team Lead or escalation role"
    blocks_work: true

# Section 53.2 — the five reconciliation levels
response_levels:
  - id: level_1_detect
    behaviour: "Record the finding with evidence and age. No notification."
    applies_to_class: green
    applies_to_text: "Green-class drift: display names, documentation links, non-blocking metadata"
  - id: level_2_warn
    behaviour: "Raise on the health report and notify the owner. No block."
    applies_to_class: amber
    applies_to_text: "Amber-class drift: stale contracts, stale flags, review concentration"
  - id: level_3_auto_repair
    behaviour: "Reconcile actual state back to declared state automatically, then record the repair."
    applies_to_class: null
    applies_to_text: "Safe, idempotent, reversible repairs only: Team membership sync from registries, CODEOWNERS regeneration, label and board field sync, re-applying declared branch protection, removing expired assignments and expired access"
  - id: level_4_block
    behaviour: "Fail CI or block the deployment path until resolved."
    applies_to_class: blocking
    applies_to_text: "Blocking-class drift: orphaned product, expired non-employee access still provisioned, restore test overdue, security control weakened, artifact digest mismatch, workflow-file change pushed by a machine identity"
  - id: level_5_escalate
    behaviour: "Create an incident and notify the escalation role, then the Founder if unresolved within its response time."
    applies_to_class: null
    applies_to_text: "Production environment drift, credential exposure, repeated failed auto-repair, a repair class discovered to have written incorrect state (53.7), the reconciliation job itself failing"

# Section 53.4 — "Older vocabulary is retired and maps onto this scale exactly
# once, here". These three are the only legacy aliases that resolve.
retired_vocabulary:
  dangerous: blocking
  correctable: level_3_auto_repair
  informational: level_1_detect

# The red-class response level is NOT stated by section 53.2. It is read at
# runtime from contracts/reconciler/level-map.yaml key red_class_level
# (DEC-L3-02-01). This file never hard-codes it.
red_class_level: from-contract
EOF
```

Now `validators/drift/levels.py`. It must expose exactly four callables and hold no policy of its own:

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
cat > validators/drift/levels.py <<'PYEOF'
"""Drift classes and response levels (spec 53.2, 53.4).

This module is a loader and a lookup. It contains no classification policy:
policy lives in validators/drift/class_map.yaml and, for the red class, in
contracts/reconciler/level-map.yaml (DEC-L3-02-01).
"""
from __future__ import annotations

import functools
import pathlib
from typing import Any

import yaml

_CLASS_MAP = pathlib.Path(__file__).with_name("class_map.yaml")
_LEVEL_CONTRACT = pathlib.Path("contracts/reconciler/level-map.yaml")

DRIFT_CLASSES = ("green", "amber", "red", "blocking")
RESPONSE_LEVELS = (
    "level_1_detect",
    "level_2_warn",
    "level_3_auto_repair",
    "level_4_block",
    "level_5_escalate",
)


class ClassMapError(RuntimeError):
    """Raised when the class map or the level contract is unusable."""


@functools.lru_cache(maxsize=1)
def load_class_map() -> dict[str, Any]:
    data = yaml.safe_load(_CLASS_MAP.read_text(encoding="utf-8"))
    ids = [c["id"] for c in data["drift_classes"]]
    if tuple(ids) != DRIFT_CLASSES:
        raise ClassMapError(f"drift_classes must be exactly {DRIFT_CLASSES}, got {tuple(ids)}")
    lids = [l["id"] for l in data["response_levels"]]
    if tuple(lids) != RESPONSE_LEVELS:
        raise ClassMapError(f"response_levels must be exactly {RESPONSE_LEVELS}, got {tuple(lids)}")
    return data


def blocks_work(drift_class: str) -> bool:
    """Section 53.4 'Blocks work' column. Only 'blocking' blocks work."""
    for entry in load_class_map()["drift_classes"]:
        if entry["id"] == drift_class:
            return bool(entry["blocks_work"])
    raise ClassMapError(f"unknown drift class: {drift_class}")


def resolve_legacy(term: str) -> str:
    """Section 53.4 retirement mapping. No other severity vocabulary exists."""
    mapping = load_class_map()["retired_vocabulary"]
    if term not in mapping:
        raise ClassMapError(f"no such retired term: {term}")
    return mapping[term]


def level_for_class(drift_class: str) -> str:
    """Return the response level for a drift class.

    green -> level_1_detect, amber -> level_2_warn, blocking -> level_4_block
    are stated by section 53.2's 'Applies to' column. 'red' is not stated
    there and is read from the L0 contract (DEC-L3-02-01).
    """
    if drift_class not in DRIFT_CLASSES:
        raise ClassMapError(f"unknown drift class: {drift_class}")
    if drift_class == "red":
        if not _LEVEL_CONTRACT.exists():
            raise ClassMapError(
                "DEC-L3-02-01 unresolved: contracts/reconciler/level-map.yaml absent; "
                "section 53.2 declares no response level for red-class drift"
            )
        contract = yaml.safe_load(_LEVEL_CONTRACT.read_text(encoding="utf-8"))
        value = contract.get("red_class_level")
        if value not in RESPONSE_LEVELS:
            raise ClassMapError(
                f"contracts/reconciler/level-map.yaml red_class_level must be one of "
                f"{RESPONSE_LEVELS}, got {value!r}"
            )
        return value
    for entry in load_class_map()["response_levels"]:
        if entry["applies_to_class"] == drift_class:
            return entry["id"]
    raise ClassMapError(f"no level declares applies_to_class={drift_class}")
PYEOF
```

Tests — nine cases, one per assertion the spec makes:

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
cat > validators/drift/tests/test_levels.py <<'PYEOF'
import pytest

from validators.drift import levels


def test_exactly_four_drift_classes():
    ids = [c["id"] for c in levels.load_class_map()["drift_classes"]]
    assert ids == ["green", "amber", "red", "blocking"]


def test_exactly_five_response_levels():
    ids = [l["id"] for l in levels.load_class_map()["response_levels"]]
    assert ids == [
        "level_1_detect",
        "level_2_warn",
        "level_3_auto_repair",
        "level_4_block",
        "level_5_escalate",
    ]


@pytest.mark.parametrize("cls,expected", [("green", False), ("amber", False), ("red", False), ("blocking", True)])
def test_only_blocking_blocks_work(cls, expected):
    assert levels.blocks_work(cls) is expected


def test_retired_vocabulary_maps_exactly_once():
    assert levels.resolve_legacy("dangerous") == "blocking"
    assert levels.resolve_legacy("correctable") == "level_3_auto_repair"
    assert levels.resolve_legacy("informational") == "level_1_detect"


def test_no_other_severity_vocabulary_exists():
    with pytest.raises(levels.ClassMapError):
        levels.resolve_legacy("critical")


def test_stated_class_to_level_mappings():
    assert levels.level_for_class("green") == "level_1_detect"
    assert levels.level_for_class("amber") == "level_2_warn"
    assert levels.level_for_class("blocking") == "level_4_block"


def test_red_class_resolves_only_through_the_contract():
    value = levels.level_for_class("red")
    assert value in levels.RESPONSE_LEVELS


def test_unknown_class_raises():
    with pytest.raises(levels.ClassMapError):
        levels.blocks_work("orange")
PYEOF
python -m pytest validators/drift/tests/test_levels.py -q 2>&1 | grep -oE '^[0-9]+ passed'
git add validators/drift/class_map.yaml validators/drift/levels.py validators/drift/tests/test_levels.py
git commit -m "L3-02-02: drift class and response-level tables as reviewable data (53.2, 53.4)"
git rebase origin/integration && git push -u origin lane/3/02-t02-class-map
```

### Acceptance criteria

| # | Criterion | Proving command | Required output |
| --- | --- | --- | --- |
| A1 | 11 tests pass | `cd "$(git rev-parse --show-toplevel)" && python -m pytest validators/drift/tests/test_levels.py -q 2>&1 \| grep -oE '^[0-9]+ passed'` | `11 passed` |
| A2 | `class_map.yaml` hard-codes no red level | `cd "$(git rev-parse --show-toplevel)" && grep -c 'red_class_level: from-contract' validators/drift/class_map.yaml` | `1` |
| A3 | Level 3 "applies to" text is the spec's closed list | `cd "$(git rev-parse --show-toplevel)" && grep -c 'removing expired assignments and expired access' validators/drift/class_map.yaml` | `1` |
| A4 | No foreign path touched | see SELF-VERIFY | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
python -m pytest validators/drift/tests/test_levels.py -q 2>&1 | grep -oE '^[0-9]+ passed'
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler|tools/provision|validators/drift)/'
```

Expected output:

```
11 passed
0
```

### STOP rule

STOP and file the R6 blocker if: the test count is not `11 passed`; `contracts/reconciler/level-map.yaml` is absent or its `red_class_level` is not one of the five level ids; you find yourself wanting to add a class or a level not in §53.2 or §53.4.
Do not invent a red-class level. Do not add a fifth drift class.

---

## L3-02-03 — Level 1: Detect

**Size:** M **Depends on:** T02, DEC-L3-02-03
**Spec basis:** §53.2 Level 1 — *"Record the finding with evidence and age. No notification."*, applying to *"Green-class drift: display names, documentation links, non-blocking metadata"*. §53.1 — *"Silent drift is not permitted. Every reconciliation run writes its result, and a clean run is recorded as clean."* Invariant 44. Also §53.1: *"Every drift finding carries an `acknowledged_by` and `acknowledged_at` field."*

### Files created

- `reconciler/levels/level1_detect.py`
- `reconciler/levels/tests/test_level1_detect.py`

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
git fetch origin && git checkout integration && git pull --ff-only
git checkout -b lane/3/02-t03-level1-detect
cat > reconciler/levels/level1_detect.py <<'PYEOF'
"""Level 1 - Detect (spec 53.2).

Behaviour: "Record the finding with evidence and age. No notification."
Applies to: green-class drift.

Two properties are load-bearing and are tested:
  1. This level emits NO notification of any kind (53.2, Level 1 row).
  2. A finding is recorded with its evidence and its age, and a clean run is
     still recorded (53.1: "Silent drift is not permitted ... a clean run is
     recorded as clean").
"""
from __future__ import annotations

import dataclasses
import datetime as _dt
import pathlib
from typing import Any

import yaml

from validators.drift import levels

_RECORDS_CONTRACT = pathlib.Path("contracts/reconciler/records.yaml")


class RecordsContractError(RuntimeError):
    """DEC-L3-02-03 unresolved or malformed."""


def _records_contract() -> dict[str, Any]:
    if not _RECORDS_CONTRACT.exists():
        raise RecordsContractError(
            "DEC-L3-02-03 unresolved: contracts/reconciler/records.yaml absent; "
            "section 97.2 names no reconciliation-run or repair record store"
        )
    data = yaml.safe_load(_RECORDS_CONTRACT.read_text(encoding="utf-8"))
    for key in ("run_record_path", "run_record_schema_id", "record_schema_version"):
        if key not in data:
            raise RecordsContractError(f"contracts/reconciler/records.yaml missing key: {key}")
    return data


@dataclasses.dataclass(frozen=True)
class Finding:
    """One drift finding. Fields are exactly what 53.1 and 53.2 require."""

    finding_id: str
    product: str
    comparison_row: str
    declared: str
    actual: str
    drift_class: str
    first_seen: _dt.datetime
    evidence_url: str
    acknowledged_by: str | None = None
    acknowledged_at: _dt.datetime | None = None

    def age_days(self, now: _dt.datetime) -> int:
        return (now - self.first_seen).days


NOTIFICATIONS: list[Any] = []  # Level 1 must never append to this.


def detect(findings: list[Finding], now: _dt.datetime) -> dict[str, Any]:
    """Record green-class findings. Emits no notification.

    Returns the run-record payload. Findings whose class is not green are
    returned untouched under 'deferred' for the higher levels to handle;
    this function never reclassifies (53.5: "There is no informal path from
    Red to Amber").
    """
    contract = _records_contract()
    recorded, deferred = [], []
    for f in findings:
        if levels.level_for_class(f.drift_class) == "level_1_detect":
            recorded.append(
                {
                    "finding_id": f.finding_id,
                    "product": f.product,
                    "comparison_row": f.comparison_row,
                    "declared": f.declared,
                    "actual": f.actual,
                    "drift_class": f.drift_class,
                    "level": "level_1_detect",
                    "age_days": f.age_days(now),
                    "evidence_url": f.evidence_url,
                    "acknowledged_by": f.acknowledged_by,
                    "acknowledged_at": f.acknowledged_at.isoformat() if f.acknowledged_at else None,
                }
            )
        else:
            deferred.append(f)
    return {
        "record_schema_version": contract["record_schema_version"],
        "schema_id": contract["run_record_schema_id"],
        "store_path": contract["run_record_path"],
        "level": "level_1_detect",
        "recorded": recorded,
        "deferred": deferred,
        "notifications_emitted": 0,
        "clean": len(recorded) == 0,
    }
PYEOF
cat > reconciler/levels/tests/test_level1_detect.py <<'PYEOF'
import datetime as dt

import pytest

from reconciler.levels import level1_detect as l1

NOW = dt.datetime(2026, 6, 1, tzinfo=dt.timezone.utc)


def _finding(cls="green", days=10, fid="F-1"):
    return l1.Finding(
        finding_id=fid,
        product="alpha",
        comparison_row="people.yaml display name",
        declared="A. Person",
        actual="A Person",
        drift_class=cls,
        first_seen=NOW - dt.timedelta(days=days),
        evidence_url="https://example.invalid/run/1",
    )


def test_green_finding_is_recorded():
    out = l1.detect([_finding()], NOW)
    assert len(out["recorded"]) == 1


def test_recorded_finding_carries_evidence_and_age():
    out = l1.detect([_finding(days=42)], NOW)
    row = out["recorded"][0]
    assert row["age_days"] == 42
    assert row["evidence_url"].startswith("https://")


def test_level1_emits_no_notification():
    before = list(l1.NOTIFICATIONS)
    out = l1.detect([_finding()], NOW)
    assert out["notifications_emitted"] == 0
    assert l1.NOTIFICATIONS == before


def test_non_green_findings_are_deferred_not_reclassified():
    f = _finding(cls="blocking")
    out = l1.detect([f], NOW)
    assert out["recorded"] == []
    assert out["deferred"] == [f]
    assert out["deferred"][0].drift_class == "blocking"


def test_clean_run_is_still_recorded_as_clean():
    out = l1.detect([], NOW)
    assert out["clean"] is True
    assert out["schema_id"]


def test_acknowledgement_fields_are_carried():
    f = l1.Finding(
        finding_id="F-2",
        product="alpha",
        comparison_row="docs link",
        declared="x",
        actual="y",
        drift_class="green",
        first_seen=NOW - dt.timedelta(days=1),
        evidence_url="https://example.invalid/run/2",
        acknowledged_by="tlead",
        acknowledged_at=NOW,
    )
    row = l1.detect([f], NOW)["recorded"][0]
    assert row["acknowledged_by"] == "tlead"
    assert row["acknowledged_at"] == NOW.isoformat()


def test_missing_records_contract_raises_not_defaults(monkeypatch, tmp_path):
    monkeypatch.setattr(l1, "_RECORDS_CONTRACT", tmp_path / "absent.yaml")
    with pytest.raises(l1.RecordsContractError):
        l1.detect([], NOW)
PYEOF
python -m pytest reconciler/levels/tests/test_level1_detect.py -q 2>&1 | grep -oE '^[0-9]+ passed'
git add reconciler/levels/level1_detect.py reconciler/levels/tests/test_level1_detect.py
git commit -m "L3-02-03: Level 1 Detect - record with evidence and age, no notification (53.2)"
git rebase origin/integration && git push -u origin lane/3/02-t03-level1-detect
```

### Acceptance criteria

| # | Criterion | Proving command | Required output |
| --- | --- | --- | --- |
| A1 | 7 tests pass | `cd "$(git rev-parse --show-toplevel)" && python -m pytest reconciler/levels/tests/test_level1_detect.py -q 2>&1 \| grep -oE '^[0-9]+ passed'` | `7 passed` |
| A2 | Level 1 module contains no notification call | `cd "$(git rev-parse --show-toplevel)" && grep -ciE 'notify|send_mail|slack|webhook' reconciler/levels/level1_detect.py` | `0` |
| A3 | The store path is never hard-coded | `cd "$(git rev-parse --show-toplevel)" && grep -c 'records/' reconciler/levels/level1_detect.py` | `0` |
| A4 | No foreign path touched | see SELF-VERIFY | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
python -m pytest reconciler/levels/tests/test_level1_detect.py -q 2>&1 | grep -oE '^[0-9]+ passed'
grep -ciE 'notify|send_mail|slack|webhook' reconciler/levels/level1_detect.py
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler|tools/provision|validators/drift)/'
```

Expected output:

```
7 passed
0
0
```

### STOP rule

STOP and file the R6 blocker if: the test count is not `7 passed`; `contracts/reconciler/records.yaml` is absent; you are tempted to write a record path literal into the module.
Do not add a notification to Level 1. Do not reclassify a non-green finding here.

---

## L3-02-04 — Level 2: Warn

**Size:** M **Depends on:** T02, T03, DEC-L3-02-01, DEC-L3-02-03
**Spec basis:** §53.2 Level 2 — *"Raise on the health report and notify the owner. No block."*, applying to *"Amber-class drift: stale contracts, stale flags, review concentration"*. §53.3 — *"Where actual state is stricter than declared state, reconciliation raises Level 2 for human judgment rather than relaxing the control."* AT-033.

> **Red output is Level 2 (BLOCKER) and raises a Founder-view flag per FD-007.**

### Files created

- `reconciler/levels/level2_warn.py`
- `reconciler/levels/tests/test_level2_warn.py`

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
git fetch origin && git checkout integration && git pull --ff-only
git checkout -b lane/3/02-t04-level2-warn
cat > reconciler/levels/level2_warn.py <<'PYEOF'
"""Level 2 - Warn (spec 53.2).

Behaviour: "Raise on the health report and notify the owner. No block."
Applies to: amber-class drift, and - per 53.3 - to every case where actual
state is STRICTER than declared state, which is raised here for human
judgment rather than relaxed.

The no-block property is structural: this module returns a payload with
blocks_work=False and exposes no check-run call. Blocking lives in
reconciler/levels/level4_block.py and nowhere else.
"""
from __future__ import annotations

from typing import Any

from reconciler.levels.level1_detect import Finding
from validators.drift import levels

STRICTER_THAN_DECLARED = "actual-stricter-than-declared"


def warn(
    findings: list[Finding],
    stricter_than_declared: list[Finding],
    now,
) -> dict[str, Any]:
    """Raise amber findings on the health report and notify their owner.

    `stricter_than_declared` carries the findings the stricter-only
    comparator refused to repair (53.3). They are raised here regardless of
    their own class, because 53.3 names Level 2 as their destination.
    """
    entries, deferred = [], []
    for f in findings:
        if levels.level_for_class(f.drift_class) == "level_2_warn":
            entries.append(
                {
                    "finding_id": f.finding_id,
                    "product": f.product,
                    "comparison_row": f.comparison_row,
                    "declared": f.declared,
                    "actual": f.actual,
                    "drift_class": f.drift_class,
                    "level": "level_2_warn",
                    "age_days": f.age_days(now),
                    "evidence_url": f.evidence_url,
                    "reason": "amber-class drift",
                    "notify_owner": True,
                    "health_report": True,
                }
            )
        else:
            deferred.append(f)
    for f in stricter_than_declared:
        entries.append(
            {
                "finding_id": f.finding_id,
                "product": f.product,
                "comparison_row": f.comparison_row,
                "declared": f.declared,
                "actual": f.actual,
                "drift_class": f.drift_class,
                "level": "level_2_warn",
                "age_days": f.age_days(now),
                "evidence_url": f.evidence_url,
                "reason": STRICTER_THAN_DECLARED,
                "notify_owner": True,
                "health_report": True,
            }
        )
    return {
        "level": "level_2_warn",
        "entries": entries,
        "deferred": deferred,
        "blocks_work": False,
    }
PYEOF
cat > reconciler/levels/tests/test_level2_warn.py <<'PYEOF'
import datetime as dt

from reconciler.levels import level2_warn as l2
from reconciler.levels.level1_detect import Finding

NOW = dt.datetime(2026, 6, 1, tzinfo=dt.timezone.utc)


def _f(cls="amber", fid="F-1"):
    return Finding(
        finding_id=fid,
        product="alpha",
        comparison_row="product.yaml reviewed_at",
        declared="2026-01-01",
        actual="2025-05-01",
        drift_class=cls,
        first_seen=NOW - dt.timedelta(days=200),
        evidence_url="https://example.invalid/run/9",
    )


def test_amber_raises_on_health_report_and_notifies_owner():
    out = l2.warn([_f()], [], NOW)
    entry = out["entries"][0]
    assert entry["health_report"] is True
    assert entry["notify_owner"] is True


def test_level2_never_blocks():
    out = l2.warn([_f()], [], NOW)
    assert out["blocks_work"] is False


def test_non_amber_is_deferred():
    f = _f(cls="blocking")
    out = l2.warn([f], [], NOW)
    assert out["entries"] == []
    assert out["deferred"] == [f]


def test_stricter_than_declared_is_raised_here_for_human_judgment():
    f = _f(cls="green", fid="F-STRICT")
    out = l2.warn([], [f], NOW)
    assert out["entries"][0]["reason"] == l2.STRICTER_THAN_DECLARED
    assert out["entries"][0]["level"] == "level_2_warn"


def test_module_exposes_no_check_run_call():
    src = open("reconciler/levels/level2_warn.py", encoding="utf-8").read()
    assert "check_run" not in src and "check-run" not in src
PYEOF
python -m pytest reconciler/levels/tests/test_level2_warn.py -q 2>&1 | grep -oE '^[0-9]+ passed'
git add reconciler/levels/level2_warn.py reconciler/levels/tests/test_level2_warn.py
git commit -m "L3-02-04: Level 2 Warn - health report plus owner notification, no block (53.2, 53.3)"
git rebase origin/integration && git push -u origin lane/3/02-t04-level2-warn
```

### Acceptance criteria

| # | Criterion | Proving command | Required output |
| --- | --- | --- | --- |
| A1 | 5 tests pass | `cd "$(git rev-parse --show-toplevel)" && python -m pytest reconciler/levels/tests/test_level2_warn.py -q 2>&1 \| grep -oE '^[0-9]+ passed'` | `5 passed` |
| A2 | Level 2 contains no blocking primitive | `cd "$(git rev-parse --show-toplevel)" && grep -ciE 'check_run|conclusion.*failure|block_deploy' reconciler/levels/level2_warn.py` | `0` |
| A3 | The §53.3 stricter-than-declared destination is present | `cd "$(git rev-parse --show-toplevel)" && grep -c 'actual-stricter-than-declared' reconciler/levels/level2_warn.py` | `1` |
| A4 | No foreign path touched | see SELF-VERIFY | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
python -m pytest reconciler/levels/tests/test_level2_warn.py -q 2>&1 | grep -oE '^[0-9]+ passed'
grep -ciE 'check_run|conclusion.*failure|block_deploy' reconciler/levels/level2_warn.py
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler|tools/provision|validators/drift)/'
```

Expected output:

```
5 passed
0
0
```

### STOP rule

STOP and file the R6 blocker if: the test count is not `5 passed`; A2 is non-zero; `red` resolves through `levels.level_for_class` to `level_2_warn` and you are unsure whether Founder-view surfacing is also required — that is DEC-L3-02-01 and it is L0's, not yours.

---

## L3-02-05 — The stricter-only comparator

**Size:** L **Depends on:** T02
**Spec basis:** §53.3 verbatim — *"a repair is permitted only when it moves the system toward the declared state **and** the declared state is at least as restrictive as the actual state. Reconciliation never loosens a control automatically, never modifies production runtime configuration, never modifies data, and never rotates or writes secrets. Where actual state is stricter than declared state, reconciliation raises Level 2 for human judgment rather than relaxing the control."* Invariant 81. AT-033. §99.6 risk 6 — *"stricter-only rule enforced in code and tested"*.

**This is the single most dangerous function in the system. It ships before any executor exists.**

### Files created

- `validators/drift/stricter_only.py`
- `validators/drift/fixtures/stricter_only_cases.yaml`
- `validators/drift/tests/test_stricter_only.py`

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
git fetch origin && git checkout integration && git pull --ff-only
git checkout -b lane/3/02-t05-stricter-only
cat > validators/drift/stricter_only.py <<'PYEOF'
"""The auto-repair rule (spec 53.3, invariant 81, AT-033).

Binding text, section 53.3:

    a repair is permitted only when it moves the system toward the declared
    state AND the declared state is at least as restrictive as the actual
    state. Reconciliation never loosens a control automatically, never
    modifies production runtime configuration, never modifies data, and
    never rotates or writes secrets. Where actual state is stricter than
    declared state, reconciliation raises Level 2 for human judgment rather
    than relaxing the control.

Four hard prohibitions and one comparison. The function is total: every
input returns one of the four verdicts, and UNKNOWN is a refusal, never an
allow. Fail-closed is deliberate (section 64.2).
"""
from __future__ import annotations

import enum
from typing import Any


class Verdict(enum.Enum):
    REPAIR_PERMITTED = "repair-permitted"
    RAISE_LEVEL_2_ACTUAL_STRICTER = "raise-level-2-actual-stricter"
    REFUSED_PROHIBITED_TARGET = "refused-prohibited-target"
    REFUSED_INCOMPARABLE = "refused-incomparable"


# Section 53.3: the four things reconciliation never does.
PROHIBITED_TARGETS = (
    "production-runtime-config",
    "data",
    "secret-rotation",
    "secret-write",
)


class Restriction:
    """A partial order on control strength.

    Strength is an integer where a HIGHER value is MORE restrictive. Two
    values are comparable only when both carry a strength for the same
    control kind; otherwise the comparator refuses.
    """

    def __init__(self, control_kind: str, strength: int | None):
        self.control_kind = control_kind
        self.strength = strength

    def comparable_to(self, other: "Restriction") -> bool:
        return (
            self.control_kind == other.control_kind
            and self.strength is not None
            and other.strength is not None
        )


def evaluate(
    control_kind: str,
    declared: Restriction,
    actual: Restriction,
    target: str,
) -> Verdict:
    """Decide whether a repair from `actual` to `declared` is permitted.

    Order of evaluation is fixed and must not be reordered:
      1. prohibited target      -> REFUSED_PROHIBITED_TARGET
      2. incomparable strengths -> REFUSED_INCOMPARABLE (fail closed)
      3. actual stricter        -> RAISE_LEVEL_2_ACTUAL_STRICTER
      4. declared >= actual     -> REPAIR_PERMITTED
    """
    if target in PROHIBITED_TARGETS:
        return Verdict.REFUSED_PROHIBITED_TARGET
    if declared.control_kind != control_kind or actual.control_kind != control_kind:
        return Verdict.REFUSED_INCOMPARABLE
    if not declared.comparable_to(actual):
        return Verdict.REFUSED_INCOMPARABLE
    if actual.strength > declared.strength:
        # Actual is stricter than declared. 53.3: raise Level 2, never relax.
        return Verdict.RAISE_LEVEL_2_ACTUAL_STRICTER
    # declared.strength >= actual.strength: declared is at least as
    # restrictive as actual, and the repair moves toward declared state.
    return Verdict.REPAIR_PERMITTED


def is_permitted(verdict: Verdict) -> bool:
    """The only place in the codebase that converts a verdict to a boolean."""
    return verdict is Verdict.REPAIR_PERMITTED
PYEOF
cat > validators/drift/fixtures/stricter_only_cases.yaml <<'EOF'
# Table-driven cases for the section 53.3 auto-repair rule.
# Higher strength == more restrictive.
# Every case names the spec clause it exercises. Add cases; never delete one.
cases:
  - id: SO-01
    clause: "53.3 declared at least as restrictive -> permitted"
    control_kind: required_approvals
    declared_strength: 2
    actual_strength: 1
    target: branch-protection
    expect: repair-permitted
  - id: SO-02
    clause: "53.3 equal strength is 'at least as restrictive' -> permitted (idempotent re-apply)"
    control_kind: required_approvals
    declared_strength: 2
    actual_strength: 2
    target: branch-protection
    expect: repair-permitted
  - id: SO-03
    clause: "53.3 / AT-033 actual stricter -> raise Level 2, never relax"
    control_kind: required_approvals
    declared_strength: 1
    actual_strength: 3
    target: branch-protection
    expect: raise-level-2-actual-stricter
  - id: SO-04
    clause: "53.3 never modifies production runtime configuration"
    control_kind: required_approvals
    declared_strength: 5
    actual_strength: 0
    target: production-runtime-config
    expect: refused-prohibited-target
  - id: SO-05
    clause: "53.3 never modifies data"
    control_kind: required_approvals
    declared_strength: 5
    actual_strength: 0
    target: data
    expect: refused-prohibited-target
  - id: SO-06
    clause: "53.3 never rotates secrets"
    control_kind: required_approvals
    declared_strength: 5
    actual_strength: 0
    target: secret-rotation
    expect: refused-prohibited-target
  - id: SO-07
    clause: "53.3 never writes secrets"
    control_kind: required_approvals
    declared_strength: 5
    actual_strength: 0
    target: secret-write
    expect: refused-prohibited-target
  - id: SO-08
    clause: "64.2 fail closed - unknown declared strength is not an allow"
    control_kind: required_approvals
    declared_strength: null
    actual_strength: 1
    target: branch-protection
    expect: refused-incomparable
  - id: SO-09
    clause: "64.2 fail closed - unknown actual strength is not an allow"
    control_kind: required_approvals
    declared_strength: 2
    actual_strength: null
    target: branch-protection
    expect: refused-incomparable
  - id: SO-10
    clause: "53.3 team membership: declared removes a member actual still has -> toward declared, stricter"
    control_kind: team_membership_count_over_declared
    declared_strength: 1
    actual_strength: 0
    target: team-membership
    expect: repair-permitted
  - id: SO-11
    clause: "53.3 team membership: actual already tighter than declared -> Level 2"
    control_kind: team_membership_count_over_declared
    declared_strength: 0
    actual_strength: 2
    target: team-membership
    expect: raise-level-2-actual-stricter
  - id: SO-12
    clause: "53.1 environment deployment branch policy: declared narrower -> permitted"
    control_kind: environment_branch_policy
    declared_strength: 3
    actual_strength: 1
    target: environment-config
    expect: repair-permitted
  - id: SO-13
    clause: "53.1 environment deployment branch policy: actual narrower -> Level 2"
    control_kind: environment_branch_policy
    declared_strength: 1
    actual_strength: 3
    target: environment-config
    expect: raise-level-2-actual-stricter
  - id: SO-14
    clause: "64.2 fail closed - mismatched control kinds are incomparable"
    control_kind: required_approvals
    declared_strength: 2
    actual_strength: 1
    target: branch-protection
    mismatch_kind: true
    expect: refused-incomparable
EOF
cat > validators/drift/tests/test_stricter_only.py <<'PYEOF'
import pathlib

import pytest
import yaml

from validators.drift.stricter_only import (
    PROHIBITED_TARGETS,
    Restriction,
    Verdict,
    evaluate,
    is_permitted,
)

CASES = yaml.safe_load(
    (pathlib.Path("validators/drift/fixtures/stricter_only_cases.yaml")).read_text(encoding="utf-8")
)["cases"]


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_case_table(case):
    kind = case["control_kind"]
    declared = Restriction(kind, case["declared_strength"])
    actual_kind = "some-other-kind" if case.get("mismatch_kind") else kind
    actual = Restriction(actual_kind, case["actual_strength"])
    assert evaluate(kind, declared, actual, case["target"]).value == case["expect"]


def test_all_four_prohibited_targets_are_present():
    assert set(PROHIBITED_TARGETS) == {
        "production-runtime-config",
        "data",
        "secret-rotation",
        "secret-write",
    }


def test_only_one_verdict_is_permitted():
    permitted = [v for v in Verdict if is_permitted(v)]
    assert permitted == [Verdict.REPAIR_PERMITTED]


def test_at_033_no_auto_loosening_end_to_end():
    """AT-033: a stricter-than-declared production control is raised, not relaxed."""
    v = evaluate(
        "required_approvals",
        Restriction("required_approvals", 1),
        Restriction("required_approvals", 4),
        "branch-protection",
    )
    assert v is Verdict.RAISE_LEVEL_2_ACTUAL_STRICTER
    assert is_permitted(v) is False


def test_prohibited_target_wins_even_when_declared_is_stricter():
    for target in PROHIBITED_TARGETS:
        v = evaluate(
            "required_approvals",
            Restriction("required_approvals", 9),
            Restriction("required_approvals", 0),
            target,
        )
        assert v is Verdict.REFUSED_PROHIBITED_TARGET


def test_no_input_returns_permitted_by_default():
    """Fail-closed: an empty/unknown comparison must not be permitted."""
    v = evaluate("k", Restriction("k", None), Restriction("k", None), "branch-protection")
    assert is_permitted(v) is False
PYEOF
python -m pytest validators/drift/tests/test_stricter_only.py -q 2>&1 | grep -oE '^[0-9]+ passed'
git add validators/drift/stricter_only.py validators/drift/fixtures/stricter_only_cases.yaml validators/drift/tests/test_stricter_only.py
git commit -m "L3-02-05: stricter-only comparator enforced in code and tested (53.3, inv 81, AT-033)"
git rebase origin/integration && git push -u origin lane/3/02-t05-stricter-only
```

### Acceptance criteria

| # | Criterion | Proving command | Required output |
| --- | --- | --- | --- |
| A1 | 19 tests pass (14 table cases + 5 property tests) | `cd "$(git rev-parse --show-toplevel)" && python -m pytest validators/drift/tests/test_stricter_only.py -q 2>&1 \| grep -oE '^[0-9]+ passed'` | `19 passed` |
| A2 | All 14 fixture cases are exercised | `cd "$(git rev-parse --show-toplevel)" && python -m pytest validators/drift/tests/test_stricter_only.py -q --collect-only 2>&1 \| grep -c 'SO-'` | `14` |
| A3 | Exactly four verdicts exist, exactly one permits | `cd "$(git rev-parse --show-toplevel)" && python -c "from validators.drift.stricter_only import Verdict,is_permitted;print(len(list(Verdict)),sum(1 for v in Verdict if is_permitted(v)))"` | `4 1` |
| A4 | The comparator is the only permit gate — no other module defines one | `cd "$(git rev-parse --show-toplevel)" && grep -rl 'REPAIR_PERMITTED' --include='*.py' reconciler validators \| wc -l` | `2` |
| A5 | No foreign path touched | see SELF-VERIFY | `0` |

*(A4 expects exactly two files at this task: `validators/drift/stricter_only.py` and its test.)*

### SELF-VERIFY

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
python -m pytest validators/drift/tests/test_stricter_only.py -q 2>&1 | grep -oE '^[0-9]+ passed'
python -c "from validators.drift.stricter_only import Verdict,is_permitted;print(len(list(Verdict)),sum(1 for v in Verdict if is_permitted(v)))"
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler|tools/provision|validators/drift)/'
```

Expected output:

```
19 passed
4 1
0
```

### STOP rule

STOP and file the R6 blocker if: the test count is not `19 passed`; A3 does not print `4 1`; any test fails; you find a real comparison whose two sides cannot be reduced to a `control_kind` plus an integer strength (that is a modelling gap and belongs to L0, not to you).
**Never add a verdict that permits.** Never add a fifth verdict. Never delete a fixture case. Never make `REFUSED_INCOMPARABLE` fall through to permitted.

---

## L3-02-06 — The permitted repair-class registry

**Size:** M **Depends on:** T05, DEC-L3-02-04
**Spec basis:** §53.2 Level 3 "Applies to" cell, verbatim and closed: *"Safe, idempotent, reversible repairs only: Team membership sync from registries, CODEOWNERS regeneration, label and board field sync, re-applying declared branch protection, removing expired assignments and expired access."* §26.4 (Level-3 repairs write under the reconciler credential and are logged as repair records). §28.1 (the compensating action must exist, be tested and be named). §99.6 risk 6.

**Five classes. The list is closed.** The §53.1 row *"`product.yaml` lifecycle → Renovate, monitoring and CI configuration → Auto-repair where safe"* is **not** a sixth class here; whether it becomes one is DEC-L3-02-04 and is read from `contracts/reconciler/repair-classes.yaml`.

> **Auto-repair branch is unreachable in current architecture:** all five repair classes ship with `enabled: false`; the repair executor (T08) requires enablement through T07's discipline. The repair execution path additionally requires L3 write access to the product repository, which is not granted in V1. See L0-04 REG-039.

### Files created

- `reconciler/repair/classes.yaml`
- `reconciler/repair/registry.py`
- `reconciler/repair/tests/test_registry.py`

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
git fetch origin && git checkout integration && git pull --ff-only
git checkout -b lane/3/02-t06-repair-classes
cat > reconciler/repair/classes.yaml <<'EOF'
# Option B ratified: five-class registry and `enabled: false` are correct as shipped. No changes.
#
# The permitted Level-3 repair classes.
#
# Section 53.2, Level 3, "Applies to", verbatim:
#   "Safe, idempotent, reversible repairs only: Team membership sync from
#    registries, CODEOWNERS regeneration, label and board field sync,
#    re-applying declared branch protection, removing expired assignments
#    and expired access"
#
# THE LIST IS CLOSED. Adding a class is a governance act, not an edit.
# Section 99.6 risk 6: "repair classes enabled one at a time".
# Every class ships enabled: false. Enablement is L3-02-07's mechanism.
registry_version: 1
spec_section: "53.2"

classes:
  - id: team-membership-sync
    spec_phrase: "Team membership sync from registries"
    control_kind: team_membership_count_over_declared
    target: team-membership
    idempotent: true
    reversible_class: fully-reversible          # section 28.1
    compensating_action: "re-add the removed member from the pre-repair snapshot"
    enabled: false

  - id: codeowners-regeneration
    spec_phrase: "CODEOWNERS regeneration"
    control_kind: codeowners_content
    target: codeowners
    idempotent: true
    reversible_class: fully-reversible
    compensating_action: "restore the pre-repair CODEOWNERS blob recorded in the repair record"
    enabled: false

  - id: label-and-board-field-sync
    spec_phrase: "label and board field sync"
    control_kind: label_and_board_field_set
    target: labels-and-board-fields
    idempotent: true
    reversible_class: fully-reversible
    compensating_action: "restore the pre-repair label and field set from the repair record"
    enabled: false

  - id: branch-protection-reapply
    spec_phrase: "re-applying declared branch protection"
    control_kind: required_approvals
    target: branch-protection
    idempotent: true
    reversible_class: fully-reversible
    compensating_action: "re-apply the pre-repair protection JSON recorded in the repair record"
    enabled: false

  - id: expired-assignment-and-access-removal
    spec_phrase: "removing expired assignments and expired access"
    control_kind: expired_grant_count
    target: expired-grant
    idempotent: true
    reversible_class: partially-reversible      # re-granting requires a human decision
    compensating_action: "re-grant only through the registry-change lane of section 26.4; the reconciler never re-grants"
    enabled: false
EOF
cat > reconciler/repair/registry.py <<'PYEOF'
"""The closed registry of permitted Level-3 repair classes (spec 53.2).

Invariants enforced here, each with a test:
  - exactly the five classes section 53.2 enumerates exist;
  - every class is idempotent (53.2: "Safe, idempotent, reversible repairs only");
  - every class names a compensating action (28.1);
  - every class ships disabled (99.6 risk 6: enabled one at a time);
  - no repair may target anything in stricter_only.PROHIBITED_TARGETS (53.3).
"""
from __future__ import annotations

import functools
import pathlib
from typing import Any

import yaml

from validators.drift.stricter_only import PROHIBITED_TARGETS

_CLASSES = pathlib.Path(__file__).with_name("classes.yaml")
_CONTRACT = pathlib.Path("contracts/reconciler/repair-classes.yaml")

# Section 53.2, Level 3 "Applies to", in the order the spec writes them.
SPEC_CLASS_IDS = (
    "team-membership-sync",
    "codeowners-regeneration",
    "label-and-board-field-sync",
    "branch-protection-reapply",
    "expired-assignment-and-access-removal",
)


class RepairClassError(RuntimeError):
    pass


@functools.lru_cache(maxsize=1)
def load() -> list[dict[str, Any]]:
    data = yaml.safe_load(_CLASSES.read_text(encoding="utf-8"))["classes"]
    ids = tuple(c["id"] for c in data)
    if ids != SPEC_CLASS_IDS:
        raise RepairClassError(
            f"repair classes must be exactly the five of section 53.2 in order "
            f"{SPEC_CLASS_IDS}, got {ids}"
        )
    for c in data:
        if not c["idempotent"]:
            raise RepairClassError(f"{c['id']}: section 53.2 permits idempotent repairs only")
        if not c.get("compensating_action"):
            raise RepairClassError(f"{c['id']}: section 28.1 requires a named compensating action")
        if c["target"] in PROHIBITED_TARGETS:
            raise RepairClassError(f"{c['id']}: section 53.3 prohibits target {c['target']}")
        if c["reversible_class"] not in ("fully-reversible", "partially-reversible"):
            raise RepairClassError(
                f"{c['id']}: section 53.2 permits reversible repairs only; "
                f"non-reversible is never a repair class"
            )
    return data


def get(class_id: str) -> dict[str, Any]:
    for c in load():
        if c["id"] == class_id:
            return c
    raise RepairClassError(f"not a permitted repair class: {class_id}")


def sixth_class_disposition() -> str:
    """DEC-L3-02-04. Section 53.1's 'auto-repair where safe' lifecycle row."""
    if not _CONTRACT.exists():
        raise RepairClassError(
            "DEC-L3-02-04 unresolved: contracts/reconciler/repair-classes.yaml absent"
        )
    value = yaml.safe_load(_CONTRACT.read_text(encoding="utf-8")).get("lifecycle_config_class")
    if value is None:
        raise RepairClassError("contracts/reconciler/repair-classes.yaml: lifecycle_config_class missing")
    return value
PYEOF
cat > reconciler/repair/tests/test_registry.py <<'PYEOF'
import pytest

from reconciler.repair import registry
from validators.drift.stricter_only import PROHIBITED_TARGETS


def test_exactly_five_classes_in_spec_order():
    assert tuple(c["id"] for c in registry.load()) == registry.SPEC_CLASS_IDS


def test_every_class_quotes_its_spec_phrase():
    phrases = {c["spec_phrase"] for c in registry.load()}
    assert phrases == {
        "Team membership sync from registries",
        "CODEOWNERS regeneration",
        "label and board field sync",
        "re-applying declared branch protection",
        "removing expired assignments and expired access",
    }


def test_every_class_is_idempotent():
    assert all(c["idempotent"] for c in registry.load())


def test_every_class_names_a_compensating_action():
    assert all(c["compensating_action"].strip() for c in registry.load())


def test_no_class_is_non_reversible():
    assert all(c["reversible_class"] != "non-reversible" for c in registry.load())


def test_no_class_targets_a_prohibited_target():
    assert all(c["target"] not in PROHIBITED_TARGETS for c in registry.load())


def test_every_class_ships_disabled():
    assert all(c["enabled"] is False for c in registry.load())


def test_unknown_class_is_refused():
    with pytest.raises(registry.RepairClassError):
        registry.get("rotate-secrets")


def test_lifecycle_row_disposition_comes_from_the_contract():
    assert registry.sixth_class_disposition()
PYEOF
python -m pytest reconciler/repair/tests/test_registry.py -q 2>&1 | grep -oE '^[0-9]+ passed'
git add reconciler/repair/classes.yaml reconciler/repair/registry.py reconciler/repair/tests/test_registry.py
git commit -m "L3-02-06: closed registry of the five permitted repair classes (53.2, 28.1, 99.6 risk 6)"
git rebase origin/integration && git push -u origin lane/3/02-t06-repair-classes
```

### Acceptance criteria

| # | Criterion | Proving command | Required output |
| --- | --- | --- | --- |
| A1 | 9 tests pass | `cd "$(git rev-parse --show-toplevel)" && python -m pytest reconciler/repair/tests/test_registry.py -q 2>&1 \| grep -oE '^[0-9]+ passed'` | `9 passed` |
| A2 | Exactly five classes | `cd "$(git rev-parse --show-toplevel)" && grep -c '^  - id: ' reconciler/repair/classes.yaml` | `5` |
| A3 | All five ship disabled | `cd "$(git rev-parse --show-toplevel)" && grep -c 'enabled: false' reconciler/repair/classes.yaml` | `5` |
| A4 | No class enabled anywhere in the tree | `cd "$(git rev-parse --show-toplevel)" && grep -rc 'enabled: true' reconciler/repair/classes.yaml` | `0` |
| A5 | No foreign path touched | see SELF-VERIFY | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
python -m pytest reconciler/repair/tests/test_registry.py -q 2>&1 | grep -oE '^[0-9]+ passed'
grep -c '^  - id: ' reconciler/repair/classes.yaml
grep -c 'enabled: false' reconciler/repair/classes.yaml
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler|tools/provision|validators/drift)/'
```

Expected output:

```
9 passed
5
5
0
```

### STOP rule

STOP and file the R6 blocker if: any count above differs; `contracts/reconciler/repair-classes.yaml` is absent or its `lifecycle_config_class` is missing.
**Option B ratified: five-class registry and `enabled: false` are correct as shipped. No changes.** Do not add a sixth class. Do not set any `enabled: true` in this task. Do not classify any repair `non-reversible` — §53.2 permits reversible repairs only.

---

## L3-02-07 — Enable-one-class-at-a-time discipline

**Size:** M **Depends on:** T06
**Spec basis:** §99.6 risk 6 — *"Detect-only first; repair classes enabled one at a time"*. §99.4 item 6 — *"Auto-repair is deferred until detection has run clean for weeks."* §26.4 — a merged registry change is applied *"to the declared canary set only; the remainder of the fleet is held for one reconciliation cycle and applied only after the canary cycle records a clean run"* (D93). §53.1 seeded-canary rule (a run reporting zero findings is a FAILED run, so "clean" means *found the canary and nothing else*).

### Files created

- `reconciler/repair/enablement.py`
- `reconciler/repair/enablement_state.yaml`
- `reconciler/repair/tests/test_enablement.py`

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
git fetch origin && git checkout integration && git pull --ff-only
git checkout -b lane/3/02-t07-enablement
cat > reconciler/repair/enablement_state.yaml <<'EOF'
# Repair-class enablement ledger.
#
# Section 99.6 risk 6: "repair classes enabled one at a time".
# Section 99.4 item 6: auto-repair waits until detection has run clean.
# Section 26.4 / D93: a change applies to the declared canary set first and
# the fleet is held for one reconciliation cycle.
#
# This file is the ONLY place a repair class becomes live. Changing it is a
# registry-change-lane edit (section 26.4), not a code change.
state_version: 1

# The number of consecutive clean reconciliation cycles a class must observe
# in detect-only shadow mode before it may be enabled. Calibrated
# configuration; the initial value below is the one L0 records at enablement.
required_clean_shadow_cycles: from-contract

# At most one entry may ever be in state 'canary' or 'enabling'.
enablements: []
# Example shape (do not uncomment; L0 writes the real entry):
#   - class_id: codeowners-regeneration
#     state: canary            # shadow | canary | fleet
#     decision_record: DEC-YYYY-NNN
#     entered_state_at: 2026-06-01T00:00:00Z
#     clean_shadow_cycles: 0
EOF
cat > reconciler/repair/enablement.py <<'PYEOF'
"""One repair class at a time (spec 99.6 risk 6, 99.4 item 6, 26.4/D93).

Three rules, each with a test:

  R-A  At most one repair class may be in a non-fleet transition state
       (shadow, canary or enabling) at any moment. 99.6 risk 6.
  R-B  A class may leave shadow only after the required number of
       consecutive CLEAN reconciliation cycles. 99.4 item 6. A cycle counts
       as clean only if it found the seeded canary (53.1) - a zero-finding
       run is a FAILED run, never a clean one.
  R-C  A class enters the fleet only after one full clean CANARY cycle on
       the declared canary set. 26.4 / D93.
"""
from __future__ import annotations

import pathlib
from typing import Any

import yaml

from reconciler.repair import registry

_STATE = pathlib.Path(__file__).with_name("enablement_state.yaml")
_CONTRACT = pathlib.Path("contracts/reconciler/repair-classes.yaml")

TRANSITION_STATES = ("shadow", "canary", "enabling")
ALL_STATES = TRANSITION_STATES + ("fleet",)


class EnablementError(RuntimeError):
    pass


def load_state() -> dict[str, Any]:
    return yaml.safe_load(_STATE.read_text(encoding="utf-8"))


def _required_cycles() -> int:
    if not _CONTRACT.exists():
        raise EnablementError("contracts/reconciler/repair-classes.yaml absent")
    value = yaml.safe_load(_CONTRACT.read_text(encoding="utf-8")).get("required_clean_shadow_cycles")
    if not isinstance(value, int) or value < 1:
        raise EnablementError(
            "contracts/reconciler/repair-classes.yaml: required_clean_shadow_cycles "
            "must be an integer >= 1"
        )
    return value


def check_single_transition(state: dict[str, Any]) -> None:
    """R-A. At most one class in a transition state."""
    in_transition = [e for e in state.get("enablements") or [] if e["state"] in TRANSITION_STATES]
    if len(in_transition) > 1:
        raise EnablementError(
            "section 99.6 risk 6: repair classes are enabled one at a time; "
            f"{len(in_transition)} classes are in a transition state: "
            f"{[e['class_id'] for e in in_transition]}"
        )


def may_leave_shadow(entry: dict[str, Any]) -> bool:
    """R-B. Enough consecutive clean cycles observed."""
    return int(entry.get("clean_shadow_cycles", 0)) >= _required_cycles()


def may_reach_fleet(entry: dict[str, Any], canary_cycle_clean: bool) -> bool:
    """R-C. One clean canary cycle before the fleet (26.4 / D93)."""
    return entry["state"] == "canary" and bool(canary_cycle_clean)


def is_live(class_id: str, product: str, canary_products: list[str]) -> bool:
    """Is this repair class permitted to write, for this product, right now?

    Fail closed: an unknown class, an absent entry, shadow state, or a
    canary-state class asked about a non-canary product all return False.
    """
    registry.get(class_id)  # raises if not one of the five
    state = load_state()
    check_single_transition(state)
    for entry in state.get("enablements") or []:
        if entry["class_id"] != class_id:
            continue
        if entry["state"] not in ALL_STATES:
            raise EnablementError(f"unknown enablement state: {entry['state']}")
        if entry["state"] == "fleet":
            return True
        if entry["state"] == "canary":
            return product in canary_products
        return False  # shadow and enabling never write
    return False
PYEOF
cat > reconciler/repair/tests/test_enablement.py <<'PYEOF'
import pytest

from reconciler.repair import enablement as en


def _state(entries):
    return {"state_version": 1, "enablements": entries}


def test_shipped_state_has_no_live_class():
    assert (en.load_state().get("enablements") or []) == []


def test_two_classes_in_transition_is_refused():
    st = _state(
        [
            {"class_id": "codeowners-regeneration", "state": "canary"},
            {"class_id": "team-membership-sync", "state": "shadow"},
        ]
    )
    with pytest.raises(en.EnablementError):
        en.check_single_transition(st)


def test_one_class_in_transition_is_allowed():
    st = _state([{"class_id": "codeowners-regeneration", "state": "canary"}])
    en.check_single_transition(st)


def test_shadow_class_never_writes(monkeypatch):
    monkeypatch.setattr(
        en, "load_state", lambda: _state([{"class_id": "codeowners-regeneration", "state": "shadow"}])
    )
    assert en.is_live("codeowners-regeneration", "alpha", ["alpha"]) is False


def test_canary_class_writes_only_on_canary_products(monkeypatch):
    monkeypatch.setattr(
        en, "load_state", lambda: _state([{"class_id": "codeowners-regeneration", "state": "canary"}])
    )
    assert en.is_live("codeowners-regeneration", "alpha", ["alpha"]) is True
    assert en.is_live("codeowners-regeneration", "beta", ["alpha"]) is False


def test_absent_entry_is_not_live(monkeypatch):
    monkeypatch.setattr(en, "load_state", lambda: _state([]))
    assert en.is_live("branch-protection-reapply", "alpha", ["alpha"]) is False


def test_class_outside_the_five_is_refused():
    with pytest.raises(Exception):
        en.is_live("rotate-secrets", "alpha", ["alpha"])


def test_shadow_exit_requires_the_contracted_clean_cycle_count():
    required = en._required_cycles()
    assert en.may_leave_shadow({"clean_shadow_cycles": required - 1}) is False
    assert en.may_leave_shadow({"clean_shadow_cycles": required}) is True


def test_fleet_requires_a_clean_canary_cycle():
    entry = {"class_id": "codeowners-regeneration", "state": "canary"}
    assert en.may_reach_fleet(entry, canary_cycle_clean=False) is False
    assert en.may_reach_fleet(entry, canary_cycle_clean=True) is True
    assert en.may_reach_fleet({"class_id": "x", "state": "shadow"}, True) is False
PYEOF
python -m pytest reconciler/repair/tests/test_enablement.py -q 2>&1 | grep -oE '^[0-9]+ passed'
git add reconciler/repair/enablement.py reconciler/repair/enablement_state.yaml reconciler/repair/tests/test_enablement.py
git commit -m "L3-02-07: one repair class at a time, shadow then canary then fleet (99.6 risk 6, 26.4/D93)"
git rebase origin/integration && git push -u origin lane/3/02-t07-enablement
```

### Acceptance criteria

| # | Criterion | Proving command | Required output |
| --- | --- | --- | --- |
| A1 | 9 tests pass | `cd "$(git rev-parse --show-toplevel)" && python -m pytest reconciler/repair/tests/test_enablement.py -q 2>&1 \| grep -oE '^[0-9]+ passed'` | `9 passed` |
| A2 | The shipped ledger enables nothing | `cd "$(git rev-parse --show-toplevel)" && python -c "from reconciler.repair import enablement as e;print(len(e.load_state().get('enablements') or []))"` | `0` |
| A3 | Two-in-transition is refused | `cd "$(git rev-parse --show-toplevel)" && python -c "
from reconciler.repair import enablement as e
try:
    e.check_single_transition({'enablements':[{'class_id':'a','state':'canary'},{'class_id':'b','state':'shadow'}]})
    print('REFUSAL-MISSING')
except e.EnablementError:
    print('REFUSED')"` | `REFUSED` |
| A4 | No foreign path touched | see SELF-VERIFY | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
python -m pytest reconciler/repair/tests/test_enablement.py -q 2>&1 | grep -oE '^[0-9]+ passed'
python -c "from reconciler.repair import enablement as e;print(len(e.load_state().get('enablements') or []))"
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler|tools/provision|validators/drift)/'
```

Expected output:

```
9 passed
0
0
```

### STOP rule

STOP and file the R6 blocker if: any count above differs; `required_clean_shadow_cycles` in the contract is absent or is not an integer ≥ 1.
**Do not add an enablement entry in this task.** Enabling a class is a registry-change-lane edit made by L0 with a linked decision record (§26.4), never a task in this plan.

---

## L3-02-08 — Level 3: the auto-repair executor

**Size:** L **Depends on:** T05, T06, T07, DEC-L3-02-03
**Spec basis:** §53.2 Level 3 — *"Reconcile actual state back to declared state automatically, then record the repair."* §53.3 (the four prohibitions and the stricter-only rule). §26.4 (repairs write under the reconciler credential and are logged as repair records). §28.1 (the compensating action must be named). §12.4 / AT-018 / AT-036 (expiry revocation without human action). AT-037 (an exception that cannot be auto-revoked becomes Blocking drift).

The executor is a **four-gate pipeline**. Every gate must pass; a refusal at any gate produces a Level 2 raise or a Level 4 finding, never a write.

| Gate | Question | Source | Failure route |
| --- | --- | --- | --- |
| G1 | Is this one of the five permitted classes? | `reconciler/repair/registry.py` (T06) | refuse; Level 4 finding |
| G2 | Is that class live for this product right now? | `reconciler/repair/enablement.py` (T07) | refuse; no write, finding stays open |
| G3 | Does the stricter-only rule permit it? | `validators/drift/stricter_only.py` (T05) | `RAISE_LEVEL_2_ACTUAL_STRICTER` → Level 2; the two REFUSED verdicts → Level 4 |
| G4 | Was a pre-repair snapshot captured for the named compensating action? | executor | refuse; no write |

### Files created

- `reconciler/repair/executor.py`
- `reconciler/levels/level3_repair.py`
- `reconciler/levels/tests/test_level3_repair.py`

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
git fetch origin && git checkout integration && git pull --ff-only
git checkout -b lane/3/02-t08-level3-repair
cat > reconciler/repair/executor.py <<'PYEOF'
"""The Level-3 repair executor (spec 53.2, 53.3, 26.4, 28.1).

Four gates, in this order, none skippable:
  G1 permitted class          (53.2 closed list)
  G2 class live for product   (99.6 risk 6, 26.4/D93)
  G3 stricter-only verdict    (53.3, invariant 81)
  G4 pre-repair snapshot      (28.1 compensating action)

A repair that passes all four writes, then records. A repair that fails any
gate never writes and returns the route its failure takes.
"""
from __future__ import annotations

import dataclasses
import datetime as _dt
import pathlib
from typing import Any, Callable

import yaml

from reconciler.repair import enablement, registry
from validators.drift.stricter_only import Restriction, Verdict, evaluate, is_permitted

_RECORDS_CONTRACT = pathlib.Path("contracts/reconciler/records.yaml")


class ExecutorError(RuntimeError):
    pass


@dataclasses.dataclass(frozen=True)
class RepairRequest:
    finding_id: str
    class_id: str
    product: str
    repository: str
    declared_strength: int | None
    actual_strength: int | None


@dataclasses.dataclass(frozen=True)
class RepairOutcome:
    finding_id: str
    class_id: str
    product: str
    wrote: bool
    route: str          # "repaired" | "level_2_warn" | "level_4_block" | "held"
    reason: str
    repair_record: dict[str, Any] | None


def _records_contract() -> dict[str, Any]:
    if not _RECORDS_CONTRACT.exists():
        raise ExecutorError("DEC-L3-02-03 unresolved: contracts/reconciler/records.yaml absent")
    return yaml.safe_load(_RECORDS_CONTRACT.read_text(encoding="utf-8"))


def execute(
    req: RepairRequest,
    canary_products: list[str],
    snapshot_fn: Callable[[RepairRequest], dict[str, Any] | None],
    apply_fn: Callable[[RepairRequest], None],
    now: _dt.datetime,
) -> RepairOutcome:
    # G1 - permitted class
    try:
        cls = registry.get(req.class_id)
    except registry.RepairClassError as exc:
        return RepairOutcome(req.finding_id, req.class_id, req.product, False,
                             "level_4_block", f"G1 not a permitted repair class: {exc}", None)

    # G2 - live for this product
    if not enablement.is_live(req.class_id, req.product, canary_products):
        return RepairOutcome(req.finding_id, req.class_id, req.product, False,
                             "held", "G2 repair class is not live for this product", None)

    # G3 - stricter-only
    verdict = evaluate(
        cls["control_kind"],
        Restriction(cls["control_kind"], req.declared_strength),
        Restriction(cls["control_kind"], req.actual_strength),
        cls["target"],
    )
    if verdict is Verdict.RAISE_LEVEL_2_ACTUAL_STRICTER:
        return RepairOutcome(req.finding_id, req.class_id, req.product, False,
                             "level_2_warn",
                             "G3 section 53.3: actual is stricter than declared; raised for human judgment",
                             None)
    if not is_permitted(verdict):
        return RepairOutcome(req.finding_id, req.class_id, req.product, False,
                             "level_4_block", f"G3 refused: {verdict.value}", None)

    # G4 - compensating-action snapshot (section 28.1)
    snapshot = snapshot_fn(req)
    if not snapshot:
        return RepairOutcome(req.finding_id, req.class_id, req.product, False,
                             "held",
                             "G4 no pre-repair snapshot; the named compensating action would be unusable",
                             None)

    apply_fn(req)

    contract = _records_contract()
    record = {
        "record_schema_version": contract["record_schema_version"],
        "schema_id": contract["repair_record_schema_id"],
        "store_path": contract["repair_record_path"],
        "finding_id": req.finding_id,
        "repair_class": req.class_id,
        "product": req.product,
        "repository": req.repository,
        "level": "level_3_auto_repair",
        "declared_strength": req.declared_strength,
        "actual_strength": req.actual_strength,
        "verdict": verdict.value,
        "reversible_class": cls["reversible_class"],
        "compensating_action": cls["compensating_action"],
        "pre_repair_snapshot": snapshot,
        "repaired_at": now.isoformat(),
        "written_by": "reconciler",
    }
    return RepairOutcome(req.finding_id, req.class_id, req.product, True,
                         "repaired", "all four gates passed", record)
PYEOF
cat > reconciler/levels/level3_repair.py <<'PYEOF'
"""Level 3 - Auto-repair (spec 53.2).

Behaviour: "Reconcile actual state back to declared state automatically,
then record the repair."

This module is a thin router. All policy is in reconciler/repair/. It exists
so that the level surface matches section 53.2 one-to-one.
"""
from __future__ import annotations

from typing import Any

from reconciler.repair.executor import RepairOutcome


def summarise(outcomes: list[RepairOutcome]) -> dict[str, Any]:
    return {
        "level": "level_3_auto_repair",
        "repaired": [o.finding_id for o in outcomes if o.wrote],
        "raised_level_2": [o.finding_id for o in outcomes if o.route == "level_2_warn"],
        "raised_level_4": [o.finding_id for o in outcomes if o.route == "level_4_block"],
        "held": [o.finding_id for o in outcomes if o.route == "held"],
        "repair_records": [o.repair_record for o in outcomes if o.repair_record],
    }
PYEOF
cat > reconciler/levels/tests/test_level3_repair.py <<'PYEOF'
import datetime as dt

import pytest

from reconciler.levels import level3_repair as l3
from reconciler.repair import enablement, executor

NOW = dt.datetime(2026, 6, 1, tzinfo=dt.timezone.utc)
WRITES = []


def _snapshot(req):
    return {"before": "captured"}


def _apply(req):
    WRITES.append(req.finding_id)


def _req(class_id="branch-protection-reapply", declared=2, actual=1, fid="F-1"):
    return executor.RepairRequest(
        finding_id=fid, class_id=class_id, product="alpha", repository="org/alpha",
        declared_strength=declared, actual_strength=actual,
    )


@pytest.fixture(autouse=True)
def _clear():
    WRITES.clear()
    yield
    WRITES.clear()


def _live(monkeypatch, class_id="branch-protection-reapply", state="fleet"):
    monkeypatch.setattr(
        enablement, "load_state",
        lambda: {"state_version": 1, "enablements": [{"class_id": class_id, "state": state}]},
    )


def test_g1_unknown_class_never_writes_and_routes_to_level_4():
    out = executor.execute(_req(class_id="rotate-secrets"), ["alpha"], _snapshot, _apply, NOW)
    assert out.wrote is False and out.route == "level_4_block" and WRITES == []


def test_g2_disabled_class_never_writes(monkeypatch):
    monkeypatch.setattr(enablement, "load_state", lambda: {"state_version": 1, "enablements": []})
    out = executor.execute(_req(), ["alpha"], _snapshot, _apply, NOW)
    assert out.wrote is False and out.route == "held" and WRITES == []


def test_g3_actual_stricter_routes_to_level_2_and_never_writes(monkeypatch):
    _live(monkeypatch)
    out = executor.execute(_req(declared=1, actual=4), ["alpha"], _snapshot, _apply, NOW)
    assert out.wrote is False and out.route == "level_2_warn" and WRITES == []


def test_g3_incomparable_routes_to_level_4_and_never_writes(monkeypatch):
    _live(monkeypatch)
    out = executor.execute(_req(declared=None, actual=1), ["alpha"], _snapshot, _apply, NOW)
    assert out.wrote is False and out.route == "level_4_block" and WRITES == []


def test_g4_missing_snapshot_never_writes(monkeypatch):
    _live(monkeypatch)
    out = executor.execute(_req(), ["alpha"], lambda r: None, _apply, NOW)
    assert out.wrote is False and out.route == "held" and WRITES == []


def test_all_gates_pass_writes_once_and_records(monkeypatch):
    _live(monkeypatch)
    out = executor.execute(_req(), ["alpha"], _snapshot, _apply, NOW)
    assert out.wrote is True and WRITES == ["F-1"]
    assert out.repair_record["compensating_action"]
    assert out.repair_record["level"] == "level_3_auto_repair"
    assert out.repair_record["written_by"] == "reconciler"


def test_repair_is_idempotent_at_equal_strength(monkeypatch):
    _live(monkeypatch)
    out = executor.execute(_req(declared=2, actual=2), ["alpha"], _snapshot, _apply, NOW)
    assert out.wrote is True


def test_canary_state_holds_the_fleet(monkeypatch):
    _live(monkeypatch, state="canary")
    on = executor.execute(_req(fid="F-C"), ["alpha"], _snapshot, _apply, NOW)
    off = executor.execute(
        executor.RepairRequest("F-F", "branch-protection-reapply", "beta", "org/beta", 2, 1),
        ["alpha"], _snapshot, _apply, NOW,
    )
    assert on.wrote is True and off.wrote is False and off.route == "held"


def test_summary_partitions_every_outcome(monkeypatch):
    _live(monkeypatch)
    outs = [
        executor.execute(_req(fid="A"), ["alpha"], _snapshot, _apply, NOW),
        executor.execute(_req(fid="B", declared=1, actual=4), ["alpha"], _snapshot, _apply, NOW),
        executor.execute(_req(fid="C", class_id="rotate-secrets"), ["alpha"], _snapshot, _apply, NOW),
    ]
    s = l3.summarise(outs)
    assert s["repaired"] == ["A"] and s["raised_level_2"] == ["B"] and s["raised_level_4"] == ["C"]
PYEOF
python -m pytest reconciler/levels/tests/test_level3_repair.py -q 2>&1 | grep -oE '^[0-9]+ passed'
git add reconciler/repair/executor.py reconciler/levels/level3_repair.py reconciler/levels/tests/test_level3_repair.py
git commit -m "L3-02-08: Level 3 auto-repair executor - four gates, no write without all four (53.2, 53.3, 26.4, 28.1)"
git rebase origin/integration && git push -u origin lane/3/02-t08-level3-repair
```

### Acceptance criteria

| # | Criterion | Proving command | Required output |
| --- | --- | --- | --- |
| A1 | 9 tests pass | `cd "$(git rev-parse --show-toplevel)" && python -m pytest reconciler/levels/tests/test_level3_repair.py -q 2>&1 \| grep -oE '^[0-9]+ passed'` | `9 passed` |
| A2 | The executor has exactly one call site for the write function | `cd "$(git rev-parse --show-toplevel)" && grep -c 'apply_fn(req)' reconciler/repair/executor.py` | `1` |
| A3 | The executor imports the stricter-only comparator | `cd "$(git rev-parse --show-toplevel)" && grep -c 'from validators.drift.stricter_only import' reconciler/repair/executor.py` | `1` |
| A4 | No prohibited target is reachable from any repair class | `cd "$(git rev-parse --show-toplevel)" && python -c "
from reconciler.repair import registry
from validators.drift.stricter_only import PROHIBITED_TARGETS
print(sum(1 for c in registry.load() if c['target'] in PROHIBITED_TARGETS))"` | `0` |
| A5 | No foreign path touched | see SELF-VERIFY | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
python -m pytest reconciler/levels/tests/test_level3_repair.py -q 2>&1 | grep -oE '^[0-9]+ passed'
grep -c 'apply_fn(req)' reconciler/repair/executor.py
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler|tools/provision|validators/drift)/'
```

Expected output:

```
9 passed
1
0
```

### STOP rule

STOP and file the R6 blocker if: the test count is not `9 passed`; `grep -c 'apply_fn(req)'` is not `1`; any test shows a write occurring on a gate failure.
**Never add a bypass, an override flag, a `force=True`, or an early `apply_fn` call.** Never reorder the four gates. Never let a `REFUSED_*` verdict fall through to a write.

---

## L3-02-09 — Reconciler write scope narrowed to `derived/**`

**Size:** M **Depends on:** T02
**Spec basis:** D93 verbatim — *"The reconciler's own write scope is narrowed to generated `derived/**` files the registries reference, so a machine write to a registry becomes detectable Blocking drift rather than an in-scope write."* §40.1 — the control-plane repository admits *"None, except the reconciler's declared repair scope (Section 26.4)"* as machine write. §98.2 completion check — *"a reconciler write outside its declared scope is Blocking drift."* D89 — *"no machine identity is a bypass actor on it."*

The point of D93 is negative: because the scope is narrow, a registry write **falls outside it and is therefore detectable**. This task builds both halves — the declared scope, and the detector that fires when a commit by the reconciler identity touches anything else.

### Files created

- `reconciler/credential/write_scope.yaml`
- `validators/drift/write_scope_guard.py`
- `validators/drift/tests/test_write_scope_guard.py`

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
git fetch origin && git checkout integration && git pull --ff-only
git checkout -b lane/3/02-t09-write-scope
cat > reconciler/credential/write_scope.yaml <<'EOF'
# The reconciler credential's declared write scope on the control-plane
# repository.
#
# D93: "The reconciler's own write scope is narrowed to generated derived/**
# files the registries reference, so a machine write to a registry becomes
# detectable Blocking drift rather than an in-scope write."
#
# Section 40.1: the control-plane repository admits no machine write path
# except "the reconciler's declared repair scope (Section 26.4)".
# D89: no machine identity is a bypass actor on this repository.
#
# The allow list is exactly one prefix. Widening it is a governance act.
scope_version: 1
spec_refs: ["D93", "40.1", "26.4", "98.2"]

control_plane_repository:
  allowed_path_prefixes:
    - "derived/"
  # Any path outside the allow list, written by the reconciler identity, is
  # Blocking drift. Registries are listed explicitly so the finding names the
  # file rather than only the prefix.
  named_out_of_scope_paths:
    - "people.yaml"
    - "roles.yaml"
    - "topology.yaml"
    - "platform.yaml"
    - "exceptions.yaml"
    - "policies.yaml"
    - "os-health.yaml"
    - "assets.yaml"
    - "tools.yaml"
    - "economics.yaml"
    - "patterns.yaml"
    - "platform-roadmap.yaml"
    - "ai-toolchain.yaml"
  out_of_scope_drift_class: blocking

records_repository:
  # Section 40.1: the records-writer credential is scoped to the records
  # repository alone; the reconciler holds no content write there.
  allowed_path_prefixes: []
  out_of_scope_drift_class: blocking

product_repositories:
  # Section 40.1: check-run write only. A check run "writes no repository
  # content, approves nothing, and satisfies no gate a human is required to
  # satisfy."
  allowed_path_prefixes: []
  check_run_write: true
  out_of_scope_drift_class: blocking
EOF
cat > validators/drift/write_scope_guard.py <<'PYEOF'
"""Reconciler write-scope guard (D93, spec 40.1, 98.2).

D93 narrows the reconciler's write scope to generated derived/** files so
that a machine write to a registry "becomes detectable Blocking drift rather
than an in-scope write". This module is that detector.

It is deliberately a whitelist: an unrecognised path is out of scope, not
in scope. Section 64.2, fail closed.
"""
from __future__ import annotations

import dataclasses
import pathlib
from typing import Any

import yaml

_SCOPE = pathlib.Path("reconciler/credential/write_scope.yaml")

CONTROL_PLANE = "control_plane_repository"
RECORDS = "records_repository"
PRODUCT = "product_repositories"


class ScopeError(RuntimeError):
    pass


@dataclasses.dataclass(frozen=True)
class ScopeFinding:
    repository_kind: str
    path: str
    author: str
    drift_class: str
    reason: str


def load_scope() -> dict[str, Any]:
    return yaml.safe_load(_SCOPE.read_text(encoding="utf-8"))


def in_scope(repository_kind: str, path: str) -> bool:
    scope = load_scope()
    if repository_kind not in scope:
        raise ScopeError(f"unknown repository kind: {repository_kind}")
    prefixes = scope[repository_kind]["allowed_path_prefixes"] or []
    return any(path.startswith(p) for p in prefixes)


def check_commit(
    repository_kind: str,
    changed_paths: list[str],
    author: str,
    reconciler_identity: str,
) -> list[ScopeFinding]:
    """Return a Blocking finding for every out-of-scope path written by the
    reconciler identity. Returns [] for any other author - this guard is
    about the reconciler's own writes only.
    """
    if author != reconciler_identity:
        return []
    scope = load_scope()
    cls = scope[repository_kind]["out_of_scope_drift_class"]
    named = set(scope[repository_kind].get("named_out_of_scope_paths") or [])
    findings = []
    for path in changed_paths:
        if in_scope(repository_kind, path):
            continue
        reason = (
            "D93: registry write by the reconciler identity"
            if path in named
            else "D93: write outside the declared derived/** repair scope"
        )
        findings.append(ScopeFinding(repository_kind, path, author, cls, reason))
    return findings
PYEOF
cat > validators/drift/tests/test_write_scope_guard.py <<'PYEOF'
import pytest

from validators.drift import write_scope_guard as g

REC = "reconciler-app[bot]"


def test_derived_write_is_in_scope():
    assert g.in_scope(g.CONTROL_PLANE, "derived/codeowners/alpha.txt") is True


def test_registry_write_is_out_of_scope():
    assert g.in_scope(g.CONTROL_PLANE, "people.yaml") is False


def test_registry_write_by_reconciler_is_blocking():
    out = g.check_commit(g.CONTROL_PLANE, ["people.yaml"], REC, REC)
    assert len(out) == 1
    assert out[0].drift_class == "blocking"
    assert "registry write" in out[0].reason


def test_every_named_registry_is_detected():
    named = g.load_scope()[g.CONTROL_PLANE]["named_out_of_scope_paths"]
    out = g.check_commit(g.CONTROL_PLANE, named, REC, REC)
    assert len(out) == len(named)
    assert all(f.drift_class == "blocking" for f in out)


def test_unknown_path_fails_closed():
    out = g.check_commit(g.CONTROL_PLANE, ["some/new/thing.yaml"], REC, REC)
    assert len(out) == 1 and out[0].drift_class == "blocking"


def test_mixed_commit_reports_only_the_out_of_scope_paths():
    out = g.check_commit(g.CONTROL_PLANE, ["derived/x.txt", "roles.yaml"], REC, REC)
    assert [f.path for f in out] == ["roles.yaml"]


def test_other_authors_are_not_this_guards_business():
    assert g.check_commit(g.CONTROL_PLANE, ["people.yaml"], "a-human", REC) == []


def test_reconciler_has_no_content_write_on_the_records_repository():
    assert g.load_scope()[g.RECORDS]["allowed_path_prefixes"] in ([], None)
    out = g.check_commit(g.RECORDS, ["records/anything.yaml"], REC, REC)
    assert len(out) == 1 and out[0].drift_class == "blocking"


def test_product_repositories_allow_check_run_write_only():
    prod = g.load_scope()[g.PRODUCT]
    assert prod["check_run_write"] is True
    assert prod["allowed_path_prefixes"] in ([], None)


def test_control_plane_allow_list_is_exactly_one_prefix():
    assert g.load_scope()[g.CONTROL_PLANE]["allowed_path_prefixes"] == ["derived/"]


def test_unknown_repository_kind_raises():
    with pytest.raises(g.ScopeError):
        g.in_scope("something_else", "derived/x")
PYEOF
python -m pytest validators/drift/tests/test_write_scope_guard.py -q 2>&1 | grep -oE '^[0-9]+ passed'
git add reconciler/credential/write_scope.yaml validators/drift/write_scope_guard.py validators/drift/tests/test_write_scope_guard.py
git commit -m "L3-02-09: reconciler write scope narrowed to derived/** with out-of-scope detector (D93, 40.1, 98.2)"
git rebase origin/integration && git push -u origin lane/3/02-t09-write-scope
```

### Acceptance criteria

| # | Criterion | Proving command | Required output |
| --- | --- | --- | --- |
| A1 | 11 tests pass | `cd "$(git rev-parse --show-toplevel)" && python -m pytest validators/drift/tests/test_write_scope_guard.py -q 2>&1 \| grep -oE '^[0-9]+ passed'` | `11 passed` |
| A2 | Control-plane allow list is exactly `derived/` | `cd "$(git rev-parse --show-toplevel)" && python -c "from validators.drift import write_scope_guard as g;print(g.load_scope()[g.CONTROL_PLANE]['allowed_path_prefixes'])"` | `['derived/']` |
| A3 | A registry write by the reconciler is Blocking | `cd "$(git rev-parse --show-toplevel)" && python -c "from validators.drift import write_scope_guard as g;print(g.check_commit(g.CONTROL_PLANE,['people.yaml'],'r','r')[0].drift_class)"` | `blocking` |
| A4 | The reconciler holds no content write on the records repository | `cd "$(git rev-parse --show-toplevel)" && python -c "from validators.drift import write_scope_guard as g;print(len(g.load_scope()[g.RECORDS]['allowed_path_prefixes'] or []))"` | `0` |
| A5 | No foreign path touched | see SELF-VERIFY | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
python -m pytest validators/drift/tests/test_write_scope_guard.py -q 2>&1 | grep -oE '^[0-9]+ passed'
python -c "from validators.drift import write_scope_guard as g;print(g.load_scope()[g.CONTROL_PLANE]['allowed_path_prefixes'])"
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler|tools/provision|validators/drift)/'
```

Expected output:

```
11 passed
['derived/']
0
```

### STOP rule

STOP and file the R6 blocker if: any output above differs; you find an existing reconciler code path that writes outside `derived/` on the control-plane repository (that is a Phase-1 defect and a Blocking finding in its own right — report it, do not fix it here).
**Never add a second prefix to `allowed_path_prefixes`.** Never add a registry path to an allow list. Never give the reconciler content write on the records repository.

---

## L3-02-10 — AT-110 credential-boundedness harness

**Size:** M **Depends on:** T09
**Spec basis:** AT-110 verbatim — *"From the reconciler's own credential, six attempts are made — a write to a GitHub Actions secret, a write to an environment, a workflow-file change, an organisation-settings change, a `records/**` write, and any Layer B access — and all six fail; the credential then still completes a normal reconciliation run. Executed for real at the phase that builds the reconciler and re-executed at every rotation."* §99.6 risk 6. §40.3 second boundary.

The harness is written here as an **executable, ordered checklist with recorded results**. It is not a unit test: AT-110 says *executed for real*. The harness therefore runs in two modes — `--dry-run` (structure only, runs in CI) and `--live` (against the real credential, run by a DevOps-capability holder).

### Files created

- `reconciler/credential/bound_check.py`
- `reconciler/credential/attempts.yaml`
- `reconciler/credential/tests/test_bound_check.py`

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
git fetch origin && git checkout integration && git pull --ff-only
git checkout -b lane/3/02-t10-at110
cat > reconciler/credential/attempts.yaml <<'EOF'
# AT-110 - "The reconciler credential is provably bounded".
#
# Six attempts, verbatim from AT-110, in the order the test states them.
# ALL SIX MUST FAIL. The credential must then still complete a normal
# reconciliation run.
#
# "Executed for real at the phase that builds the reconciler and re-executed
# at every rotation, on the same gate as 40.1's clean-reconciliation
# condition."
attempts_version: 1
acceptance_test: "AT-110"

attempts:
  - id: A1
    description: "a write to a GitHub Actions secret"
    expect: fail
  - id: A2
    description: "a write to an environment"
    expect: fail
  - id: A3
    description: "a workflow-file change"
    expect: fail
  - id: A4
    description: "an organisation-settings change"
    expect: fail
  - id: A5
    description: "a records/** write"
    expect: fail
  - id: A6
    description: "any Layer B access"
    expect: fail

post_condition:
  id: A7
  description: "the credential then still completes a normal reconciliation run"
  expect: pass
EOF
cat > reconciler/credential/bound_check.py <<'PYEOF'
"""AT-110 harness: the reconciler credential is provably bounded.

Two modes:
  --dry-run  validate the checklist's structure; safe in CI
  --live     execute the six attempts for real against the reconciler
             credential and assert all six fail, then assert a normal
             reconciliation run still completes

The six attempt implementations are supplied by the caller as a mapping of
attempt id -> callable. Each callable MUST raise on success of the attempt,
i.e. the harness treats "the attempt succeeded" as a FAILED test.
"""
from __future__ import annotations

import argparse
import pathlib
import sys
from typing import Any, Callable

import yaml

_ATTEMPTS = pathlib.Path(__file__).with_name("attempts.yaml")

EXPECTED_IDS = ("A1", "A2", "A3", "A4", "A5", "A6")


class BoundCheckError(RuntimeError):
    pass


def load() -> dict[str, Any]:
    data = yaml.safe_load(_ATTEMPTS.read_text(encoding="utf-8"))
    ids = tuple(a["id"] for a in data["attempts"])
    if ids != EXPECTED_IDS:
        raise BoundCheckError(f"AT-110 requires exactly six attempts {EXPECTED_IDS}, got {ids}")
    if any(a["expect"] != "fail" for a in data["attempts"]):
        raise BoundCheckError("AT-110: all six attempts must expect 'fail'")
    if data["post_condition"]["expect"] != "pass":
        raise BoundCheckError("AT-110: the post-condition run must expect 'pass'")
    return data


def run_live(
    attempt_fns: dict[str, Callable[[], bool]],
    reconciliation_run_fn: Callable[[], bool],
) -> dict[str, Any]:
    """Execute AT-110. Returns a result payload; raises on any breach."""
    data = load()
    missing = [a["id"] for a in data["attempts"] if a["id"] not in attempt_fns]
    if missing:
        raise BoundCheckError(f"AT-110: no implementation supplied for {missing}")
    results = []
    for a in data["attempts"]:
        succeeded = bool(attempt_fns[a["id"]]())
        results.append({"id": a["id"], "description": a["description"], "attempt_succeeded": succeeded})
        if succeeded:
            raise BoundCheckError(
                f"AT-110 BREACH: attempt {a['id']} ({a['description']}) SUCCEEDED; "
                "the reconciler credential is not bounded"
            )
    if not reconciliation_run_fn():
        raise BoundCheckError(
            "AT-110: all six attempts failed but the credential no longer completes a "
            "normal reconciliation run; per 40.1 the credential has been broken, not bounded"
        )
    return {"acceptance_test": "AT-110", "attempts": results, "post_condition_passed": True}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="bound_check")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args(argv)
    if args.dry_run:
        load()
        print("AT-110 checklist OK: 6 attempts, all expect fail, post-condition expects pass")
        return 0
    print("--live requires attempt implementations; call run_live() from the rotation runbook")
    return 2


if __name__ == "__main__":
    sys.exit(main())
PYEOF
cat > reconciler/credential/tests/test_bound_check.py <<'PYEOF'
import pytest

from reconciler.credential import bound_check as bc


def test_exactly_six_attempts_in_at110_order():
    assert tuple(a["id"] for a in bc.load()["attempts"]) == bc.EXPECTED_IDS


def test_the_six_descriptions_are_the_at110_six():
    descs = [a["description"] for a in bc.load()["attempts"]]
    assert descs == [
        "a write to a GitHub Actions secret",
        "a write to an environment",
        "a workflow-file change",
        "an organisation-settings change",
        "a records/** write",
        "any Layer B access",
    ]


def test_all_six_must_fail():
    assert all(a["expect"] == "fail" for a in bc.load()["attempts"])


def test_post_condition_is_a_normal_run():
    assert bc.load()["post_condition"]["expect"] == "pass"


def test_all_six_failing_plus_working_run_passes():
    fns = {i: (lambda: False) for i in bc.EXPECTED_IDS}
    out = bc.run_live(fns, lambda: True)
    assert out["post_condition_passed"] is True
    assert len(out["attempts"]) == 6


def test_any_attempt_succeeding_is_a_breach():
    for breach in bc.EXPECTED_IDS:
        fns = {i: (lambda: False) for i in bc.EXPECTED_IDS}
        fns[breach] = lambda: True
        with pytest.raises(bc.BoundCheckError) as exc:
            bc.run_live(fns, lambda: True)
        assert "BREACH" in str(exc.value)


def test_broken_credential_is_not_a_bounded_credential():
    fns = {i: (lambda: False) for i in bc.EXPECTED_IDS}
    with pytest.raises(bc.BoundCheckError):
        bc.run_live(fns, lambda: False)


def test_missing_implementation_is_refused():
    fns = {i: (lambda: False) for i in bc.EXPECTED_IDS if i != "A4"}
    with pytest.raises(bc.BoundCheckError):
        bc.run_live(fns, lambda: True)


def test_dry_run_exits_zero():
    assert bc.main(["--dry-run"]) == 0
PYEOF
python -m pytest reconciler/credential/tests/test_bound_check.py -q 2>&1 | grep -oE '^[0-9]+ passed'
python -m reconciler.credential.bound_check --dry-run
git add reconciler/credential/attempts.yaml reconciler/credential/bound_check.py reconciler/credential/tests/test_bound_check.py
git commit -m "L3-02-10: AT-110 credential-boundedness harness - six attempts, all must fail"
git rebase origin/integration && git push -u origin lane/3/02-t10-at110
```

### Acceptance criteria

| # | Criterion | Proving command | Required output |
| --- | --- | --- | --- |
| A1 | 9 tests pass | `cd "$(git rev-parse --show-toplevel)" && python -m pytest reconciler/credential/tests/test_bound_check.py -q 2>&1 \| grep -oE '^[0-9]+ passed'` | `9 passed` |
| A2 | Dry run reports the AT-110 shape | `cd "$(git rev-parse --show-toplevel)" && python -m reconciler.credential.bound_check --dry-run` | `AT-110 checklist OK: 6 attempts, all expect fail, post-condition expects pass` |
| A3 | Exactly six attempts | `cd "$(git rev-parse --show-toplevel)" && grep -c '^  - id: A' reconciler/credential/attempts.yaml` | `6` |
| A4 | No foreign path touched | see SELF-VERIFY | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
python -m pytest reconciler/credential/tests/test_bound_check.py -q 2>&1 | grep -oE '^[0-9]+ passed'
python -m reconciler.credential.bound_check --dry-run
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler|tools/provision|validators/drift)/'
```

Expected output:

```
9 passed
AT-110 checklist OK: 6 attempts, all expect fail, post-condition expects pass
0
```

### STOP rule

STOP and file the R6 blocker if: any output above differs; you are asked to run `--live` (that requires the fifth-tier credential on the operations VM and a DevOps-capability holder — it is not an executor action).
**Do not add a seventh attempt and do not remove one.** Do not soften a breach into a warning. Do not implement the six attempt callables here — they belong to the rotation runbook, which L5 owns.

---

## L3-02-11 — Level 4: Block, via the blocking check run (D92)

**Size:** L **Depends on:** T02, T09, DEC-L3-02-02
**Spec basis:** §53.2 Level 4 — *"Fail CI or block the deployment path until resolved."* applying to *"Blocking-class drift: orphaned product, expired non-employee access still provisioned, restore test overdue, security control weakened, artifact digest mismatch, workflow-file change pushed by a machine identity"*. D92 verbatim — *"'Fails CI' was claimed for conditions that go bad without a push — a lapsed restore test, a departed owner, an expired assignment — but a required status check that last ran green stays green, so the detection existed and the blocking did not. The reconciler holds a check-run-write scope and posts a named required check on every affected repository, failing while a Blocking finding is open against that product."* §40.1 check-run scope. SIG-05 (orphan risk, Blocking), SIG-17 (restore-test currency, Blocking past), SIG-03 (permission drift, Blocking if it weakens a security control), invariant 57, AT-017, AT-037.

**The mechanism is the whole point:** the check run is re-posted on **every reconciliation run**, not on push, so a product with no pushes still goes red.

### Files created

- `reconciler/checkrun/poster.py`
- `reconciler/levels/level4_block.py`
- `reconciler/levels/tests/test_level4_block.py`

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
git fetch origin && git checkout integration && git pull --ff-only
git checkout -b lane/3/02-t11-level4-block
cat > reconciler/checkrun/poster.py <<'PYEOF'
"""The blocking check run (D92, spec 40.1, 53.2 Level 4).

D92: "The reconciler holds a check-run-write scope and posts a named required
check on every affected repository, failing while a Blocking finding is open
against that product."

The name and the publishing app identity come from
contracts/l3-reconciler.yaml (DEC-L3-02-02). Nothing here hard-codes
either. Section 40.1: the scope is "used for exactly one named check".

Non-push conditions are the reason this exists: a lapsed restore test, a
departed owner and an expired assignment change nothing in the repository,
so a required status check that last ran green stays green. This check run
is re-posted on EVERY reconciliation run, against the repository's current
default-branch head, so its conclusion tracks the finding, not the push.
"""
from __future__ import annotations

import dataclasses
import pathlib
from typing import Any, Callable

import yaml

_CONTRACT = pathlib.Path("contracts/l3-reconciler.yaml")

CONCLUSION_FAILURE = "failure"
CONCLUSION_SUCCESS = "success"


class CheckRunContractError(RuntimeError):
    pass


@dataclasses.dataclass(frozen=True)
class CheckRunPost:
    repository: str
    head_sha: str
    name: str
    conclusion: str
    title: str
    summary: str


def contract() -> dict[str, Any]:
    if not _CONTRACT.exists():
        raise CheckRunContractError(
            "DEC-L3-02-02 unresolved: contracts/l3-reconciler.yaml absent; "
            "D92 names the check but the spec does not write the name string"
        )
    data = yaml.safe_load(_CONTRACT.read_text(encoding="utf-8"))
    for key in ("blocking_check_name", "expected_app_slug"):
        if not data.get(key):
            raise CheckRunContractError(f"contracts/l3-reconciler.yaml missing key: {key}")
    return data


def build_post(repository: str, head_sha: str, open_blocking_findings: list[dict[str, Any]]) -> CheckRunPost:
    """One check-run post for one repository, from that repository's product's
    open Blocking findings. Zero findings -> success. One or more -> failure.
    """
    name = contract()["blocking_check_name"]
    if open_blocking_findings:
        rows = "\n".join(
            f"- {f['finding_id']} | {f['comparison_row']} | opened {f['first_seen']}"
            for f in open_blocking_findings
        )
        return CheckRunPost(
            repository=repository,
            head_sha=head_sha,
            name=name,
            conclusion=CONCLUSION_FAILURE,
            title=f"{len(open_blocking_findings)} open Blocking drift finding(s)",
            summary=(
                "Blocking-class drift is open against this product (spec 53.2 Level 4; D92).\n"
                "This check is re-posted on every reconciliation run and does not require a "
                "push to change state.\n\n" + rows
            ),
        )
    return CheckRunPost(
        repository=repository,
        head_sha=head_sha,
        name=name,
        conclusion=CONCLUSION_SUCCESS,
        title="No open Blocking drift",
        summary="No Blocking-class drift finding is open against this product.",
    )


def post_all(
    repositories_by_product: dict[str, list[str]],
    head_sha_fn: Callable[[str], str],
    findings_by_product: dict[str, list[dict[str, Any]]],
) -> list[CheckRunPost]:
    """Post the check on EVERY affected repository of EVERY product.

    Section 16 / AT-010: a product may have several repositories; D92 says
    "every affected repository". A product with zero open Blocking findings
    still receives a success post, so the check is always present and a
    missing check is itself visible.
    """
    posts = []
    for product, repos in sorted(repositories_by_product.items()):
        open_findings = findings_by_product.get(product, [])
        for repo in repos:
            posts.append(build_post(repo, head_sha_fn(repo), open_findings))
    return posts
PYEOF
cat > reconciler/levels/level4_block.py <<'PYEOF'
"""Level 4 - Block (spec 53.2).

Behaviour: "Fail CI or block the deployment path until resolved."
Applies to: "Blocking-class drift: orphaned product, expired non-employee
access still provisioned, restore test overdue, security control weakened,
artifact digest mismatch, workflow-file change pushed by a machine identity"

The six conditions above are transcribed as a closed set of blocking reasons
so that a finding cannot reach Level 4 under an unnamed reason.
"""
from __future__ import annotations

from typing import Any

from reconciler.checkrun import poster

# Section 53.2, Level 4 "Applies to", verbatim, in order.
BLOCKING_REASONS = (
    "orphaned product",
    "expired non-employee access still provisioned",
    "restore test overdue",
    "security control weakened",
    "artifact digest mismatch",
    "workflow-file change pushed by a machine identity",
)

# Conditions that go bad without a push (D92). Listed so the mechanism's
# purpose is testable, not merely documented.
NON_PUSH_CONDITIONS = (
    "restore test overdue",
    "orphaned product",
    "expired non-employee access still provisioned",
)


class BlockingReasonError(RuntimeError):
    pass


def validate_reason(reason: str) -> str:
    if reason not in BLOCKING_REASONS:
        raise BlockingReasonError(
            f"not a Level-4 blocking reason declared by section 53.2: {reason!r}"
        )
    return reason


def block(
    findings_by_product: dict[str, list[dict[str, Any]]],
    repositories_by_product: dict[str, list[str]],
    head_sha_fn,
) -> dict[str, Any]:
    for product, findings in findings_by_product.items():
        for f in findings:
            validate_reason(f["reason"])
    posts = poster.post_all(repositories_by_product, head_sha_fn, findings_by_product)
    return {
        "level": "level_4_block",
        "posts": posts,
        "failing_repositories": [p.repository for p in posts if p.conclusion == poster.CONCLUSION_FAILURE],
    }
PYEOF
cat > reconciler/levels/tests/test_level4_block.py <<'PYEOF'
import pytest

from reconciler.checkrun import poster
from reconciler.levels import level4_block as l4

SHA = "0" * 40


def _f(reason="restore test overdue", fid="F-1"):
    return {
        "finding_id": fid,
        "comparison_row": "product.yaml restore_tested",
        "first_seen": "2026-05-01",
        "reason": reason,
    }


def test_the_six_blocking_reasons_are_the_spec_six():
    assert l4.BLOCKING_REASONS == (
        "orphaned product",
        "expired non-employee access still provisioned",
        "restore test overdue",
        "security control weakened",
        "artifact digest mismatch",
        "workflow-file change pushed by a machine identity",
    )


def test_an_unnamed_reason_cannot_reach_level_4():
    with pytest.raises(l4.BlockingReasonError):
        l4.validate_reason("looks bad")


def test_open_blocking_finding_fails_the_check_run():
    out = l4.block({"alpha": [_f()]}, {"alpha": ["org/alpha"]}, lambda r: SHA)
    assert out["posts"][0].conclusion == poster.CONCLUSION_FAILURE
    assert out["failing_repositories"] == ["org/alpha"]


def test_no_finding_posts_success_so_the_check_is_always_present():
    out = l4.block({"alpha": []}, {"alpha": ["org/alpha"]}, lambda r: SHA)
    assert out["posts"][0].conclusion == poster.CONCLUSION_SUCCESS
    assert out["failing_repositories"] == []


def test_every_repository_of_a_multi_repo_product_is_posted():
    out = l4.block({"alpha": [_f()]}, {"alpha": ["org/a1", "org/a2", "org/a3"]}, lambda r: SHA)
    assert [p.repository for p in out["posts"]] == ["org/a1", "org/a2", "org/a3"]
    assert all(p.conclusion == poster.CONCLUSION_FAILURE for p in out["posts"])


@pytest.mark.parametrize("reason", l4.NON_PUSH_CONDITIONS)
def test_non_push_conditions_fail_the_check_without_any_push(reason):
    """D92: the condition goes bad without a push; the check must still fail."""
    out = l4.block({"alpha": [_f(reason=reason)]}, {"alpha": ["org/alpha"]}, lambda r: SHA)
    assert out["posts"][0].conclusion == poster.CONCLUSION_FAILURE


def test_check_name_comes_from_the_contract_not_from_code():
    src = open("reconciler/checkrun/poster.py", encoding="utf-8").read()
    assert 'blocking_check_name"]' in src
    assert poster.contract()["blocking_check_name"]


def test_summary_names_each_open_finding():
    out = l4.block({"alpha": [_f(fid="F-9")]}, {"alpha": ["org/alpha"]}, lambda r: SHA)
    assert "F-9" in out["posts"][0].summary


def test_products_are_posted_in_stable_order():
    out = l4.block(
        {"beta": [], "alpha": []},
        {"beta": ["org/beta"], "alpha": ["org/alpha"]},
        lambda r: SHA,
    )
    assert [p.repository for p in out["posts"]] == ["org/alpha", "org/beta"]
PYEOF
python -m pytest reconciler/levels/tests/test_level4_block.py -q 2>&1 | grep -oE '^[0-9]+ passed'
git add reconciler/checkrun/poster.py reconciler/levels/level4_block.py reconciler/levels/tests/test_level4_block.py
git commit -m "L3-02-11: Level 4 Block via the named blocking check run, re-posted every run (D92, 53.2, 40.1)"
git rebase origin/integration && git push -u origin lane/3/02-t11-level4-block
```

### Acceptance criteria

| # | Criterion | Proving command | Required output |
| --- | --- | --- | --- |
| A1 | 11 tests pass (8 named + 3 parametrised non-push cases) | `cd "$(git rev-parse --show-toplevel)" && python -m pytest reconciler/levels/tests/test_level4_block.py -q 2>&1 \| grep -oE '^[0-9]+ passed'` | `11 passed` |
| A2 | The check name is never a literal in code | `cd "$(git rev-parse --show-toplevel)" && grep -rc "$(python -c "from reconciler.checkrun import poster;print(poster.contract()['blocking_check_name'])")" reconciler/checkrun/poster.py reconciler/levels/level4_block.py \| grep -c ':0'` | `2` |
| A3 | Exactly six blocking reasons | `cd "$(git rev-parse --show-toplevel)" && python -c "from reconciler.levels import level4_block as l;print(len(l.BLOCKING_REASONS))"` | `6` |
| A4 | A non-push condition still fails the check | `cd "$(git rev-parse --show-toplevel)" && python -c "
from reconciler.levels import level4_block as l
o=l.block({'a':[{'finding_id':'F','comparison_row':'r','first_seen':'d','reason':'restore test overdue'}]},{'a':['org/a']},lambda r:'0'*40)
print(o['posts'][0].conclusion)"` | `failure` |
| A5 | No foreign path touched | see SELF-VERIFY | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
python -m pytest reconciler/levels/tests/test_level4_block.py -q 2>&1 | grep -oE '^[0-9]+ passed'
python -c "from reconciler.levels import level4_block as l;print(len(l.BLOCKING_REASONS))"
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler|tools/provision|validators/drift)/'
```

Expected output:

```
11 passed
6
0
```

### STOP rule

STOP and file the R6 blocker if: any output above differs; `contracts/l3-reconciler.yaml` is absent or either key is empty; you find a seventh blocking reason you believe is required.
**Never hard-code the check name.** Never post more than one named check from the reconciler (§40.1: "exactly one named check"). Never make the check conditional on a push event.

---

## L3-02-12 — Check-run identity guard

**Size:** S **Depends on:** T11, DEC-L3-02-02
**Spec basis:** §40.1 verbatim — *"A check run published under that name by any identity other than the reconciler is Blocking drift."* Same authorship discipline as §33.2 and D107.

### Files created

- `validators/drift/checkrun_identity_guard.py`
- `validators/drift/tests/test_checkrun_identity_guard.py`

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
git fetch origin && git checkout integration && git pull --ff-only
git checkout -b lane/3/02-t12-checkrun-identity
cat > validators/drift/checkrun_identity_guard.py <<'PYEOF'
"""Check-run identity guard (spec 40.1).

"A check run published under that name by any identity other than the
reconciler is Blocking drift."

A forged success under the blocking check's name would silently reopen a
repository the reconciler is holding closed, so this guard fires on the
identity regardless of the conclusion posted.
"""
from __future__ import annotations

import dataclasses

from reconciler.checkrun.poster import contract


@dataclasses.dataclass(frozen=True)
class IdentityFinding:
    repository: str
    check_name: str
    published_by: str
    drift_class: str
    reason: str


def check(observed_check_runs: list[dict[str, str]]) -> list[IdentityFinding]:
    """observed_check_runs: [{'repository':..., 'name':..., 'app_slug':..., 'conclusion':...}]"""
    c = contract()
    name = c["blocking_check_name"]
    expected = c["expected_app_slug"]
    findings = []
    for run in observed_check_runs:
        if run["name"] != name:
            continue
        if run["app_slug"] != expected:
            findings.append(
                IdentityFinding(
                    repository=run["repository"],
                    check_name=name,
                    published_by=run["app_slug"],
                    drift_class="blocking",
                    reason=(
                        "section 40.1: a check run published under the reconciler's named "
                        f"check by another identity ({run['app_slug']}) is Blocking drift"
                    ),
                )
            )
    return findings
PYEOF
cat > validators/drift/tests/test_checkrun_identity_guard.py <<'PYEOF'
from reconciler.checkrun.poster import contract
from validators.drift import checkrun_identity_guard as guard

NAME = contract()["blocking_check_name"]
MINE = contract()["expected_app_slug"]


def _run(app=MINE, conclusion="success", name=NAME):
    return {"repository": "org/alpha", "name": name, "app_slug": app, "conclusion": conclusion}


def test_reconciler_published_run_is_clean():
    assert guard.check([_run()]) == []


def test_foreign_identity_under_the_name_is_blocking():
    out = guard.check([_run(app="someone-else[bot]")])
    assert len(out) == 1 and out[0].drift_class == "blocking"


def test_forged_success_is_caught_not_only_forged_failure():
    assert len(guard.check([_run(app="attacker", conclusion="success")])) == 1
    assert len(guard.check([_run(app="attacker", conclusion="failure")])) == 1


def test_other_check_names_are_ignored():
    assert guard.check([_run(app="anyone", name="ci")]) == []


def test_mixed_batch_reports_only_the_foreign_ones():
    out = guard.check([_run(), _run(app="x"), _run(app="y"), _run(name="ci", app="z")])
    assert [f.published_by for f in out] == ["x", "y"]
PYEOF
python -m pytest validators/drift/tests/test_checkrun_identity_guard.py -q 2>&1 | grep -oE '^[0-9]+ passed'
git add validators/drift/checkrun_identity_guard.py validators/drift/tests/test_checkrun_identity_guard.py
git commit -m "L3-02-12: a check run under the reconciler's named check by another identity is Blocking drift (40.1)"
git rebase origin/integration && git push -u origin lane/3/02-t12-checkrun-identity
```

### Acceptance criteria

| # | Criterion | Proving command | Required output |
| --- | --- | --- | --- |
| A1 | 5 tests pass | `cd "$(git rev-parse --show-toplevel)" && python -m pytest validators/drift/tests/test_checkrun_identity_guard.py -q 2>&1 \| grep -oE '^[0-9]+ passed'` | `5 passed` |
| A2 | The guard fires on identity, not on conclusion | `cd "$(git rev-parse --show-toplevel)" && python -c "
from reconciler.checkrun.poster import contract
from validators.drift import checkrun_identity_guard as g
n=contract()['blocking_check_name']
r=lambda c:{'repository':'org/a','name':n,'app_slug':'x','conclusion':c}
print(len(g.check([r('success')])), len(g.check([r('failure')])))"` | `1 1` |
| A3 | No foreign path touched | see SELF-VERIFY | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
python -m pytest validators/drift/tests/test_checkrun_identity_guard.py -q 2>&1 | grep -oE '^[0-9]+ passed'
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler|tools/provision|validators/drift)/'
```

Expected output:

```
5 passed
0
```

### STOP rule

STOP and file the R6 blocker if: the test count is not `5 passed`; A2 does not print `1 1`; `expected_app_slug` is absent from the contract.
Never make the guard conditional on the posted conclusion.

---

## L3-02-13 — Level 5: Escalate, and the repair-class freeze

**Size:** M **Depends on:** T08, T11, DEC-L3-02-03
**Spec basis:** §53.2 Level 5 — *"Create an incident and notify the escalation role, then the Founder if unresolved within its response time."* applying to *"Production environment drift, credential exposure, repeated failed auto-repair, a repair class discovered to have written incorrect state (53.7), the reconciliation job itself failing"*. §53.7 "When the loop ran wrong" — *"freeze that repair class, enumerate its repairs in the affected window from the repair records of Section 26.4, revert or human-confirm each against the compensating action its change plan was required to name and test (Section 28.1), and mark every record produced in the window `gap-window` until re-verified."* SIG-13. D107 (a non-descendant records head is Blocking drift, Level 5).

### Files created

- `reconciler/levels/level5_escalate.py`
- `reconciler/repair/freeze.py`
- `reconciler/levels/tests/test_level5_escalate.py`

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
git fetch origin && git checkout integration && git pull --ff-only
git checkout -b lane/3/02-t13-level5-escalate
cat > reconciler/levels/level5_escalate.py <<'PYEOF'
"""Level 5 - Escalate (spec 53.2, 53.7).

Behaviour: "Create an incident and notify the escalation role, then the
Founder if unresolved within its response time."

Applies to, verbatim: "Production environment drift, credential exposure,
repeated failed auto-repair, a repair class discovered to have written
incorrect state (53.7), the reconciliation job itself failing".

D107 adds one more Level-5 condition by name: a records-repository head that
does not descend from the last anchored SHA.
"""
from __future__ import annotations

from typing import Any

# Section 53.2, Level 5 "Applies to", verbatim, in order.
ESCALATION_CONDITIONS = (
    "production environment drift",
    "credential exposure",
    "repeated failed auto-repair",
    "repair class wrote incorrect state",
    "reconciliation job failing",
)

# D107: "A non-descendant head is Blocking drift, Level 5 - the
# reconciliation-instrument failure class of Section 53.2".
D107_CONDITION = "records head does not descend from the last anchor"

ALL_CONDITIONS = ESCALATION_CONDITIONS + (D107_CONDITION,)


class EscalationError(RuntimeError):
    pass


def escalate(condition: str, evidence: dict[str, Any]) -> dict[str, Any]:
    if condition not in ALL_CONDITIONS:
        raise EscalationError(
            f"not a Level-5 escalation condition declared by section 53.2 or D107: {condition!r}"
        )
    return {
        "level": "level_5_escalate",
        "condition": condition,
        "create_incident": True,
        "notify": "escalation_role",
        "escalate_to_founder_if_unresolved": True,
        "signal": "SIG-13" if condition == "reconciliation job failing" else None,
        "evidence": evidence,
    }
PYEOF
cat > reconciler/repair/freeze.py <<'PYEOF'
"""Repair-class freeze - "When the loop ran wrong" (spec 53.7).

Section 53.7, verbatim requirements when a repair class is discovered to
have written incorrect state:

  1. freeze that repair class
  2. enumerate its repairs in the affected window from the repair records
     of section 26.4
  3. revert or human-confirm each against the compensating action its change
     plan was required to name and test (section 28.1)
  4. mark every record produced in the window `gap-window` until re-verified

Plus 53.7's standing rule: "a gap-window record is not evidence for any gate
until re-verification clears the mark".
"""
from __future__ import annotations

import dataclasses
from typing import Any

from reconciler.repair import registry

GAP_WINDOW_MARK = "gap-window"


@dataclasses.dataclass(frozen=True)
class FreezePlan:
    class_id: str
    frozen: bool
    window_start: str
    window_end: str
    repairs_in_window: list[dict[str, Any]]
    disposition_required: list[str]   # finding ids needing revert or human confirmation
    marked_gap_window: list[str]      # record ids marked
    escalation_condition: str


def plan(
    class_id: str,
    window_start: str,
    window_end: str,
    repair_records: list[dict[str, Any]],
) -> FreezePlan:
    registry.get(class_id)  # a freeze names one of the five classes or nothing
    in_window = [
        r
        for r in repair_records
        if r["repair_class"] == class_id and window_start <= r["repaired_at"] <= window_end
    ]
    for r in in_window:
        if not r.get("compensating_action"):
            raise ValueError(
                f"repair record {r['finding_id']} carries no compensating action; "
                "section 28.1 required it to be named and tested"
            )
    return FreezePlan(
        class_id=class_id,
        frozen=True,
        window_start=window_start,
        window_end=window_end,
        repairs_in_window=in_window,
        disposition_required=[r["finding_id"] for r in in_window],
        marked_gap_window=[r["finding_id"] for r in in_window],
        escalation_condition="repair class wrote incorrect state",
    )


def is_gate_evidence(record: dict[str, Any]) -> bool:
    """53.7: a gap-window record is not evidence for any gate until re-verified."""
    return record.get("mark") != GAP_WINDOW_MARK
PYEOF
cat > reconciler/levels/tests/test_level5_escalate.py <<'PYEOF'
import pytest

from reconciler.levels import level5_escalate as l5
from reconciler.repair import freeze


def test_the_five_conditions_are_the_spec_five():
    assert l5.ESCALATION_CONDITIONS == (
        "production environment drift",
        "credential exposure",
        "repeated failed auto-repair",
        "repair class wrote incorrect state",
        "reconciliation job failing",
    )


def test_d107_non_descendant_head_is_a_level_5_condition():
    out = l5.escalate(l5.D107_CONDITION, {"head": "abc", "anchor": "def"})
    assert out["level"] == "level_5_escalate"


def test_unnamed_condition_is_refused():
    with pytest.raises(l5.EscalationError):
        l5.escalate("something odd", {})


def test_escalation_creates_an_incident_and_notifies_the_escalation_role():
    out = l5.escalate("credential exposure", {})
    assert out["create_incident"] is True
    assert out["notify"] == "escalation_role"
    assert out["escalate_to_founder_if_unresolved"] is True


def test_reconciliation_job_failing_carries_sig_13():
    assert l5.escalate("reconciliation job failing", {})["signal"] == "SIG-13"


def _rec(fid, cls="branch-protection-reapply", at="2026-06-05"):
    return {
        "finding_id": fid,
        "repair_class": cls,
        "repaired_at": at,
        "compensating_action": "re-apply the pre-repair protection JSON",
    }


def test_freeze_enumerates_only_that_class_in_that_window():
    recs = [
        _rec("A", at="2026-06-05"),
        _rec("B", at="2026-07-05"),
        _rec("C", cls="codeowners-regeneration", at="2026-06-05"),
    ]
    p = freeze.plan("branch-protection-reapply", "2026-06-01", "2026-06-30", recs)
    assert [r["finding_id"] for r in p.repairs_in_window] == ["A"]


def test_freeze_freezes_and_routes_to_the_level_5_condition():
    p = freeze.plan("branch-protection-reapply", "2026-06-01", "2026-06-30", [_rec("A")])
    assert p.frozen is True
    assert p.escalation_condition in l5.ESCALATION_CONDITIONS


def test_every_in_window_repair_needs_disposition_and_is_marked():
    p = freeze.plan("branch-protection-reapply", "2026-06-01", "2026-06-30", [_rec("A"), _rec("B")])
    assert p.disposition_required == ["A", "B"]
    assert p.marked_gap_window == ["A", "B"]


def test_a_repair_without_a_compensating_action_is_refused():
    bad = _rec("A")
    bad["compensating_action"] = ""
    with pytest.raises(ValueError):
        freeze.plan("branch-protection-reapply", "2026-06-01", "2026-06-30", [bad])


def test_gap_window_record_is_not_gate_evidence():
    assert freeze.is_gate_evidence({"mark": freeze.GAP_WINDOW_MARK}) is False
    assert freeze.is_gate_evidence({"mark": None}) is True


def test_freeze_of_an_unknown_class_is_refused():
    with pytest.raises(Exception):
        freeze.plan("rotate-secrets", "2026-06-01", "2026-06-30", [])
PYEOF
python -m pytest reconciler/levels/tests/test_level5_escalate.py -q 2>&1 | grep -oE '^[0-9]+ passed'
git add reconciler/levels/level5_escalate.py reconciler/repair/freeze.py reconciler/levels/tests/test_level5_escalate.py
git commit -m "L3-02-13: Level 5 Escalate and the 53.7 repair-class freeze with gap-window marking"
git rebase origin/integration && git push -u origin lane/3/02-t13-level5-escalate
```

### Acceptance criteria

| # | Criterion | Proving command | Required output |
| --- | --- | --- | --- |
| A1 | 11 tests pass | `cd "$(git rev-parse --show-toplevel)" && python -m pytest reconciler/levels/tests/test_level5_escalate.py -q 2>&1 \| grep -oE '^[0-9]+ passed'` | `11 passed` |
| A2 | Exactly five §53.2 conditions plus the D107 one | `cd "$(git rev-parse --show-toplevel)" && python -c "from reconciler.levels import level5_escalate as l;print(len(l.ESCALATION_CONDITIONS), len(l.ALL_CONDITIONS))"` | `5 6` |
| A3 | A gap-window record is not gate evidence | `cd "$(git rev-parse --show-toplevel)" && python -c "from reconciler.repair import freeze;print(freeze.is_gate_evidence({'mark':freeze.GAP_WINDOW_MARK}))"` | `False` |
| A4 | No foreign path touched | see SELF-VERIFY | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
python -m pytest reconciler/levels/tests/test_level5_escalate.py -q 2>&1 | grep -oE '^[0-9]+ passed'
python -c "from reconciler.levels import level5_escalate as l;print(len(l.ESCALATION_CONDITIONS), len(l.ALL_CONDITIONS))"
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler|tools/provision|validators/drift)/'
```

Expected output:

```
11 passed
5 6
0
```

### STOP rule

STOP and file the R6 blocker if: any output above differs; a repair record you must plan a freeze over carries no `compensating_action` (§28.1 required it; that is a Level-5 finding in its own right — escalate, do not synthesise one).
Never let `is_gate_evidence` return `True` for a `gap-window` record. Never auto-revert a repair without the named compensating action.

---

## L3-02-14 — Level-ordering integration test and phase exit gate

**Size:** M **Depends on:** T03, T04, T08, T11, T12, T13
**Spec basis:** §53.2 (the five levels as one graded response), §53.4 (one severity scale used everywhere), §53.1 seeded-canary rule and AT-102 (*"a run that reports zero findings, including the canary, is a FAILED run"*), §99.6 risk 6.

> **Red output is Level 2 (BLOCKER) and raises a Founder-view flag per FD-007.**

### Files created

- `reconciler/tests/test_phase2_integration.py`
- `reconciler/PHASE2-EXIT.md`

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
git fetch origin && git checkout integration && git pull --ff-only
git checkout -b lane/3/02-t14-exit-gate
mkdir -p reconciler/tests
test -f reconciler/tests/__init__.py || printf '' > reconciler/tests/__init__.py
cat > reconciler/tests/test_phase2_integration.py <<'PYEOF'
"""Phase-2 integration properties.

These assert the graded response as a whole, not any one level. Each test
names the spec clause it protects.
"""
import datetime as dt

import pytest

from reconciler.checkrun import poster
from reconciler.credential import bound_check
from reconciler.levels import level1_detect, level2_warn, level4_block, level5_escalate
from reconciler.repair import enablement, executor, registry
from validators.drift import levels, stricter_only, write_scope_guard

NOW = dt.datetime(2026, 6, 1, tzinfo=dt.timezone.utc)


def test_all_five_levels_are_importable_and_named_per_53_2():
    assert levels.RESPONSE_LEVELS == (
        "level_1_detect",
        "level_2_warn",
        "level_3_auto_repair",
        "level_4_block",
        "level_5_escalate",
    )


def test_no_repair_class_is_enabled_at_phase_exit():
    """99.6 risk 6: repair classes are enabled one at a time, by L0, later."""
    assert (enablement.load_state().get("enablements") or []) == []
    assert all(c["enabled"] is False for c in registry.load())


def test_the_only_permit_gate_is_the_stricter_only_comparator():
    """53.3 / invariant 81: one gate, no second opinion."""
    permitted = [v for v in stricter_only.Verdict if stricter_only.is_permitted(v)]
    assert permitted == [stricter_only.Verdict.REPAIR_PERMITTED]


def test_a_blocking_finding_never_reaches_the_repair_executor():
    """53.2: Level 4 blocks; it does not repair."""
    out = executor.execute(
        executor.RepairRequest("F", "branch-protection-reapply", "alpha", "org/alpha", 2, 1),
        ["alpha"],
        lambda r: {"before": 1},
        lambda r: pytest.fail("a write occurred with no class enabled"),
        NOW,
    )
    assert out.wrote is False and out.route == "held"


def test_level_1_never_notifies_and_level_2_always_does():
    f = level1_detect.Finding("F", "alpha", "row", "d", "a", "green", NOW, "https://x.invalid")
    assert level1_detect.detect([f], NOW)["notifications_emitted"] == 0
    g = level1_detect.Finding("G", "alpha", "row", "d", "a", "amber", NOW, "https://x.invalid")
    assert level2_warn.warn([g], [], NOW)["entries"][0]["notify_owner"] is True


def test_only_blocking_class_blocks_work():
    assert [c for c in levels.DRIFT_CLASSES if levels.blocks_work(c)] == ["blocking"]


def test_zero_findings_is_not_treated_as_health_by_any_level():
    """53.1 seeded canary / AT-102: a run reporting zero findings is FAILED.

    No level in this phase may convert an empty finding set into a success
    signal on its own; Level 4 posting success is per-product and is driven
    by the finding set, not by the run's total.
    """
    out = level4_block.block({"alpha": []}, {"alpha": ["org/alpha"]}, lambda r: "0" * 40)
    assert out["posts"][0].conclusion == poster.CONCLUSION_SUCCESS
    # the run-level canary verdict is Phase 1's; assert only that Level 5
    # carries a condition for the instrument failing.
    assert "reconciliation job failing" in level5_escalate.ESCALATION_CONDITIONS


def test_reconciler_cannot_write_a_registry_in_scope():
    """D93: a registry write is out of scope and therefore detectable."""
    assert write_scope_guard.in_scope(write_scope_guard.CONTROL_PLANE, "people.yaml") is False


def test_at110_checklist_is_present_and_well_formed():
    assert len(bound_check.load()["attempts"]) == 6
PYEOF
python -m pytest reconciler/tests/test_phase2_integration.py -q 2>&1 | grep -oE '^[0-9]+ passed'
python -m pytest reconciler validators/drift -q 2>&1 | grep -oE '^[0-9]+ passed'
cat > reconciler/PHASE2-EXIT.md <<'EOF'
# L3 Phase 2 exit record — the five response levels and auto-repair

## What exists

| Spec | Module |
| --- | --- |
| 53.2 Level 1 Detect | reconciler/levels/level1_detect.py |
| 53.2 Level 2 Warn | reconciler/levels/level2_warn.py |
| 53.2 Level 3 Auto-repair | reconciler/levels/level3_repair.py, reconciler/repair/executor.py |
| 53.2 Level 4 Block | reconciler/levels/level4_block.py, reconciler/checkrun/poster.py |
| 53.2 Level 5 Escalate | reconciler/levels/level5_escalate.py, reconciler/repair/freeze.py |
| 53.3 / invariant 81 / AT-033 | validators/drift/stricter_only.py |
| 53.4 | validators/drift/class_map.yaml, validators/drift/levels.py |
| 53.7 "when the loop ran wrong" | reconciler/repair/freeze.py |
| 99.6 risk 6 one-class-at-a-time | reconciler/repair/enablement.py |
| D92 blocking check run | reconciler/checkrun/poster.py |
| D93 derived/** write scope | reconciler/credential/write_scope.yaml, validators/drift/write_scope_guard.py |
| 40.1 check-run identity | validators/drift/checkrun_identity_guard.py |
| AT-110 | reconciler/credential/bound_check.py |

## State at exit

Every one of the five permitted repair classes ships `enabled: false`.
`reconciler/repair/enablement_state.yaml` carries no enablement entry.
Nothing in this phase writes to the estate.

## What is NOT in this phase

- Enabling a repair class. That is a registry-change-lane edit (26.4) with a
  linked decision record, made by L0, one class at a time (99.6 risk 6).
- Running AT-110 `--live`. That needs the fifth-tier credential on the
  operations VM and a DevOps-capability holder.
- The seeded canary and the run-level clean/failed verdict (53.1, AT-102):
  Phase 1.
- The independent control verifier of 53.1: it runs off the operations VM
  under a different credential and is not L3's to build.
EOF
git add reconciler/tests reconciler/PHASE2-EXIT.md
git commit -m "L3-02-14: phase-2 integration properties and exit record"
git rebase origin/integration && git push -u origin lane/3/02-t14-exit-gate
```

### Acceptance criteria

| # | Criterion | Proving command | Required output |
| --- | --- | --- | --- |
| A1 | 9 integration tests pass | `cd "$(git rev-parse --show-toplevel)" && python -m pytest reconciler/tests/test_phase2_integration.py -q 2>&1 \| grep -oE '^[0-9]+ passed'` | `9 passed` |
| A2 | The whole phase passes: 125 tests | `cd "$(git rev-parse --show-toplevel)" && python -m pytest reconciler validators/drift -q 2>&1 \| grep -oE '^[0-9]+ passed'` | `125 passed` |
| A3 | Nothing is enabled at exit | `cd "$(git rev-parse --show-toplevel)" && grep -c 'enabled: false' reconciler/repair/classes.yaml && python -c "from reconciler.repair import enablement as e;print(len(e.load_state().get('enablements') or []))"` | `5` then `0` |
| A4 | All five level modules exist | `cd "$(git rev-parse --show-toplevel)" && ls reconciler/levels/level1_detect.py reconciler/levels/level2_warn.py reconciler/levels/level3_repair.py reconciler/levels/level4_block.py reconciler/levels/level5_escalate.py \| wc -l` | `5` |
| A5 | No foreign path touched | see SELF-VERIFY | `0` |

*(A2's total is the sum of the per-task counts: T02 11 + T03 7 + T04 5 + T05 19 + T06 9 + T07 9 + T08 9 + T09 11 + T10 9 + T11 11 + T12 5 + T13 11 + T14 9 = **125**. Run A2 only after all thirteen prior task branches are merged to `integration` and this branch is rebased on it. Before that point, run the zero-failures form in SELF-VERIFY instead — the binding criterion on a partially-merged tree is zero failures, not the total.)*

### SELF-VERIFY

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
python -m pytest reconciler/tests/test_phase2_integration.py -q 2>&1 | grep -oE '^[0-9]+ passed'
python -m pytest reconciler validators/drift -q 2>&1 | grep -cE '^[0-9]+ failed'
python -c "from reconciler.repair import enablement as e;print(len(e.load_state().get('enablements') or []))"
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler|tools/provision|validators/drift)/'
```

Expected output:

```
9 passed
0
0
0
```

### STOP rule

STOP and file the R6 blocker if: `9 passed` is not printed; the failure count is not `0`; the enablement count is not `0`; the lane-guard count is not `0`; any earlier task's branch is not yet merged to `integration` (rebase and wait — do not merge another lane's branch, per PARTITION "A lane NEVER merges another lane's branch").

---

## 5. Phase exit conditions — all must hold before L3 Phase 3 begins

| # | Condition | Command | Required |
| --- | --- | --- | --- |
| E1 | All fourteen task branches merged to `integration` | `git log --oneline origin/integration \| grep -c 'L3-02-T'` | `14` |
| E2 | Whole-phase suite green, zero failures | `python -m pytest reconciler validators/drift -q 2>&1 \| grep -cE '^[0-9]+ failed'` | `0` |
| E3 | No repair class enabled | `python -c "from reconciler.repair import enablement as e;print(len(e.load_state().get('enablements') or []))"` | `0` |
| E4 | Reconciler control-plane write scope is exactly `derived/` | `python -c "from validators.drift import write_scope_guard as g;print(g.load_scope()[g.CONTROL_PLANE]['allowed_path_prefixes'])"` | `['derived/']` |
| E5 | AT-110 checklist present and well-formed | `python -m reconciler.credential.bound_check --dry-run` | `AT-110 checklist OK: 6 attempts, all expect fail, post-condition expects pass` |
| E6 | No foreign path in any phase commit | `git diff --name-only $(git merge-base origin/main origin/integration)...origin/integration -- \| grep -vcE '^(reconciler|tools/provision|validators/drift)/'` | `0` |

**AT-110 `--live` is the gate that lets a repair class be enabled at all.** It is executed by a DevOps-capability holder against the fifth-tier credential (§40.1), not by this executor, and its result is recorded before L0 writes the first enablement entry.
