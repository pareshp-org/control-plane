> **[SUPERSEDED — FD-B1-L3 2026-09-02]**
> This file has been superseded by L3-06-tasks.md. Do not execute tasks from this file.
> Authoritative plan: Code/implementation/lanes/L3-06-tasks.md

# LANE 3 — RECONCILER AND PROVISIONING
# PHASE 3 — INSTRUMENT INTEGRITY

> **REFERENCE ONLY** — FD-098 (2026-09-09): Task bodies superseded by L3-06-tasks.md. This file is a design-note reference. Do not execute task bodies from this file.

Subsystems **C** (Reconciliation engine) and **D** (Provisioning and scaffolding), spec Section 99.2.
Owned paths (PARTITION.md, FROZEN): `reconciler/**`, `tools/provision/**`, `validators/drift/**`.
Branch prefix: `lane/3/*`. Merge train position: L1 → L4 → L2 → **L3** → L5.

> Section 99.6, risk 6: *"Reconciliation auto-repair as the most dangerous code — a write-scope, org-admin automation whose bug loosens security or locks everyone out; the reconciler is the highest-privilege identity in the system."* Mitigation named there and binding on every task below: **detect-only first; repair classes enabled one at a time; stricter-only rule enforced in code and tested.** No task in this phase enables a new repair class. Every new code path in this phase is either a detector, a recorder, or a gate that fails closed.

---

## 1. What Phase 3 delivers

Phase 3 makes the reconciler's own instrument honest. Phases 1 and 2 built an engine that compares declared state to actual state; nothing in them proves the engine was still *looking*. This phase adds the five mechanisms that make a silent instrument failure loud.

| # | Mechanism | Spec source | Tasks |
| --- | --- | --- | --- |
| 1 | **The seeded-canary rule** — a permanently planted, clearly labelled drift record every run MUST find; a run reporting zero findings, the canary included, is a **FAILED** run | §53.1 (*"The seeded-canary rule"*), **AT-102**, **EC-109**, **D63** | T01–T04, T14 |
| 2 | **The declared-state canary** — a merged registry change applies to the declared canary product set first and holds the fleet for one reconciliation cycle; reconciler write scope narrowed to generated `derived/**` | **D93**, §26.4 (*"Registry edits stage before they reach the fleet"*), §61.3, §61.5, invariant 72 | T05–T06 |
| 3 | **The control-loop gap procedure** — replay expiries, diff-audit grants/merges/production approvals, re-run standing checks, record the gap at Level 5, mark interim records `gap-window`; plus the *"when the loop ran wrong"* branch | §53.7, §53.2 (Level 5), §26.4 (repair records), **D63** | T07–T09 |
| 4 | **Records tamper-evidence anchoring** — the records-repository head SHA and commit count anchored into the protected control-plane repository once per run; a non-descendant head is **Blocking, Level 5** | **D107**, §53.2, §63.1, §97.1, invariant 47 | T10–T11 |
| 5 | **Behavioural credential bounds** — signed run record naming the scheduled trigger, run-count ceiling, expected source host, published per-run API-call counts, per-run mutation cap; a run without a matching scheduled trigger is **Blocking** | **D96**, §40.1 (*"The behavioural envelope"*), §51.2, §53.1 | T12–T13 |

**Acceptance test this phase must satisfy: AT-102** — *"The seeded reconciliation canary. Every reconciliation run must find the deliberately seeded canary drift. A run reporting zero findings — the canary included — is a **failed** run, raises SIG-13 (failed reconciliations), and triggers the gap procedure; a reconciler that finds nothing is assumed broken, never assumed clean."* AT-102 is proved by task **T14** and by no other task. Related coverage carried incidentally: **AT-032** (self-observability) by T03 and T07; **AT-033** (no auto-loosening) is Phase 2's and is only re-asserted, never re-implemented, here.

Signals raised by this phase's code: **SIG-13** (Failed reconciliations — Red, Team Lead; §52 signal table). No other signal is raised by Phase 3 code.

---

## 2. DECISION REQUIRED — two items for L0

These two items require a choice this lane has no authority to make. **Both carry an interim default so that no task in this file is blocked.** Every task below reads the value from a configuration file this lane owns; when L0 rules, exactly one line changes and no code changes.

### DECISION REQUIRED — DR-3.1 · Anchor destination path and the reconciler write-scope allowlist

**The question.** D107 requires the reconciler to write the records-repository head SHA *"into the **control-plane repository**, which is fully protected."* D93 narrows *"the reconciler's own write scope … to generated `derived/**` files the registries reference, so a machine write to a registry becomes detectable Blocking drift rather than an in-scope write."* PARTITION.md assigns `derived/**` to **no lane**. L3 therefore cannot create the anchor's destination directory, and cannot declare which paths the write-scope allowlist contains.

**What L0 must decide.**
1. The exact anchor destination path inside the control-plane repository, expected to be under `derived/`.
2. Which lane owns `derived/**` in PARTITION.md, or whether `derived/**` is generated-only and owned by L0 alongside `contracts/**`.
3. The literal contents of the reconciler write-scope allowlist — the complete set of path globs the reconciler credential may write in the control-plane repository.

**Interim default in force until L0 rules** (`reconciler/config/anchoring.yaml`, created by T10, owned by this lane):

```yaml
anchor_path: derived/anchors/records-head.yaml
write_scope_allowlist:
  - derived/**
```

**Why the default is safe to build against.** It is the narrowest reading of D93 and D107 together, it is one line to change, and T06 enforces the allowlist as data rather than as code — so a change to the allowlist is a configuration edit, never a code edit.

### DECISION REQUIRED — DR-3.2 · Drift class of the permanent canary finding

**The question.** §53.1 requires a permanently present seeded drift finding. §53.4 declares exactly one drift severity scale and gives Amber and Red hard portfolio budgets (*"up to 2 open Amber per product … Red is deliberately held flat at 3 portfolio-wide"*). A permanent finding that consumes budget forever would exhaust the budget by construction; a permanent finding excluded from the budget by ad-hoc code would violate §53.4's *"Class assignment lives in configuration and is reviewable; it is not decided ad hoc during an incident."*

**What L0 must decide.** The canary finding's drift class, and whether it is excluded from the §53.4 budget counters.

**Interim default in force until L0 rules** (`validators/drift/canary/canary.yaml`, created by T01):

```yaml
drift_class: green          # §53.4 — "Green | Within tolerance; recorded only | None | Nobody | No"
counts_against_budget: false
```

**Why the default is safe to build against.** §53.4 gives Green no budget (*"Green is unlimited"*), so the default is the only class whose semantics do not change the budget arithmetic. The class lives in configuration and is reviewable, exactly as §53.4 requires. The canary's *absence* is never Green — absence is handled by T03 as a FAILED run at Level 5, which is a different finding with a different class.

---

## 3. Conventions binding on every task

**Read this section once before starting T00. Every task assumes it.**

| Item | Value |
| --- | --- |
| Control-plane clone | `~/control-plane` |
| Records clone (read-only in this phase) | `~/control-plane-records` |
| Language and runtime | Python `== 3.12` (exact pin; this is the seventh runtime-declaring file FD-005 omits) |
| Test runner | `pytest` |
| Linter | `ruff` |
| Branch naming | `lane/3/p3-<task-id-lowercase>` — e.g. `lane/3/p3-t01` |
| Base branch for every task | `integration` |
| Timestamps | UTC with offset, per §97.1 (*"Every record and event timestamp is stored in UTC with its offset"*) |
| Record schema field | every emitted record carries `record_schema_version: 1`, per §97.2 |

**Additive-only.** PARTITION.md rule 5. Every task in this phase creates **new** files. No task in this phase edits a file created by Phase 1 or Phase 2. Where Phase 3 must be reached from existing code, it is reached by **glob discovery**, never by editing a central list — PARTITION.md rule 3, *"No shared mutable file, ever."*

**Discovery contract.** Two glob directories are the only integration surface Phase 3 uses:

* `validators/drift/rules/*.py` — each file exposes `RULE`, a `DriftRule` instance. Discovered by glob at engine start.
* `reconciler/hooks/*.py` — each file exposes `HOOK`, a `RunHook` instance. Discovered by glob at engine start.

Both directories are created by T00 if absent. Adding a rule or a hook is adding a file. Nothing is appended to anything.

**Cross-lane boundary — records writes.** PARTITION.md rule 4: *"A lane consumes another lane's output only through `contracts/**` or a published artifact — never by reaching into its source tree."* Every record store under `records/**` and `events/**` belongs to **L4**. Phase 3 code therefore **never writes a record file**. Where §53.7 requires marking records `gap-window`, T08 emits a *manifest artifact* naming the records to be marked; L4's records tooling consumes the manifest and performs the write. A task that finds itself about to write under `records/` has misread this file and must STOP.

**The universal blocker-issue template.** Every STOP rule in this file uses it. Open the issue in the `control-plane` repository with label `blocker` and label `lane-3`.

```
Title: [BLOCKER][L3-P3][<task-id>] <one-line symptom>

Task id:        <task-id>
Lane:           L3 — Reconciler & Provisioning
Phase:          3 — Instrument Integrity
Branch:         lane/3/p3-<task-id-lowercase>
Spec anchors:   <the § / D / AT identifiers named in the task's Spec anchors row>

STOP rule that fired:
<paste the exact STOP condition text from the task>

Command run:
<paste the exact command>

Expected output:
<paste the SELF-VERIFY expected output from the task>

Actual output:
<paste verbatim, complete, no truncation>

Repository state:
git -C ~/control-plane rev-parse --abbrev-ref HEAD  ->  <paste>
git -C ~/control-plane rev-parse HEAD               ->  <paste>
git -C ~/control-plane status --porcelain           ->  <paste>

What I did NOT do:
I stopped at this task. I made no change outside reconciler/**, tools/provision/**
and validators/drift/**. I opened no pull request. I merged nothing.

Decision needed from L0:
<state the single question that unblocks this, or write "unknown — please triage">
```

**The universal STOP preamble.** In addition to each task's own STOP rule, **stop immediately and open a blocker on any of these, in every task**:

1. A command requires editing a file outside `reconciler/**`, `tools/provision/**` or `validators/drift/**`.
2. `git status --porcelain` shows a modified file outside those three prefixes.
3. A rebase on `integration` produces a conflict in a file this lane does not own.
4. A test asserts something this file does not state, and you would have to decide what it should assert.
5. Any step would loosen, disable or skip an existing check to make a new one pass.

Rule 5 is the one that matters most. §53.3 is binding on the engine and §99.6 risk 6 is binding on the person editing it: *"Reconciliation never loosens a control automatically."* A developer who loosens one manually has done something the engine is forbidden to do.

---

## 4. Task manifest

| Task | Title | Size | Depends on |
| --- | --- | --- | --- |
| L3-P3-T00 | Phase entry gate and discovery directories | S | — |
| L3-P3-T01 | The seeded canary declaration and its loader | M | T00 |
| L3-P3-T02 | Canary through the real comparator dispatch; per-registry comparison counts | M | T01 |
| L3-P3-T03 | The FAILED-run rule — zero findings including the canary | M | T02 |
| L3-P3-T04 | Negative tests: prove the canary catches a blinded instrument | M | T03 |
| L3-P3-T05 | D93 — canary-set-first application and the one-cycle fleet hold | L | T03 |
| L3-P3-T06 | D93 — reconciler write-scope allowlist and machine-registry-write drift rule | M | T05 |
| L3-P3-T07 | §53.7 — control-loop gap detection | M | T03 |
| L3-P3-T08 | §53.7 — the gap procedure runner | L | T07 |
| L3-P3-T09 | §53.7 — the "when the loop ran wrong" branch | M | T08 |
| L3-P3-T10 | D107 — anchor the records head SHA and commit count each run | M | T02 |
| L3-P3-T11 | D107 — the non-descendant check at Blocking, Level 5 | M | T10 |
| L3-P3-T12 | D96 — the behavioural envelope: signed run record and published counts | L | T02 |
| L3-P3-T13 | D96 — envelope enforcement; unmatched trigger is Blocking | M | T12 |
| L3-P3-T14 | AT-102 acceptance harness and the phase exit gate | M | T03, T05, T06, T08, T09, T11, T13 |

Fifteen tasks. Sizes: S under half a day, M half a day to a day and a half, L two to three days, for the reader profile PARTITION.md names.

---

## L3-P3-T00 — Phase entry gate and discovery directories

| Field | Value |
| --- | --- |
| **Task id** | `L3-P3-T00` |
| **Size** | S |
| **Depends on** | — (phase entry) |
| **Spec anchors** | §99.2 subsystem C; §99.6 risk 6; PARTITION.md |
| **Files created** | `reconciler/hooks/__init__.py`, `validators/drift/rules/__init__.py`, `reconciler/phase3/__init__.py`, `reconciler/tests/test_p3_entry.py`, `reconciler/tests/verify_t00.sh` |

**Purpose.** Prove the environment Phase 3 assumes actually exists before any of it is built, and create the two glob-discovery directories every later task writes into. This task writes no logic.

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
git fetch origin
git switch integration
git pull --ff-only origin integration
git switch -c lane/3/p3-t00
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
python3 --version
python3 -c "import sys; assert sys.version_info >= (3,11), sys.version; print('PYTHON_OK')"
python3 -m pytest --version
python3 -m ruff --version
test -d reconciler && echo "RECONCILER_DIR_OK"
test -d validators/drift && echo "DRIFT_DIR_OK"
test -d contracts && echo "CONTRACTS_DIR_OK"
test -d ~/control-plane-records/.git && echo "RECORDS_CLONE_OK"
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
mkdir -p reconciler/hooks reconciler/phase3 reconciler/tests reconciler/config \
         validators/drift/rules validators/drift/canary
touch reconciler/hooks/__init__.py reconciler/phase3/__init__.py validators/drift/rules/__init__.py
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
cat > reconciler/tests/test_p3_entry.py <<'PYEOF'
"""Phase 3 entry gate. Proves the environment Phase 3 is written against.

Lane 3 (Reconciler & Provisioning), Phase 3 (Instrument Integrity).
Owned paths only: reconciler/**, tools/provision/**, validators/drift/**.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]

OWNED_PREFIXES = ("reconciler/", "tools/provision/", "validators/drift/")

REQUIRED_DIRS = [
    "reconciler",
    "reconciler/hooks",
    "reconciler/phase3",
    "reconciler/config",
    "reconciler/tests",
    "validators/drift",
    "validators/drift/rules",
    "validators/drift/canary",
]


def test_python_version_is_at_least_3_11():
    assert sys.version_info >= (3, 11), f"python too old: {sys.version}"


def test_required_directories_exist():
    missing = [d for d in REQUIRED_DIRS if not (ROOT / d).is_dir()]
    assert not missing, f"missing directories: {missing}"


def test_glob_discovery_directories_are_packages():
    for pkg in ("reconciler/hooks", "reconciler/phase3", "validators/drift/rules"):
        assert (ROOT / pkg / "__init__.py").is_file(), f"not a package: {pkg}"


def test_owned_prefixes_are_the_only_ones_phase3_writes():
    """Documents the PARTITION.md rule as an executable assertion."""
    assert OWNED_PREFIXES == (
        "reconciler/",
        "tools/provision/",
        "validators/drift/",
    )
PYEOF
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
cat > reconciler/tests/verify_t00.sh <<'SHEOF'
#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
python3 -m pytest -q reconciler/tests/test_p3_entry.py >/dev/null
CHANGED=$(git status --porcelain | awk '{print $2}' \
  | grep -v -E '^(reconciler/|tools/provision/|validators/drift/)' || true)
if [ -n "$CHANGED" ]; then
  echo "T00 FAIL foreign-path-touched"
  exit 1
fi
echo "T00 PASS"
SHEOF
chmod +x reconciler/tests/verify_t00.sh
bash reconciler/tests/verify_t00.sh
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
python3 -m ruff check reconciler validators/drift
git add reconciler validators/drift
git status --porcelain
git commit -m "L3-P3-T00: phase 3 entry gate and glob-discovery directories"
git push -u origin lane/3/p3-t00
gh pr create --base integration --head lane/3/p3-t00 \
  --title "L3-P3-T00 phase 3 entry gate" \
  --body "Lane 3, Phase 3, task T00. Creates reconciler/hooks/, reconciler/phase3/, validators/drift/rules/, validators/drift/canary/ and the entry-gate test. No logic. Owned paths only."
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
| --- | --- | --- | --- |
| 1 | Python is exactly 3.12 (exact pin) | `python3 -c "import sys; assert sys.version_info[:2]==(3,12); print('PYTHON_OK')"` | `PYTHON_OK` |
| 2 | All four discovery/config directories exist and are packages where required | `python3 -m pytest -q reconciler/tests/test_p3_entry.py` | last line `4 passed` |
| 3 | The working tree touches no foreign path | `git -C ~/control-plane status --porcelain \| awk '{print $2}' \| grep -v -E '^(reconciler/\|tools/provision/\|validators/drift/)' \| wc -l` | `0` |
| 4 | Lint is clean on both owned trees | `python3 -m ruff check reconciler validators/drift` | `All checks passed!` |
| 5 | The records clone is present and readable | `git -C ~/control-plane-records rev-parse --abbrev-ref HEAD` | a branch name, non-empty |

### SELF-VERIFY

```bash
set -euo pipefail
cd ~/control-plane && bash reconciler/tests/verify_t00.sh
```

Expected output, exactly one line:

```
T00 PASS
```

### STOP rule

**Stop and open a blocker if any of the following is true.** Do not work around any of them.

* `python3 --version` reports other than 3.12 (exact pin `== 3.12` required per FD-005), or `pytest` / `ruff` is not installed.
* `reconciler/`, `validators/drift/` or `contracts/` does not exist on `integration` — Phase 1, Phase 2 or L0 Phase 0 has not landed, and Phase 3 has nothing to attach to.
* `~/control-plane-records/.git` does not exist — T10 and T11 cannot be built without a records clone.
* `verify_t00.sh` prints `T00 FAIL foreign-path-touched`.
* Anything in the universal STOP preamble (Section 3).

Use the universal blocker template. For the missing-directory case, the *Decision needed from L0* line is: `Which lane's phase creates <path>, and has it merged to integration yet?`

---

## L3-P3-T01 — The seeded canary declaration and its loader

| Field | Value |
| --- | --- |
| **Task id** | `L3-P3-T01` |
| **Size** | M |
| **Depends on** | `L3-P3-T00` |
| **Spec anchors** | §53.1 (*"The seeded-canary rule"*); **AT-102**; **EC-109**; **D63**; §53.4 (*"Security drift and production environment drift are never classified below Red"*, *"Class assignment lives in configuration and is reviewable"*); §97.1 (UTC with offset); §97.2 (`record_schema_version`); **DR-3.2** |
| **Files created** | `validators/drift/canary/canary.yaml`, `validators/drift/canary/__init__.py`, `validators/drift/canary/loader.py`, `validators/drift/tests/test_canary_loader.py` |

**Purpose.** Declare the permanent seeded drift record §53.1 requires — *"a deliberately planted, clearly labelled mismatch in the comparison set — exists at all times"* — as configuration, and build the loader that reads it. This task creates the canary's *declaration*. T02 puts it through the real comparator dispatch; T03 makes its absence a FAILED run. Nothing here decides where the canary is planted against real platform state: that is **D-L3-04(a)**, filed to L0 by Phase 1, and until L0 rules the canary's two sides are two literals held in this file, which differ by construction.

The canary is a **mismatch**, not a marker. A canary whose declared and actual sides are equal produces no finding, and a canary that produces no finding cannot prove the instrument looked. The loader refuses to load such a configuration.

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
git fetch origin
git switch integration
git pull --ff-only origin integration
git switch -c lane/3/p3-t01
mkdir -p validators/drift/canary validators/drift/tests
[ -f validators/drift/tests/__init__.py ] || touch validators/drift/tests/__init__.py
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
cat > validators/drift/canary/canary.yaml <<'YAMLEOF'
# The permanent seeded drift record. Section 53.1, "The seeded-canary rule":
#   "A permanent seeded drift record - a deliberately planted, clearly
#    labelled mismatch in the comparison set - exists at all times, and every
#    reconciliation run MUST find it."
#
# AT-102: a run reporting zero findings, the canary included, is a FAILED run.
# EC-109: the canary is what exposes a silently-vacuous run.
# D63:    the reconciliation loop is negatively tested.
#
# DO NOT DELETE THIS FILE. DO NOT MAKE THE TWO MARKERS EQUAL.
# Deleting it or equalising the markers disarms AT-102 silently, which is the
# exact failure AT-102 exists to detect.
canary_version: 1
spec_refs: ["53.1", "AT-102", "EC-109", "D63", "53.4"]

canary_id: CANARY-DRIFT-001
label: SEEDED-CANARY-DO-NOT-REMOVE

# DR-3.2 interim default, in force until L0 rules.
# Section 53.4: "Green | Within tolerance; recorded only | None | Nobody | No"
# and "Green is unlimited", so a permanent Green finding cannot exhaust a
# budget. Class assignment lives here, in configuration, and is reviewable -
# Section 53.4 - and is never decided during an incident.
drift_class: green
counts_against_budget: false

# The planted mismatch. The two sides differ by construction.
# REG-028 (D-L3-04(a)) answered: a labelled reserved row in the L1-owned
# registry the reconciler already reads, compared under RECON-S3.
# registry_key and marker values are now contract-driven (not literals).
registry_key: contracts/registry/canary.v1.yaml  # FROM REG-028: L1-owned canary registry path
comparison_row: "Seeded canary marker (53.1 seeded-canary rule)"
declared_marker: "row-key:canary_reserved_row_declared"  # FROM REG-028: contract-driven row key reference
actual_marker_source: "row-key:canary_reserved_row_actual"  # FROM REG-028: contract-driven; no longer a literal

# Rows the canary may never be planted on.
# Section 53.4: "Security drift and production environment drift are never
# classified below Red." A canary planted on such a row would either consume
# the Red budget forever or force a class the spec forbids.
forbidden_placement_classes: ["blocking", "red"]
forbidden_placement_scopes: ["production"]
YAMLEOF
touch validators/drift/canary/__init__.py
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
cat > validators/drift/canary/loader.py <<'PYEOF'
"""Loader for the permanent seeded canary (spec 53.1, AT-102, EC-109, D63).

Section 53.1, the seeded-canary rule:
    "A permanent seeded drift record - a deliberately planted, clearly
     labelled mismatch in the comparison set - exists at all times, and every
     reconciliation run MUST find it. A run that reports zero findings,
     including the canary, is a FAILED run, not a clean one."

This module reads the declaration and nothing else. It decides no class
(Section 53.4: class assignment lives in configuration) and writes no record
(the record stores belong to L4).
"""
from __future__ import annotations

import dataclasses
import datetime as _dt
import pathlib
from typing import Any

import yaml

CANARY_CONFIG = pathlib.Path("validators/drift/canary/canary.yaml")

RECORD_SCHEMA_VERSION = 1  # spec 97.2

_REQUIRED_KEYS = (
    "canary_id",
    "label",
    "drift_class",
    "counts_against_budget",
    "registry_key",
    "comparison_row",
    "declared_marker",
    "actual_marker_source",
    "forbidden_placement_classes",
    "forbidden_placement_scopes",
)


class CanaryConfigError(RuntimeError):
    """The canary declaration is absent, malformed, or not a mismatch.

    Never fall back to a default. An absent canary is the condition AT-102
    exists to make loud, so it raises rather than degrading quietly.
    """


@dataclasses.dataclass(frozen=True)
class Canary:
    canary_id: str
    label: str
    drift_class: str
    counts_against_budget: bool
    registry_key: str
    comparison_row: str
    declared: str
    actual: str
    forbidden_placement_classes: tuple[str, ...]
    forbidden_placement_scopes: tuple[str, ...]


def _resolve_actual(source: str) -> str:
    """Resolve the actual side of the planted mismatch.

    Only the 'literal:' form is implemented. Any other form means L0 has
    ruled on D-L3-04(a) and this module must be re-issued against the ruled
    placement rather than guessed at here.
    """
    if not source.startswith("literal:"):
        raise CanaryConfigError(
            "unsupported actual_marker_source: "
            f"{source!r}; D-L3-04(a) is unresolved and only 'literal:' is built"
        )
    return source[len("literal:") :]


def load(path: pathlib.Path | None = None) -> Canary:
    cfg_path = path or CANARY_CONFIG
    if not cfg_path.is_file():
        raise CanaryConfigError(
            f"canary declaration absent: {cfg_path}. Section 53.1 requires the "
            "seeded drift record to exist at all times"
        )
    data: Any = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise CanaryConfigError(f"canary declaration is not a mapping: {cfg_path}")
    missing = [k for k in _REQUIRED_KEYS if k not in data]
    if missing:
        raise CanaryConfigError(f"canary declaration missing keys: {missing}")

    declared = str(data["declared_marker"])
    actual = _resolve_actual(str(data["actual_marker_source"]))
    if declared == actual:
        raise CanaryConfigError(
            "canary declared and actual markers are equal: the seeded record is "
            "not a mismatch and would produce no finding (53.1)"
        )

    forbidden_classes = tuple(str(c) for c in data["forbidden_placement_classes"])
    drift_class = str(data["drift_class"])
    if drift_class in forbidden_classes:
        raise CanaryConfigError(
            f"canary drift_class {drift_class!r} is forbidden: section 53.4 - "
            "security and production drift are never classified below Red, so "
            "the canary is never planted on such a row"
        )

    return Canary(
        canary_id=str(data["canary_id"]),
        label=str(data["label"]),
        drift_class=drift_class,
        counts_against_budget=bool(data["counts_against_budget"]),
        registry_key=str(data["registry_key"]),
        comparison_row=str(data["comparison_row"]),
        declared=declared,
        actual=actual,
        forbidden_placement_classes=forbidden_classes,
        forbidden_placement_scopes=tuple(
            str(s) for s in data["forbidden_placement_scopes"]
        ),
    )


def finding(canary: Canary, now: _dt.datetime) -> dict[str, Any]:
    """The canary's drift finding, shaped like every other finding.

    Section 53.1: "Every drift finding carries an `acknowledged_by` and
    `acknowledged_at` field." Section 97.1: timestamps are UTC with offset.
    """
    if now.tzinfo is None:
        raise CanaryConfigError("now must be timezone-aware (97.1: UTC with offset)")
    return {
        "record_schema_version": RECORD_SCHEMA_VERSION,
        "finding_id": canary.canary_id,
        "label": canary.label,
        "registry_key": canary.registry_key,
        "comparison_row": canary.comparison_row,
        "declared": canary.declared,
        "actual": canary.actual,
        "drift_class": canary.drift_class,
        "counts_against_budget": canary.counts_against_budget,
        "is_canary": True,
        "observed_at": now.astimezone(_dt.timezone.utc).isoformat(),
        "acknowledged_by": None,
        "acknowledged_at": None,
    }
PYEOF
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
cat > validators/drift/tests/test_canary_loader.py <<'PYEOF'
import datetime as dt
import pathlib

import pytest
import yaml

from validators.drift.canary import loader as cl

NOW = dt.datetime(2026, 6, 1, 9, 0, tzinfo=dt.timezone.utc)


def _write(tmp_path: pathlib.Path, **overrides):
    data = yaml.safe_load(cl.CANARY_CONFIG.read_text(encoding="utf-8"))
    data.update(overrides)
    p = tmp_path / "canary.yaml"
    p.write_text(yaml.safe_dump(data), encoding="utf-8")
    return p


def test_declaration_loads_from_the_repository_copy():
    c = cl.load()
    assert c.canary_id == "CANARY-DRIFT-001"


def test_canary_is_clearly_labelled():
    assert cl.load().label == "SEEDED-CANARY-DO-NOT-REMOVE"


def test_canary_is_a_mismatch_by_construction():
    c = cl.load()
    assert c.declared != c.actual


def test_canary_class_is_not_a_forbidden_placement_class():
    c = cl.load()
    assert c.drift_class not in c.forbidden_placement_classes


def test_canary_does_not_consume_a_drift_budget():
    assert cl.load().counts_against_budget is False


def test_finding_carries_the_record_schema_version():
    f = cl.finding(cl.load(), NOW)
    assert f["record_schema_version"] == 1


def test_finding_timestamp_is_utc_with_offset():
    f = cl.finding(cl.load(), NOW)
    assert f["observed_at"].endswith("+00:00")


def test_finding_carries_the_acknowledgement_fields():
    f = cl.finding(cl.load(), NOW)
    assert "acknowledged_by" in f and "acknowledged_at" in f


def test_equal_markers_are_rejected(tmp_path):
    p = _write(tmp_path, actual_marker_source="literal:SEEDED-CANARY-DECLARED-A")
    with pytest.raises(cl.CanaryConfigError):
        cl.load(p)


def test_absent_declaration_raises_and_never_defaults(tmp_path):
    with pytest.raises(cl.CanaryConfigError):
        cl.load(tmp_path / "absent.yaml")


def test_forbidden_class_is_rejected(tmp_path):
    p = _write(tmp_path, drift_class="blocking")
    with pytest.raises(cl.CanaryConfigError):
        cl.load(p)


def test_naive_timestamp_is_rejected():
    with pytest.raises(cl.CanaryConfigError):
        cl.finding(cl.load(), dt.datetime(2026, 6, 1, 9, 0))
PYEOF
python3 -m pytest -q validators/drift/tests/test_canary_loader.py
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
python3 -m ruff check reconciler validators/drift
git add validators/drift
git status --porcelain
git commit -m "L3-P3-T01: seeded canary declaration and loader (53.1, AT-102, D63)"
git push -u origin lane/3/p3-t01
gh pr create --base integration --head lane/3/p3-t01 \
  --title "L3-P3-T01 seeded canary declaration and loader" \
  --body "Lane 3, Phase 3, task T01. Declares the permanent seeded drift record of section 53.1 as configuration (DR-3.2 interim class: green, not budget-counting) and adds its loader. The canary is a mismatch by construction; equal markers are rejected. No record is written. Owned paths only."
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
| --- | --- | --- | --- |
| 1 | The declaration loads and is a mismatch | `python3 -c "from validators.drift.canary import loader as l;c=l.load();print(c.declared != c.actual)"` | `True` |
| 2 | Twelve loader tests pass | `python3 -m pytest -q validators/drift/tests/test_canary_loader.py 2>&1 \| grep -oE '^[0-9]+ passed'` | `12 passed` |
| 3 | The canary's class comes from configuration, never from code | `grep -c "drift_class = \"" validators/drift/canary/loader.py` | `0` |
| 4 | The canary does not consume a §53.4 budget | `python3 -c "from validators.drift.canary import loader as l;print(l.load().counts_against_budget)"` | `False` |
| 5 | Lint clean | `python3 -m ruff check reconciler validators/drift` | `All checks passed!` |
| 6 | No foreign path touched | `git -C ~/control-plane diff --name-only origin/integration...HEAD \| grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'` | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd ~/control-plane
python3 -m pytest -q validators/drift/tests/test_canary_loader.py 2>&1 | grep -oE '^[0-9]+ passed'
python3 -c "from validators.drift.canary import loader as l;c=l.load();print(c.canary_id, c.declared != c.actual, c.counts_against_budget)"
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'
```

Expected output, exactly three lines:

```
12 passed
CANARY-DRIFT-001 True False
0
```

### STOP rule

**Stop and open a blocker if any of the following is true.**

* `docs/decisions/D-L3-04.md` exists on `integration`. L0 has ruled on canary placement (Phase 1's decision item) and this task must be re-issued against the ruled placement. **Do not interpret the decision record yourself** — that is the judgment PARTITION.md forbids this reader.
* The test count is not `12 passed`.
* You are about to make `declared_marker` equal to the resolved actual marker to "make the run clean". A canary that produces no finding disarms AT-102. This is universal STOP preamble rule 5.
* You are about to plant the canary on a real security control or on a `production`-scoped row. §53.4 forbids it.

Use the universal blocker template. *Decision needed from L0* for the first case: `D-L3-04(a) is answered — re-issue L3-P3-T01 and T02 against the ruled canary placement.`

---

## L3-P3-T02 — Canary through the real comparator dispatch; per-registry comparison counts

| Field | Value |
| --- | --- |
| **Task id** | `L3-P3-T02` |
| **Size** | M |
| **Depends on** | `L3-P3-T01` |
| **Spec anchors** | §53.1 (*"every reconciliation run MUST find it"*; *"Every run additionally records its per-registry comparison counts — how many rows of each registry it actually compared — so that a silently narrowed comparison is itself visible drift"*); **AT-102**; **EC-109**; §95.4 (negative-test philosophy, cited by §53.1) |
| **Files created** | `reconciler/phase3/rule_api.py`, `reconciler/phase3/discovery.py`, `reconciler/phase3/counts.py`, `validators/drift/rules/canary_rule.py`, `reconciler/tests/test_p3_discovery.py`, `validators/drift/tests/test_canary_rule.py` |

**Purpose.** Make the canary travel the **same** code path as every other finding. A canary appended to the result list after the comparison has finished proves nothing: the appending code would keep appending it while the comparators sat idle, which is precisely EC-109 (*"A reconciliation run completes 'clean' while actually checking nothing"*). So the canary is published as a discovered rule in `validators/drift/rules/`, evaluated by the same dispatch that evaluates every other rule, and counted in the same per-registry comparison counts.

This task also establishes the two dataclasses Section 3's discovery contract names — `DriftRule` and `RunHook` — and the glob discovery that finds them. Nothing is appended to any central list, per PARTITION.md rule 3.

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
git fetch origin
git switch integration
git pull --ff-only origin integration
git switch -c lane/3/p3-t02
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
cat > reconciler/phase3/rule_api.py <<'PYEOF'
"""The Phase 3 discovery contract: DriftRule and RunHook.

Section 3 of the Phase 3 plan: adding a rule or a hook is adding a file.
Nothing is appended to a central list (PARTITION.md rule 3, "No shared
mutable file, ever").

A DriftRule is a pure function of its context. It reads; it never writes a
record (the record stores belong to L4) and it never mutates platform state
(section 99.6 risk 6: this phase adds detectors, recorders and gates only).
"""
from __future__ import annotations

import dataclasses
from typing import Any, Callable

Findings = list[dict[str, Any]]


@dataclasses.dataclass(frozen=True)
class DriftRule:
    """One discovered comparison row.

    rule_id       stable identifier, unique across validators/drift/rules/
    registry_key  the per-registry comparison-count bucket this row counts in
    evaluate      (context) -> list of finding dicts
    """

    rule_id: str
    registry_key: str
    evaluate: Callable[[dict[str, Any]], Findings]


@dataclasses.dataclass(frozen=True)
class RunHook:
    """One discovered per-run step.

    phase is 'pre' (runs before any comparison; may fail the run closed) or
    'post' (runs after the comparison; may add findings or artifacts).
    """

    hook_id: str
    phase: str
    run: Callable[[dict[str, Any]], dict[str, Any]]

    def __post_init__(self) -> None:
        if self.phase not in ("pre", "post"):
            raise ValueError(f"hook phase must be 'pre' or 'post': {self.phase!r}")
PYEOF
cat > reconciler/phase3/discovery.py <<'PYEOF'
"""Glob discovery of drift rules and run hooks (Phase 3, Section 3).

Two directories are the only integration surface Phase 3 uses:
    validators/drift/rules/*.py   each exposes RULE, a DriftRule
    reconciler/hooks/*.py         each exposes HOOK, a RunHook

Discovery is fail-closed: a module in either directory that does not expose
its symbol is an error, never a silent skip. A silent skip is how an
instrument stops looking without saying so (EC-109).
"""
from __future__ import annotations

import importlib
import pathlib
from typing import Any

from reconciler.phase3.rule_api import DriftRule, RunHook

RULES_DIR = pathlib.Path("validators/drift/rules")
HOOKS_DIR = pathlib.Path("reconciler/hooks")

_SKIP = {"__init__.py"}


class DiscoveryError(RuntimeError):
    pass


def _module_names(directory: pathlib.Path) -> list[str]:
    if not directory.is_dir():
        raise DiscoveryError(f"discovery directory absent: {directory}")
    names = sorted(
        p.stem
        for p in directory.glob("*.py")
        if p.name not in _SKIP and not p.name.startswith("_")
    )
    return names


def _package(directory: pathlib.Path) -> str:
    return str(directory).replace("/", ".").replace("\\", ".")


def discover_rules(directory: pathlib.Path | None = None) -> list[DriftRule]:
    d = directory or RULES_DIR
    out: list[DriftRule] = []
    for name in _module_names(d):
        mod = importlib.import_module(f"{_package(d)}.{name}")
        rule: Any = getattr(mod, "RULE", None)
        if not isinstance(rule, DriftRule):
            raise DiscoveryError(f"{d}/{name}.py exposes no DriftRule named RULE")
        out.append(rule)
    ids = [r.rule_id for r in out]
    if len(ids) != len(set(ids)):
        raise DiscoveryError(f"duplicate rule_id in {d}: {ids}")
    return out


def discover_hooks(directory: pathlib.Path | None = None) -> list[RunHook]:
    d = directory or HOOKS_DIR
    out: list[RunHook] = []
    for name in _module_names(d):
        mod = importlib.import_module(f"{_package(d)}.{name}")
        hook: Any = getattr(mod, "HOOK", None)
        if not isinstance(hook, RunHook):
            raise DiscoveryError(f"{d}/{name}.py exposes no RunHook named HOOK")
        out.append(hook)
    ids = [h.hook_id for h in out]
    if len(ids) != len(set(ids)):
        raise DiscoveryError(f"duplicate hook_id in {d}: {ids}")
    return out
PYEOF
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
cat > validators/drift/rules/canary_rule.py <<'PYEOF'
"""The seeded canary as a discovered comparison row (53.1, AT-102).

The canary is evaluated by the same dispatch as every other rule. It is not
added to the result list afterwards: an after-the-fact writer would keep
producing it while the comparators sat idle, which is EC-109 exactly.
"""
from __future__ import annotations

import datetime as _dt
from typing import Any

from reconciler.phase3.rule_api import DriftRule, Findings
from validators.drift.canary import loader as canary_loader


def _evaluate(context: dict[str, Any]) -> Findings:
    now = context.get("now") or _dt.datetime.now(_dt.timezone.utc)
    canary = canary_loader.load(context.get("canary_config_path"))
    if canary.declared == canary.actual:  # pragma: no cover - loader rejects it
        return []
    return [canary_loader.finding(canary, now)]


RULE = DriftRule(
    rule_id="CANARY-DRIFT-001",
    registry_key="canary",
    evaluate=_evaluate,
)
PYEOF
cat > reconciler/phase3/counts.py <<'PYEOF'
"""Per-registry comparison counts (spec 53.1, mandatory).

Section 53.1: "Every run additionally records its per-registry comparison
counts - how many rows of each registry it actually compared - so that a
silently narrowed comparison is itself visible drift."

The count is structural. Each discovered rule declares the registry bucket it
counts in and reports the rows it actually compared; rows_declared is
computed independently from the declared state. A rule that silently narrows
its own row set therefore produces rows_compared < rows_declared without
anybody having to notice.

The canary counts in its own bucket, 'canary', so that it can never inflate a
real registry's compared-row count.
"""
from __future__ import annotations

import dataclasses
from typing import Any


@dataclasses.dataclass(frozen=True)
class RegistryCount:
    registry_key: str
    rows_declared: int
    rows_compared: int
    rules: tuple[str, ...]

    @property
    def shortfall(self) -> bool:
        return self.rows_compared < self.rows_declared


CANARY_BUCKET = "canary"
CANARY_ROWS_DECLARED = 1


def build_counts(
    declared_rows: dict[str, int],
    compared: list[tuple[str, str, int]],
) -> dict[str, RegistryCount]:
    """Build the per-registry counts.

    declared_rows  registry_key -> rows_declared, computed from declared state
    compared       (registry_key, rule_id, rows_compared) per rule execution

    The canary bucket is always present with rows_declared == 1: section 53.1
    requires the seeded record to exist at all times, so a run that compared
    zero canary rows is a shortfall like any other.
    """
    declared = dict(declared_rows)
    declared.setdefault(CANARY_BUCKET, CANARY_ROWS_DECLARED)

    totals: dict[str, int] = {k: 0 for k in declared}
    rules: dict[str, list[str]] = {k: [] for k in declared}
    for registry_key, rule_id, rows in compared:
        totals.setdefault(registry_key, 0)
        rules.setdefault(registry_key, [])
        declared.setdefault(registry_key, 0)
        totals[registry_key] += int(rows)
        rules[registry_key].append(rule_id)

    return {
        key: RegistryCount(
            registry_key=key,
            rows_declared=declared[key],
            rows_compared=totals.get(key, 0),
            rules=tuple(sorted(rules.get(key, []))),
        )
        for key in sorted(declared)
    }


def shortfall_keys(counts: dict[str, RegistryCount]) -> list[str]:
    return sorted(k for k, c in counts.items() if c.shortfall)


def as_record_payload(counts: dict[str, RegistryCount]) -> list[dict[str, Any]]:
    return [
        {
            "registry_key": c.registry_key,
            "rows_declared": c.rows_declared,
            "rows_compared": c.rows_compared,
            "rules": list(c.rules),
            "shortfall": c.shortfall,
        }
        for c in (counts[k] for k in sorted(counts))
    ]
PYEOF
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
cat > reconciler/tests/test_p3_discovery.py <<'PYEOF'
import pathlib
import textwrap

import pytest

from reconciler.phase3 import discovery as d
from reconciler.phase3.rule_api import DriftRule, RunHook


def test_canary_rule_is_discovered_by_glob():
    ids = [r.rule_id for r in d.discover_rules()]
    assert "CANARY-DRIFT-001" in ids


def test_every_discovered_rule_is_a_driftrule():
    assert all(isinstance(r, DriftRule) for r in d.discover_rules())


def test_hooks_directory_discovers_without_error():
    assert isinstance(d.discover_hooks(), list)


def test_a_module_without_RULE_is_an_error_not_a_silent_skip(tmp_path, monkeypatch):
    pkg = tmp_path / "rules_pkg"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "broken.py").write_text("X = 1\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))
    with pytest.raises(d.DiscoveryError):
        d.discover_rules(pathlib.Path("rules_pkg"))


def test_absent_directory_is_an_error():
    with pytest.raises(d.DiscoveryError):
        d.discover_rules(pathlib.Path("no/such/dir"))


def test_runhook_rejects_an_unknown_phase():
    with pytest.raises(ValueError):
        RunHook(hook_id="x", phase="middle", run=lambda ctx: {})


def test_duplicate_rule_ids_are_rejected(tmp_path, monkeypatch):
    pkg = tmp_path / "dup_pkg"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    body = textwrap.dedent(
        """
        from reconciler.phase3.rule_api import DriftRule
        RULE = DriftRule(rule_id="SAME", registry_key="canary", evaluate=lambda c: [])
        """
    )
    (pkg / "a.py").write_text(body, encoding="utf-8")
    (pkg / "b.py").write_text(body, encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))
    with pytest.raises(d.DiscoveryError):
        d.discover_rules(pathlib.Path("dup_pkg"))
PYEOF
cat > validators/drift/tests/test_canary_rule.py <<'PYEOF'
import datetime as dt

from reconciler.phase3 import counts as c
from reconciler.phase3 import discovery as d

NOW = dt.datetime(2026, 6, 1, 9, 0, tzinfo=dt.timezone.utc)


def _canary_rule():
    return next(r for r in d.discover_rules() if r.rule_id == "CANARY-DRIFT-001")


def test_the_canary_rule_yields_exactly_one_finding():
    findings = _canary_rule().evaluate({"now": NOW})
    assert len(findings) == 1


def test_the_canary_finding_is_marked_as_the_canary():
    f = _canary_rule().evaluate({"now": NOW})[0]
    assert f["is_canary"] is True and f["finding_id"] == "CANARY-DRIFT-001"


def test_the_canary_counts_in_its_own_registry_bucket():
    assert _canary_rule().registry_key == c.CANARY_BUCKET


def test_the_canary_never_inflates_a_real_registry_count():
    counts = c.build_counts(
        {"people.yaml": 10},
        [("people.yaml", "CMP-01", 10), ("canary", "CANARY-DRIFT-001", 1)],
    )
    assert counts["people.yaml"].rows_compared == 10
    assert counts["canary"].rows_compared == 1


def test_a_run_that_compared_no_canary_row_is_a_shortfall():
    counts = c.build_counts({"people.yaml": 10}, [("people.yaml", "CMP-01", 10)])
    assert c.shortfall_keys(counts) == ["canary"]


def test_a_narrowed_registry_is_a_shortfall():
    counts = c.build_counts(
        {"people.yaml": 10},
        [("people.yaml", "CMP-01", 3), ("canary", "CANARY-DRIFT-001", 1)],
    )
    assert c.shortfall_keys(counts) == ["people.yaml"]


def test_a_full_run_has_no_shortfall():
    counts = c.build_counts(
        {"people.yaml": 10, "product.yaml": 8},
        [
            ("people.yaml", "CMP-01", 10),
            ("product.yaml", "CMP-03", 8),
            ("canary", "CANARY-DRIFT-001", 1),
        ],
    )
    assert c.shortfall_keys(counts) == []


def test_count_payload_names_every_bucket_and_its_shortfall_flag():
    counts = c.build_counts({"people.yaml": 1}, [("canary", "CANARY-DRIFT-001", 1)])
    payload = c.as_record_payload(counts)
    keys = [row["registry_key"] for row in payload]
    assert keys == ["canary", "people.yaml"]
    assert all("shortfall" in row for row in payload)
PYEOF
python3 -m pytest -q reconciler/tests/test_p3_discovery.py validators/drift/tests/test_canary_rule.py
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
python3 -m ruff check reconciler validators/drift
git add reconciler validators/drift
git status --porcelain
git commit -m "L3-P3-T02: canary through the real dispatch; per-registry comparison counts (53.1)"
git push -u origin lane/3/p3-t02
gh pr create --base integration --head lane/3/p3-t02 \
  --title "L3-P3-T02 canary dispatch and comparison counts" \
  --body "Lane 3, Phase 3, task T02. Adds the DriftRule/RunHook discovery contract, glob discovery that is fail-closed, the canary as a discovered rule, and the per-registry comparison counts of section 53.1. The canary counts in its own bucket and can never inflate a real registry count. Owned paths only."
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
| --- | --- | --- | --- |
| 1 | The canary is reached by glob discovery, not by a list | `python3 -c "from reconciler.phase3 import discovery as d;print('CANARY-DRIFT-001' in [r.rule_id for r in d.discover_rules()])"` | `True` |
| 2 | Fifteen tests pass | `python3 -m pytest -q reconciler/tests/test_p3_discovery.py validators/drift/tests/test_canary_rule.py 2>&1 \| grep -oE '^[0-9]+ passed'` | `15 passed` |
| 3 | A run that compared no canary row is a shortfall | `python3 -c "from reconciler.phase3 import counts as c;print(c.shortfall_keys(c.build_counts({}, [])))"` | `['canary']` |
| 4 | The rule is reached by discovery, not by registration into a shared list | `grep -c "append" validators/drift/rules/canary_rule.py` | `0` |
| 5 | Lint clean | `python3 -m ruff check reconciler validators/drift` | `All checks passed!` |
| 6 | No foreign path touched | `git -C ~/control-plane diff --name-only origin/integration...HEAD \| grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'` | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd ~/control-plane
python3 -m pytest -q reconciler/tests/test_p3_discovery.py validators/drift/tests/test_canary_rule.py 2>&1 | grep -oE '^[0-9]+ passed'
python3 -c "from reconciler.phase3 import discovery as d;print(sorted(r.rule_id for r in d.discover_rules()))"
python3 -c "from reconciler.phase3 import counts as c;print(c.shortfall_keys(c.build_counts({}, [])))"
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'
```

Expected output, exactly four lines:

```
15 passed
['CANARY-DRIFT-001']
['canary']
0
```

### STOP rule

**Stop and open a blocker if any of the following is true.**

* The test count is not `15 passed`.
* `discover_rules()` returns an empty list, or does not contain `CANARY-DRIFT-001`.
* You are about to make discovery skip a module it cannot load. A silent skip is the failure mode EC-109 names; discovery fails closed or it is not a control.
* You are about to add the canary finding to the result list outside the dispatch, "so that it is always there". That defeats the entire mechanism — universal STOP preamble rule 5.

---

## L3-P3-T03 — The FAILED-run rule — zero findings including the canary

| Field | Value |
| --- | --- |
| **Task id** | `L3-P3-T03` |
| **Size** | M |
| **Depends on** | `L3-P3-T02` |
| **Spec anchors** | §53.1 (*"A run that reports zero findings, including the canary, is a FAILED run, not a clean one"*; *"Silent drift is not permitted. Every reconciliation run writes its result, and a clean run is recorded as clean"*); **AT-102**; **EC-109**; §53.2 Level 5 (*"the reconciliation job itself failing"*); §52 signal table (**SIG-13**, Red, Team Lead) |
| **Files created** | `reconciler/phase3/run_verdict.py`, `reconciler/tests/test_run_verdict.py` |

**Purpose.** Turn the canary's absence into a verdict. This is the task AT-102 rests on: *"a reconciler that finds nothing is assumed broken, never assumed clean."* The verdict function is the only place in this lane that decides `CLEAN` versus `FAILED`, and it is written so that `CLEAN` is the narrow case — it requires the canary to have been found **and** every registry to have met its declared row count. Every other outcome is `FAILED`.

A `FAILED` verdict carries three consequences, all named by the spec and none invented here: response **Level 5** (§53.2, *"the reconciliation job itself failing"*), signal **SIG-13** (§52 signal table), and `gap_procedure_required: true` (AT-102, *"triggers the gap procedure"*).

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
git fetch origin
git switch integration
git pull --ff-only origin integration
git switch -c lane/3/p3-t03
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
cat > reconciler/phase3/run_verdict.py <<'PYEOF'
"""The FAILED-run rule (spec 53.1, AT-102, EC-109).

Section 53.1, verbatim:
    "A run that reports zero findings, including the canary, is a FAILED run,
     not a clean one: it proves the instrument stopped looking, not that
     nothing drifted."

AT-102, verbatim:
    "Every reconciliation run must find the deliberately seeded canary drift.
     A run reporting zero findings - the canary included - is a failed run,
     raises SIG-13 (failed reconciliations), and triggers the gap procedure;
     a reconciler that finds nothing is assumed broken, never assumed clean."

CLEAN is the narrow case. Everything else is FAILED. This module writes no
record: the record stores belong to L4 (PARTITION.md rule 1). It returns the
verdict payload the run record is built from.
"""
from __future__ import annotations

import dataclasses
import datetime as _dt
from typing import Any

from reconciler.phase3 import counts as _counts

CANARY_ID = "CANARY-DRIFT-001"

CLEAN = "CLEAN"
FAILED = "FAILED"
DRIFT = "DRIFT"

SIGNAL_FAILED_RECONCILIATIONS = "SIG-13"  # section 52 signal table
LEVEL_ESCALATE = 5  # section 53.2, "the reconciliation job itself failing"

RECORD_SCHEMA_VERSION = 1  # section 97.2

REASON_CANARY_MISSING = "canary-not-found"
REASON_SHORTFALL = "comparison-count-shortfall"
REASON_ZERO_FINDINGS = "zero-findings"


@dataclasses.dataclass(frozen=True)
class Verdict:
    verdict: str
    reasons: tuple[str, ...]
    level: int | None
    signal: str | None
    gap_procedure_required: bool
    canary_found: bool
    finding_count: int
    shortfall_keys: tuple[str, ...]
    decided_at: str

    def as_record_payload(self) -> dict[str, Any]:
        return {
            "record_schema_version": RECORD_SCHEMA_VERSION,
            "verdict": self.verdict,
            "reasons": list(self.reasons),
            "level": self.level,
            "signal": self.signal,
            "gap_procedure_required": self.gap_procedure_required,
            "canary_found": self.canary_found,
            "finding_count": self.finding_count,
            "shortfall_keys": list(self.shortfall_keys),
            "decided_at": self.decided_at,
        }


def canary_found(findings: list[dict[str, Any]]) -> bool:
    return any(
        f.get("is_canary") is True or f.get("finding_id") == CANARY_ID
        for f in findings
    )


def decide(
    findings: list[dict[str, Any]],
    registry_counts: dict[str, _counts.RegistryCount] | None = None,
    now: _dt.datetime | None = None,
) -> Verdict:
    """Decide the run verdict.

    CLEAN requires all of:
      * the canary was found (53.1, AT-102);
      * no registry reported rows_compared < rows_declared (53.1);
      * no non-canary finding was raised.

    DRIFT is a run that found the canary, had no shortfall, and also found
    real drift. It is a successful run reporting findings - not a failure of
    the instrument.

    Anything else is FAILED.
    """
    stamp = (now or _dt.datetime.now(_dt.timezone.utc)).astimezone(_dt.timezone.utc)
    counts = registry_counts or {}
    shortfalls = tuple(_counts.shortfall_keys(counts)) if counts else ()

    found = canary_found(findings)
    real_findings = [f for f in findings if not f.get("is_canary")]

    reasons: list[str] = []
    if not found:
        reasons.append(REASON_CANARY_MISSING)
    if not findings:
        reasons.append(REASON_ZERO_FINDINGS)
    if shortfalls:
        reasons.append(REASON_SHORTFALL)

    if reasons:
        return Verdict(
            verdict=FAILED,
            reasons=tuple(reasons),
            level=LEVEL_ESCALATE,
            signal=SIGNAL_FAILED_RECONCILIATIONS,
            gap_procedure_required=True,
            canary_found=found,
            finding_count=len(findings),
            shortfall_keys=shortfalls,
            decided_at=stamp.isoformat(),
        )

    return Verdict(
        verdict=DRIFT if real_findings else CLEAN,
        reasons=(),
        level=None,
        signal=None,
        gap_procedure_required=False,
        canary_found=True,
        finding_count=len(findings),
        shortfall_keys=(),
        decided_at=stamp.isoformat(),
    )


def exit_code(verdict: Verdict) -> int:
    """0 CLEAN, 1 DRIFT, 2 FAILED. Fail closed: an unknown verdict is 2."""
    return {CLEAN: 0, DRIFT: 1}.get(verdict.verdict, 2)
PYEOF
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
cat > reconciler/tests/test_run_verdict.py <<'PYEOF'
import datetime as dt

from reconciler.phase3 import counts as c
from reconciler.phase3 import run_verdict as rv

NOW = dt.datetime(2026, 6, 1, 9, 0, tzinfo=dt.timezone.utc)

CANARY = {"finding_id": rv.CANARY_ID, "is_canary": True, "drift_class": "green"}
REAL = {"finding_id": "F-9", "is_canary": False, "drift_class": "amber"}


def _counts(compared_canary=1, people_compared=10):
    rows = [("people.yaml", "CMP-01", people_compared)]
    if compared_canary:
        rows.append(("canary", rv.CANARY_ID, compared_canary))
    return c.build_counts({"people.yaml": 10}, rows)


def test_zero_findings_is_a_failed_run_not_a_clean_one():
    v = rv.decide([], _counts(), NOW)
    assert v.verdict == rv.FAILED


def test_zero_findings_names_both_reasons():
    v = rv.decide([], _counts(), NOW)
    assert rv.REASON_CANARY_MISSING in v.reasons
    assert rv.REASON_ZERO_FINDINGS in v.reasons


def test_a_failed_run_raises_sig_13():
    assert rv.decide([], _counts(), NOW).signal == "SIG-13"


def test_a_failed_run_is_level_5():
    assert rv.decide([], _counts(), NOW).level == 5


def test_a_failed_run_triggers_the_gap_procedure():
    assert rv.decide([], _counts(), NOW).gap_procedure_required is True


def test_findings_without_the_canary_are_still_a_failed_run():
    v = rv.decide([REAL], _counts(), NOW)
    assert v.verdict == rv.FAILED
    assert rv.REASON_CANARY_MISSING in v.reasons


def test_canary_only_run_is_clean():
    v = rv.decide([CANARY], _counts(), NOW)
    assert v.verdict == rv.CLEAN
    assert v.gap_procedure_required is False


def test_canary_plus_real_drift_is_drift_not_failure():
    v = rv.decide([CANARY, REAL], _counts(), NOW)
    assert v.verdict == rv.DRIFT
    assert v.signal is None


def test_a_comparison_shortfall_fails_the_run_even_with_the_canary():
    v = rv.decide([CANARY], _counts(people_compared=2), NOW)
    assert v.verdict == rv.FAILED
    assert rv.REASON_SHORTFALL in v.reasons
    assert v.shortfall_keys == ("people.yaml",)


def test_a_run_that_compared_no_canary_row_fails():
    v = rv.decide([CANARY], _counts(compared_canary=0), NOW)
    assert v.verdict == rv.FAILED
    assert "canary" in v.shortfall_keys


def test_verdict_payload_carries_the_record_schema_version():
    assert rv.decide([CANARY], _counts(), NOW).as_record_payload()[
        "record_schema_version"
    ] == 1


def test_decided_at_is_utc_with_offset():
    assert rv.decide([CANARY], _counts(), NOW).decided_at.endswith("+00:00")


def test_exit_codes_are_zero_one_two():
    assert rv.exit_code(rv.decide([CANARY], _counts(), NOW)) == 0
    assert rv.exit_code(rv.decide([CANARY, REAL], _counts(), NOW)) == 1
    assert rv.exit_code(rv.decide([], _counts(), NOW)) == 2


def test_the_module_writes_no_record():
    src = open("reconciler/phase3/run_verdict.py", encoding="utf-8").read()
    assert "records/" not in src
    assert "open(" not in src
PYEOF
python3 -m pytest -q reconciler/tests/test_run_verdict.py
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
python3 -m ruff check reconciler validators/drift
git add reconciler
git status --porcelain
git commit -m "L3-P3-T03: the FAILED-run rule - zero findings including the canary (AT-102, 53.1)"
git push -u origin lane/3/p3-t03
gh pr create --base integration --head lane/3/p3-t03 \
  --title "L3-P3-T03 the FAILED-run rule" \
  --body "Lane 3, Phase 3, task T03. A run reporting zero findings, the canary included, is FAILED: Level 5, SIG-13, gap procedure required. CLEAN requires the canary found and no per-registry comparison shortfall. Writes no record. Owned paths only."
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
| --- | --- | --- | --- |
| 1 | A zero-finding run is FAILED, never CLEAN | `python3 -c "from reconciler.phase3 import run_verdict as v;print(v.decide([]).verdict)"` | `FAILED` |
| 2 | A FAILED run raises SIG-13 at Level 5 and requires the gap procedure | `python3 -c "from reconciler.phase3 import run_verdict as v;d=v.decide([]);print(d.signal, d.level, d.gap_procedure_required)"` | `SIG-13 5 True` |
| 3 | Fourteen tests pass | `python3 -m pytest -q reconciler/tests/test_run_verdict.py 2>&1 \| grep -oE '^[0-9]+ passed'` | `14 passed` |
| 4 | The verdict module writes nothing | `grep -c "records/" reconciler/phase3/run_verdict.py` | `0` |
| 5 | Lint clean | `python3 -m ruff check reconciler validators/drift` | `All checks passed!` |
| 6 | No foreign path touched | `git -C ~/control-plane diff --name-only origin/integration...HEAD \| grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'` | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd ~/control-plane
python3 -m pytest -q reconciler/tests/test_run_verdict.py 2>&1 | grep -oE '^[0-9]+ passed'
python3 -c "from reconciler.phase3 import run_verdict as v;d=v.decide([]);print(d.verdict, d.signal, d.level, d.gap_procedure_required)"
python3 -c "from reconciler.phase3 import run_verdict as v;print(v.exit_code(v.decide([])))"
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'
```

Expected output, exactly four lines:

```
14 passed
FAILED SIG-13 5 True
2
0
```

### STOP rule

**Stop and open a blocker if any of the following is true.**

* `decide([])` returns anything other than `FAILED`.
* The test count is not `14 passed`.
* A test would have to assert that an empty run is clean. It is not, and §53.1 is unambiguous: *"a reconciler that finds nothing is assumed broken, never assumed clean."*
* You are about to add a fourth verdict value, a "clean-but-degraded", or a flag that suppresses the FAILED verdict for a known-broken comparator. Suppression is universal STOP preamble rule 5 and the exact behaviour EC-109 describes.

---

## L3-P3-T04 — Negative tests: prove the canary catches a blinded instrument

| Field | Value |
| --- | --- |
| **Task id** | `L3-P3-T04` |
| **Size** | M |
| **Depends on** | `L3-P3-T03` |
| **Spec anchors** | **D63** (*"The reconciliation loop is negatively tested"*); §95.4 (the negative-test philosophy §53.1 invokes); **EC-109**; **AT-102** |
| **Files created** | `reconciler/tests/blinding/__init__.py`, `reconciler/tests/blinding/blinders.py`, `reconciler/tests/test_canary_negative.py` |

**Purpose.** A canary nobody has ever seen fire is not evidence. D63 requires the loop to be *negatively* tested: the instrument is deliberately blinded four ways, and each blinding must produce a `FAILED` verdict. If a blinding produces `CLEAN`, the canary does not in fact catch that failure mode and the phase has a hole.

The four blindings are the four ways EC-109 says a run goes vacuous:

| Blinder | What it simulates | Must yield |
| --- | --- | --- |
| `empty_enumeration` | The product enumeration returns nothing; every comparator iterates an empty set | `FAILED` |
| `dispatch_skipped` | Rule discovery returns no rules — the dispatch never ran | `FAILED` |
| `comparator_raised` | A comparator raised and its findings were dropped | `FAILED` |
| `findings_filtered` | Findings were produced and then filtered away downstream | `FAILED` |

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
git fetch origin
git switch integration
git pull --ff-only origin integration
git switch -c lane/3/p3-t04
mkdir -p reconciler/tests/blinding
touch reconciler/tests/blinding/__init__.py
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
cat > reconciler/tests/blinding/blinders.py <<'PYEOF'
"""Deliberate blindings of the reconciliation instrument (D63, EC-109).

D63: "The reconciliation loop is negatively tested: a permanent seeded canary
drift record must be found on every run - zero findings including the canary
is a failed run."

Each blinder simulates one way a run goes vacuous while still completing.
None of them touches production code: each returns the (findings, counts)
pair a blinded run would have produced, which the verdict function then
judges. Adding a blinder is adding a function here and a case to the table in
test_canary_negative.py. Never delete one.
"""
from __future__ import annotations

from typing import Any

from reconciler.phase3 import counts as _counts
from reconciler.phase3 import discovery as _discovery

DECLARED_ROWS = {"people.yaml": 10, "product.yaml": 8}


def _full_compared() -> list[tuple[str, str, int]]:
    return [
        ("people.yaml", "CMP-01", 10),
        ("product.yaml", "CMP-03", 8),
        ("canary", "CANARY-DRIFT-001", 1),
    ]


def _canary_bucket_rules():
    """The canary bucket's rules, reached through the real glob discovery.

    The harness dispatches this bucket only. The other discovered rules read
    run-specific context - commits, anchors, signed run records - that a
    blinding harness has no business fabricating, and each carries its own
    negative tests in its own task.
    """
    return [
        r
        for r in _discovery.discover_rules()
        if r.registry_key == _counts.CANARY_BUCKET
    ]


def healthy(context: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """The control case: a real dispatch over the discovered canary rules."""
    findings: list[dict[str, Any]] = []
    for rule in _canary_bucket_rules():
        findings.extend(rule.evaluate(context))
    return findings, _counts.build_counts(DECLARED_ROWS, _full_compared())


def empty_enumeration(
    context: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Every comparator iterated an empty product set."""
    return [], _counts.build_counts(
        DECLARED_ROWS,
        [("people.yaml", "CMP-01", 0), ("product.yaml", "CMP-03", 0)],
    )


def dispatch_skipped(
    context: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Rule discovery returned nothing: the dispatch never ran."""
    return [], _counts.build_counts(DECLARED_ROWS, [])


def comparator_raised(
    context: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """A comparator raised and its findings were dropped on the floor."""
    findings, counts = healthy(context)
    kept = [f for f in findings if not f.get("is_canary")]
    return kept, counts


def findings_filtered(
    context: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Findings were produced, then filtered away downstream."""
    _, counts = healthy(context)
    return [], counts


BLINDERS = {
    "empty_enumeration": empty_enumeration,
    "dispatch_skipped": dispatch_skipped,
    "comparator_raised": comparator_raised,
    "findings_filtered": findings_filtered,
}
PYEOF
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
cat > reconciler/tests/test_canary_negative.py <<'PYEOF'
"""Negative tests for the seeded canary (D63, EC-109, AT-102).

Every blinded run must be FAILED. A blinding that produces CLEAN is a hole in
the instrument, not a test to relax.
"""
import datetime as dt

import pytest

from reconciler.phase3 import run_verdict as rv
from reconciler.tests.blinding import blinders

NOW = dt.datetime(2026, 6, 1, 9, 0, tzinfo=dt.timezone.utc)
CTX = {"now": NOW}


def test_the_healthy_control_case_finds_the_canary():
    findings, _ = blinders.healthy(CTX)
    assert rv.canary_found(findings) is True


def test_the_healthy_control_case_is_clean():
    findings, counts = blinders.healthy(CTX)
    assert rv.decide(findings, counts, NOW).verdict == rv.CLEAN


@pytest.mark.parametrize("name", sorted(blinders.BLINDERS))
def test_every_blinding_produces_a_failed_run(name):
    findings, counts = blinders.BLINDERS[name](CTX)
    assert rv.decide(findings, counts, NOW).verdict == rv.FAILED


@pytest.mark.parametrize("name", sorted(blinders.BLINDERS))
def test_every_blinding_raises_sig_13(name):
    findings, counts = blinders.BLINDERS[name](CTX)
    assert rv.decide(findings, counts, NOW).signal == "SIG-13"


@pytest.mark.parametrize("name", sorted(blinders.BLINDERS))
def test_every_blinding_requires_the_gap_procedure(name):
    findings, counts = blinders.BLINDERS[name](CTX)
    assert rv.decide(findings, counts, NOW).gap_procedure_required is True


def test_all_four_blinders_are_present():
    assert sorted(blinders.BLINDERS) == [
        "comparator_raised",
        "dispatch_skipped",
        "empty_enumeration",
        "findings_filtered",
    ]


def test_a_dropped_canary_is_detected_even_when_counts_look_full():
    findings, counts = blinders.comparator_raised(CTX)
    v = rv.decide(findings, counts, NOW)
    assert v.verdict == rv.FAILED
    assert rv.REASON_CANARY_MISSING in v.reasons
PYEOF
python3 -m pytest -q reconciler/tests/test_canary_negative.py
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
python3 -m ruff check reconciler validators/drift
git add reconciler
git status --porcelain
git commit -m "L3-P3-T04: negative tests - four blindings, each a FAILED run (D63, EC-109)"
git push -u origin lane/3/p3-t04
gh pr create --base integration --head lane/3/p3-t04 \
  --title "L3-P3-T04 negative tests for the seeded canary" \
  --body "Lane 3, Phase 3, task T04. Four deliberate blindings of the instrument - empty enumeration, skipped dispatch, dropped comparator findings, filtered findings - each proved to produce a FAILED run with SIG-13 and the gap procedure required. D63 requires the loop to be negatively tested. Owned paths only."
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
| --- | --- | --- | --- |
| 1 | Sixteen tests pass | `python3 -m pytest -q reconciler/tests/test_canary_negative.py 2>&1 \| grep -oE '^[0-9]+ passed'` | `16 passed` |
| 2 | Exactly four blinders are registered | `python3 -c "from reconciler.tests.blinding import blinders as b;print(len(b.BLINDERS))"` | `4` |
| 3 | No blinding produces a clean verdict | `python3 -c "import datetime as d;from reconciler.phase3 import run_verdict as v;from reconciler.tests.blinding import blinders as b;n=d.datetime(2026,6,1,tzinfo=d.timezone.utc);print(sorted({v.decide(*b.BLINDERS[k]({'now':n}), now=n).verdict for k in b.BLINDERS}))"` | `['FAILED']` |
| 4 | The healthy control case is clean | `python3 -c "import datetime as d;from reconciler.phase3 import run_verdict as v;from reconciler.tests.blinding import blinders as b;n=d.datetime(2026,6,1,tzinfo=d.timezone.utc);f,c=b.healthy({'now':n});print(v.decide(f,c,n).verdict)"` | `CLEAN` |
| 5 | Lint clean | `python3 -m ruff check reconciler validators/drift` | `All checks passed!` |
| 6 | No foreign path touched | `git -C ~/control-plane diff --name-only origin/integration...HEAD \| grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'` | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd ~/control-plane
python3 -m pytest -q reconciler/tests/test_canary_negative.py 2>&1 | grep -oE '^[0-9]+ passed'
python3 -c "from reconciler.tests.blinding import blinders as b;print(len(b.BLINDERS))"
python3 -c "import datetime as d;from reconciler.phase3 import run_verdict as v;from reconciler.tests.blinding import blinders as b;n=d.datetime(2026,6,1,tzinfo=d.timezone.utc);print(sorted({v.decide(*b.BLINDERS[k]({'now':n}), now=n).verdict for k in b.BLINDERS}))"
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'
```

Expected output, exactly four lines:

```
16 passed
4
['FAILED']
0
```

### STOP rule

**Stop and open a blocker if any of the following is true.**

* Any blinder produces a verdict other than `FAILED`. That is a hole in the instrument. **Do not delete or weaken the blinder** — report it. The blinder is the acceptance test, not the thing under negotiation.
* The healthy control case does not produce `CLEAN`. Either the canary rule is not discovered (re-run T02's SELF-VERIFY) or the counts are wrong.
* The test count is not `16 passed`.
* You are about to mark a blinding `xfail` to get a green run. Universal STOP preamble rule 5.

---

## L3-P3-T05 — D93 — canary-set-first application and the one-cycle fleet hold

| Field | Value |
| --- | --- |
| **Task id** | `L3-P3-T05` |
| **Size** | L |
| **Depends on** | `L3-P3-T03` |
| **Spec anchors** | **D93**; §26.4 (*"a merged registry change is applied by the next reconciliation run to the declared canary set only; the remainder of the fleet is held for one reconciliation cycle and applied only after the canary cycle records a clean run"*); §61.3 (*"The canary set is configurable in `platform.yaml`"*; *"An unexercised canary is not a passed canary"*); §61.5 (*"Never roll a shared change across the fleet automatically"*); §101 #72; §53.1 (what "clean" means) |
| **Files created** | `reconciler/config/staging.yaml`, `reconciler/phase3/registry_stage.py`, `reconciler/tests/test_registry_stage.py` |

**Purpose.** D93 observes that invariant 72 *"protects the fleet from a bad workflow and left declared state uncovered"*, and closes the hole: a merged registry change reaches the declared canary product set first and the fleet is held for one reconciliation cycle. This task computes and holds that staging state. It **applies nothing** — application is the Level-3 write path, which is a later phase and is gated by §99.6 risk 6. Phase 3 produces the plan and the hold; the plan is data.

Three properties are load-bearing and each is tested:

1. **Canary first.** Wave 1 is the intersection of the change's affected products with the declared canary set from `registries/platform.yaml`. The fleet wave is never wave 1 (§61.5).
2. **One clean cycle.** The fleet becomes eligible only after a full reconciliation cycle whose verdict is `CLEAN` by T03's rule — which means *the canary was found and no registry reported a comparison shortfall*. A `DRIFT` or `FAILED` cycle does not release the fleet.
3. **Exercised, not merely observed.** §61.3: *"An unexercised canary is not a passed canary — a product that happened to have no activity during the window has verified nothing."* A canary product with zero compared rows in the cycle does not count as having passed.

**Not in this task, and not this lane's.** §26.4's second rule — an **authority delta** fails CI without a linked decision record ID in the same commit — is a check on registry pull requests. It belongs to the registry validators, `validators/registry/**`, which PARTITION.md gives to **L1**. It is named here so that nobody believes Phase 3 covers it, and is routed to L0 as a cross-lane note, not claimed.

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
git fetch origin
git switch integration
git pull --ff-only origin integration
git switch -c lane/3/p3-t05
mkdir -p reconciler/config reconciler/state/staging
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
cat > reconciler/config/staging.yaml <<'YAMLEOF'
# Registry-change staging (D93, section 26.4).
#
# Section 26.4: "a merged registry change is applied by the next
# reconciliation run to the declared canary set only; the remainder of the
# fleet is held for one reconciliation cycle and applied only after the canary
# cycle records a clean run."
#
# Section 61.5: "Never roll a shared change across the fleet automatically."
# Invariant 72: "Portfolio-wide changes never roll out to the fleet without
# passing a canary first."
staging_version: 1
spec_refs: ["D93", "26.4", "61.3", "61.5", "101 #72"]

# The number of reconciliation cycles the fleet is held after the canary wave.
# Section 26.4 says "one reconciliation cycle". Raising this is a governance
# act; lowering it below 1 contradicts 26.4 and is rejected by the loader.
hold_cycles: 1

# Where the declared canary set is read from. Section 61.3: "The canary set is
# configurable in platform.yaml". That file is L1's; this lane reads it and
# never writes it.
canary_set_source: registries/platform.yaml
canary_set_key: canary_set

# One file per staged change. Directory-per-item, PARTITION.md rule 3.
state_dir: reconciler/state/staging

# Section 61.3: "An unexercised canary is not a passed canary." A canary
# product that compared zero rows during the cycle has verified nothing.
require_canary_products_exercised: true
YAMLEOF
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
cat > reconciler/phase3/registry_stage.py <<'PYEOF'
"""Canary-set-first staging of merged registry changes (D93, spec 26.4).

D93: "A registry change applies to the canary product set first and holds the
fleet for one cycle."

This module computes and holds staging state. It applies nothing. Application
is the Level-3 write path, deferred by section 99.6 risk 6 ("detect-only
first; repair classes enabled one at a time") and out of scope for Phase 3.
"""
from __future__ import annotations

import dataclasses
import datetime as _dt
import pathlib
from typing import Any

import yaml

CONFIG = pathlib.Path("reconciler/config/staging.yaml")

PENDING = "pending"
CANARY_APPLIED = "canary-applied"
FLEET_ELIGIBLE = "fleet-eligible"
FLEET_APPLIED = "fleet-applied"

STATES = (PENDING, CANARY_APPLIED, FLEET_ELIGIBLE, FLEET_APPLIED)

RECORD_SCHEMA_VERSION = 1


class StagingError(RuntimeError):
    """Configuration or declared state is absent or contradicts 26.4."""


def load_config(path: pathlib.Path | None = None) -> dict[str, Any]:
    p = path or CONFIG
    if not p.is_file():
        raise StagingError(f"staging configuration absent: {p}")
    cfg = yaml.safe_load(p.read_text(encoding="utf-8"))
    if int(cfg.get("hold_cycles", 0)) < 1:
        raise StagingError(
            "hold_cycles below 1 contradicts section 26.4, which holds the "
            "fleet for one reconciliation cycle"
        )
    return cfg


def canary_products(
    platform_yaml: pathlib.Path, key: str = "canary_set"
) -> tuple[str, ...]:
    """Read the declared canary set (61.3). Fail closed when it is absent."""
    if not platform_yaml.is_file():
        raise StagingError(f"declared canary set unreadable: {platform_yaml}")
    data = yaml.safe_load(platform_yaml.read_text(encoding="utf-8")) or {}
    block = data.get(key)
    products = (block or {}).get("products") if isinstance(block, dict) else block
    if not products:
        raise StagingError(
            f"{platform_yaml} declares no {key}.products; section 61.3 requires a "
            "configured canary set and 61.5 forbids rolling to the fleet without one"
        )
    return tuple(str(p) for p in products)


@dataclasses.dataclass(frozen=True)
class StagePlan:
    change_id: str
    commit_sha: str
    affected_products: tuple[str, ...]
    canary_wave: tuple[str, ...]
    fleet_wave: tuple[str, ...]
    hold_cycles: int

    def as_record_payload(self) -> dict[str, Any]:
        return {
            "record_schema_version": RECORD_SCHEMA_VERSION,
            "change_id": self.change_id,
            "commit_sha": self.commit_sha,
            "affected_products": list(self.affected_products),
            "canary_wave": list(self.canary_wave),
            "fleet_wave": list(self.fleet_wave),
            "hold_cycles": self.hold_cycles,
        }


def plan(
    change_id: str,
    commit_sha: str,
    affected_products: list[str],
    declared_canary_products: tuple[str, ...],
    cfg: dict[str, Any] | None = None,
) -> StagePlan:
    """Wave 1 is the canary set. The fleet is everything else, held."""
    config = cfg or load_config()
    affected = tuple(sorted(set(affected_products)))
    canary = tuple(p for p in affected if p in set(declared_canary_products))
    fleet = tuple(p for p in affected if p not in set(declared_canary_products))
    if affected and not canary:
        raise StagingError(
            f"change {change_id} affects {list(affected)} and no declared canary "
            "product; section 61.5 forbids reaching the fleet without a canary wave"
        )
    return StagePlan(
        change_id=change_id,
        commit_sha=commit_sha,
        affected_products=affected,
        canary_wave=canary,
        fleet_wave=fleet,
        hold_cycles=int(config["hold_cycles"]),
    )


@dataclasses.dataclass(frozen=True)
class StageState:
    change_id: str
    state: str
    clean_cycles: int
    hold_cycles: int
    updated_at: str

    def as_record_payload(self) -> dict[str, Any]:
        return {
            "record_schema_version": RECORD_SCHEMA_VERSION,
            "change_id": self.change_id,
            "state": self.state,
            "clean_cycles": self.clean_cycles,
            "hold_cycles": self.hold_cycles,
            "updated_at": self.updated_at,
        }


def initial_state(p: StagePlan, now: _dt.datetime) -> StageState:
    return StageState(
        change_id=p.change_id,
        state=PENDING,
        clean_cycles=0,
        hold_cycles=p.hold_cycles,
        updated_at=now.astimezone(_dt.timezone.utc).isoformat(),
    )


def canary_cycle_passed(
    verdict_name: str,
    canary_wave: tuple[str, ...],
    products_exercised: dict[str, int],
    require_exercised: bool = True,
) -> bool:
    """One canary cycle counts only when it was clean AND exercised.

    Section 53.1 / T03: "clean" means the seeded canary was found and no
    registry reported a comparison shortfall.
    Section 61.3: "An unexercised canary is not a passed canary."
    """
    if verdict_name != "CLEAN":
        return False
    if not require_exercised:
        return True
    return bool(canary_wave) and all(
        int(products_exercised.get(p, 0)) > 0 for p in canary_wave
    )


def record_cycle(
    state: StageState,
    p: StagePlan,
    verdict_name: str,
    products_exercised: dict[str, int],
    now: _dt.datetime,
    require_exercised: bool = True,
) -> StageState:
    """Advance the staging state by exactly one reconciliation cycle."""
    stamp = now.astimezone(_dt.timezone.utc).isoformat()
    if state.state == PENDING:
        return dataclasses.replace(state, state=CANARY_APPLIED, updated_at=stamp)
    if state.state == CANARY_APPLIED:
        if not canary_cycle_passed(
            verdict_name, p.canary_wave, products_exercised, require_exercised
        ):
            return dataclasses.replace(state, clean_cycles=0, updated_at=stamp)
        clean = state.clean_cycles + 1
        new_state = FLEET_ELIGIBLE if clean >= state.hold_cycles else CANARY_APPLIED
        return dataclasses.replace(
            state, state=new_state, clean_cycles=clean, updated_at=stamp
        )
    return dataclasses.replace(state, updated_at=stamp)


def may_apply_to_fleet(state: StageState) -> bool:
    """The only sanctioned road to the fleet. 61.5, invariant 72."""
    return state.state == FLEET_ELIGIBLE


def state_path(change_id: str, cfg: dict[str, Any] | None = None) -> pathlib.Path:
    config = cfg or load_config()
    return pathlib.Path(config["state_dir"]) / f"{change_id}.yaml"
PYEOF
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
cat > reconciler/tests/test_registry_stage.py <<'PYEOF'
import datetime as dt
import pathlib

import pytest
import yaml

from reconciler.phase3 import registry_stage as rs

NOW = dt.datetime(2026, 6, 1, 9, 0, tzinfo=dt.timezone.utc)
CANARY = ("alpha", "bravo")
AFFECTED = ["alpha", "bravo", "charlie", "delta"]


def _platform(tmp_path: pathlib.Path, products=("alpha", "bravo")):
    p = tmp_path / "platform.yaml"
    p.write_text(yaml.safe_dump({"canary_set": {"products": list(products)}}), encoding="utf-8")
    return p


def _plan():
    return rs.plan("CHG-1", "a" * 40, AFFECTED, CANARY)


def test_config_loads_and_holds_the_fleet_for_one_cycle():
    assert rs.load_config()["hold_cycles"] == 1


def test_hold_cycles_below_one_is_rejected(tmp_path):
    p = tmp_path / "staging.yaml"
    p.write_text(yaml.safe_dump({"hold_cycles": 0, "state_dir": "x"}), encoding="utf-8")
    with pytest.raises(rs.StagingError):
        rs.load_config(p)


def test_canary_set_is_read_from_declared_state(tmp_path):
    assert rs.canary_products(_platform(tmp_path)) == ("alpha", "bravo")


def test_absent_canary_set_fails_closed(tmp_path):
    p = tmp_path / "platform.yaml"
    p.write_text(yaml.safe_dump({}), encoding="utf-8")
    with pytest.raises(rs.StagingError):
        rs.canary_products(p)


def test_wave_one_is_the_canary_set():
    assert _plan().canary_wave == ("alpha", "bravo")


def test_the_fleet_wave_is_everything_else():
    assert _plan().fleet_wave == ("charlie", "delta")


def test_a_change_touching_no_canary_product_is_refused():
    with pytest.raises(rs.StagingError):
        rs.plan("CHG-2", "b" * 40, ["charlie"], CANARY)


def test_a_new_change_starts_pending():
    assert rs.initial_state(_plan(), NOW).state == rs.PENDING


def test_the_first_cycle_applies_the_canary_wave_only():
    st = rs.record_cycle(
        rs.initial_state(_plan(), NOW), _plan(), "CLEAN", {"alpha": 5, "bravo": 5}, NOW
    )
    assert st.state == rs.CANARY_APPLIED
    assert rs.may_apply_to_fleet(st) is False


def test_one_clean_exercised_cycle_releases_the_fleet():
    p = _plan()
    st = rs.record_cycle(rs.initial_state(p, NOW), p, "CLEAN", {}, NOW)
    st = rs.record_cycle(st, p, "CLEAN", {"alpha": 5, "bravo": 5}, NOW)
    assert st.state == rs.FLEET_ELIGIBLE
    assert rs.may_apply_to_fleet(st) is True


def test_a_failed_cycle_does_not_release_the_fleet():
    p = _plan()
    st = rs.record_cycle(rs.initial_state(p, NOW), p, "CLEAN", {}, NOW)
    st = rs.record_cycle(st, p, "FAILED", {"alpha": 5, "bravo": 5}, NOW)
    assert rs.may_apply_to_fleet(st) is False
    assert st.clean_cycles == 0


def test_a_drift_cycle_does_not_release_the_fleet():
    p = _plan()
    st = rs.record_cycle(rs.initial_state(p, NOW), p, "CLEAN", {}, NOW)
    st = rs.record_cycle(st, p, "DRIFT", {"alpha": 5, "bravo": 5}, NOW)
    assert rs.may_apply_to_fleet(st) is False


def test_an_unexercised_canary_product_does_not_pass_the_cycle():
    p = _plan()
    st = rs.record_cycle(rs.initial_state(p, NOW), p, "CLEAN", {}, NOW)
    st = rs.record_cycle(st, p, "CLEAN", {"alpha": 5, "bravo": 0}, NOW)
    assert rs.may_apply_to_fleet(st) is False


def test_state_is_one_file_per_change():
    assert rs.state_path("CHG-1").name == "CHG-1.yaml"


def test_the_module_applies_nothing():
    src = open("reconciler/phase3/registry_stage.py", encoding="utf-8").read()
    for forbidden in ("requests.", "subprocess", "POST", "PATCH", "DELETE"):
        assert forbidden not in src


def test_payloads_carry_the_record_schema_version():
    p = _plan()
    assert p.as_record_payload()["record_schema_version"] == 1
    assert rs.initial_state(p, NOW).as_record_payload()["record_schema_version"] == 1
PYEOF
python3 -m pytest -q reconciler/tests/test_registry_stage.py
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
python3 -m ruff check reconciler validators/drift
git add reconciler
git status --porcelain
git commit -m "L3-P3-T05: D93 canary-set-first staging and the one-cycle fleet hold (26.4, 61.5)"
git push -u origin lane/3/p3-t05
gh pr create --base integration --head lane/3/p3-t05 \
  --title "L3-P3-T05 canary-set-first registry staging" \
  --body "Lane 3, Phase 3, task T05. A merged registry change stages to the declared canary set first and the fleet is held for one reconciliation cycle; the fleet is released only by a CLEAN cycle in which every canary product was actually exercised. Applies nothing - the plan is data. Owned paths only."
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
| --- | --- | --- | --- |
| 1 | The fleet is held for exactly one cycle | `python3 -c "from reconciler.phase3 import registry_stage as s;print(s.load_config()['hold_cycles'])"` | `1` |
| 2 | Sixteen tests pass | `python3 -m pytest -q reconciler/tests/test_registry_stage.py 2>&1 \| grep -oE '^[0-9]+ passed'` | `16 passed` |
| 3 | A non-CLEAN cycle never releases the fleet | `python3 -m pytest -q reconciler/tests/test_registry_stage.py -k "not_release" 2>&1 \| grep -oE '^[0-9]+ passed'` | `2 passed` |
| 4 | The module performs no write and no mutation call | `grep -c "subprocess" reconciler/phase3/registry_stage.py` | `0` |
| 5 | Staging state is one file per change | `python3 -c "from reconciler.phase3 import registry_stage as s;print(s.state_path('CHG-1'))"` | `reconciler/state/staging/CHG-1.yaml` |
| 6 | No foreign path touched | `git -C ~/control-plane diff --name-only origin/integration...HEAD \| grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'` | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd ~/control-plane
python3 -m pytest -q reconciler/tests/test_registry_stage.py 2>&1 | grep -oE '^[0-9]+ passed'
python3 -c "from reconciler.phase3 import registry_stage as s;print(s.load_config()['hold_cycles'])"
python3 -c "from reconciler.phase3 import registry_stage as s;p=s.plan('C','a'*40,['alpha','charlie'],('alpha',));print(p.canary_wave, p.fleet_wave)"
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'
```

Expected output, exactly four lines:

```
16 passed
1
('alpha',) ('charlie',)
0
```

### STOP rule

**Stop and open a blocker if any of the following is true.**

* `registries/platform.yaml` on `integration` declares no `canary_set.products`. That is an L1 dependency. *Decision needed from L0*: `Which L1 task populates registries/platform.yaml canary_set.products, and has it merged to integration?` Do **not** invent a canary set — §61.3 says *"Do not hard-code specific products as permanent canaries."*
* The test count is not `16 passed`.
* You are about to make `hold_cycles: 0`, or to add a "skip the hold for small changes" path. §26.4 holds the fleet for one cycle and §61.5 is absolute: *"Never roll a shared change across the fleet automatically."*
* You are about to write code in this module that applies a change. Phase 3 applies nothing.

---

## L3-P3-T06 — D93 — reconciler write-scope allowlist and machine-registry-write drift rule

| Field | Value |
| --- | --- |
| **Task id** | `L3-P3-T06` |
| **Size** | M |
| **Depends on** | `L3-P3-T05` |
| **Spec anchors** | **D93** (*"The reconciler's own write scope is narrowed to generated `derived/**` files the registries reference, so a machine write to a registry becomes detectable Blocking drift rather than an in-scope write"*); §40.1 (control plane: *"No bypass actor exists"*; machine write *"None, except the reconciler's declared repair scope (Section 26.4)"*); §53.2 Level 4; §53.1 (*"A workflow-file change pushed by a machine identity is Blocking-class drift"*); **DR-3.1** |
| **Files created** | `reconciler/config/anchoring.yaml`, `reconciler/phase3/write_scope.py`, `validators/drift/rules/machine_registry_write_rule.py`, `reconciler/tests/test_write_scope_allowlist.py`, `validators/drift/tests/test_machine_registry_write_rule.py` |

**Purpose.** D93's point is negative: because the reconciler's write scope is narrow, **a registry write falls outside it and is therefore detectable**. This task supplies the two halves Phase 3 owes that sentence — the allowlist **as data**, so that DR-3.1's resolution is a configuration edit and never a code edit, and a discovered drift rule that fires Blocking on any path a machine identity wrote outside it.

**This task edits nothing.** Phase 2 shipped `validators/drift/write_scope_guard.py` and `reconciler/credential/write_scope.yaml`; both are left exactly as they are (Section 3, additive-only). Phase 3 adds a *discovered rule* — reachable by glob from the run dispatch — whose allowlist comes from configuration.

**On `reconciler/config/anchoring.yaml`.** DR-3.1 names T10 as the file's creator. T06 needs the same file, and the two tasks are on two branches. The heredoc below is **byte-identical** to T10's: an add/add of identical content merges without conflict, and criterion 1 in both tasks is the same SHA-256. Do not reformat it, do not re-indent it, do not add a comment to it. If the file already exists on your branch after a rebase, skip the heredoc and go straight to the checksum check.

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
git fetch origin
git switch integration
git pull --ff-only origin integration
git switch -c lane/3/p3-t06
mkdir -p reconciler/config
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
if [ ! -f reconciler/config/anchoring.yaml ]; then
cat > reconciler/config/anchoring.yaml <<'YAMLEOF'
# reconciler/config/anchoring.yaml
#
# DR-3.1 ratified: bytes unchanged. T06 and T10 both assert sha256 `2dffc3c7…`
# — identical content makes the two branches merge correctly.
#
# D107: "the reconciler anchors the records head SHA into the protected
# control-plane repository each run, so a head that does not descend from the
# last anchor is proof of rewriting at Level 5."
# D93:  "The reconciler's own write scope is narrowed to generated derived/**
# files the registries reference, so a machine write to a registry becomes
# detectable Blocking drift rather than an in-scope write."
config_version: 1
spec_refs: ["D107", "D93", "53.2", "63.1", "97.1", "101 #47"]

# Destination of the per-run anchor inside the control-plane repository.
# Written at run time by the reconciler credential. NOT created in the
# repository by any Phase 3 task: derived/** is owned by no lane (DR-3.1).
anchor_path: derived/anchors/records-head.yaml

# The complete set of path globs the reconciler credential may write in the
# control-plane repository. Read as data by T06. Never hard-coded.
write_scope_allowlist:
  - derived/**

# The records clone the anchor is computed from. Read-only in this phase.
records_clone_path: ~/control-plane-records
records_ref: HEAD
YAMLEOF
fi
sha256sum reconciler/config/anchoring.yaml
```

The checksum printed must be exactly:

```
2dffc3c76487e863ea190cbca4bd683a402a947e0d1e2204b0f0f9b71eb215ee  reconciler/config/anchoring.yaml
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
cat > reconciler/phase3/write_scope.py <<'PYEOF'
"""The reconciler write-scope allowlist, as data (D93, DR-3.1).

D93: "The reconciler's own write scope is narrowed to generated [...] files
the registries reference, so a machine write to a registry becomes detectable
Blocking drift rather than an in-scope write."

The glob the quotation names is deliberately absent from this module: the
allowlist is configuration, never code. DR-3.1 is unresolved, and when L0
rules, one line of reconciler/config/anchoring.yaml changes and nothing here
changes. Matching is a whitelist and fails closed - an unrecognised path is
out of scope, not in scope.
"""
from __future__ import annotations

import fnmatch
import pathlib
from typing import Any

import yaml

CONFIG = pathlib.Path("reconciler/config/anchoring.yaml")

ALLOWLIST_KEY = "write_scope_allowlist"


class WriteScopeError(RuntimeError):
    """The allowlist is absent or empty. Never default to permissive."""


def load_allowlist(path: pathlib.Path | None = None) -> tuple[str, ...]:
    p = path or CONFIG
    if not p.is_file():
        raise WriteScopeError(
            f"write-scope allowlist absent: {p}. Section 40.1 admits no machine "
            "write to the control-plane repository except the reconciler's "
            "declared repair scope, so an absent declaration is not an empty "
            "one - it is a stop"
        )
    data: Any = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    globs = data.get(ALLOWLIST_KEY)
    if not globs:
        raise WriteScopeError(f"{p} declares no {ALLOWLIST_KEY}")
    return tuple(str(g) for g in globs)


def in_scope(path: str, allowlist: tuple[str, ...] | None = None) -> bool:
    """True only when the path matches a declared glob. Whitelist, fail closed."""
    globs = allowlist if allowlist is not None else load_allowlist()
    normalised = path.lstrip("./")
    return any(fnmatch.fnmatch(normalised, g) for g in globs)


def out_of_scope_paths(
    paths: list[str], allowlist: tuple[str, ...] | None = None
) -> list[str]:
    globs = allowlist if allowlist is not None else load_allowlist()
    return sorted(p for p in paths if not in_scope(p, globs))
PYEOF
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
cat > validators/drift/rules/machine_registry_write_rule.py <<'PYEOF'
"""A machine write outside the declared scope is Blocking drift (D93).

D93 makes the detection possible by narrowing the scope; this rule performs
it. Section 53.2 Level 4: "Fail CI or block the deployment path until
resolved", applying to Blocking-class drift.

Context keys read:
    commits            list of {sha, author_login, committer_login,
                                changed_paths: [str]}
    machine_identities list of logins that are machine identities
    now                timezone-aware datetime (optional)

A commit by a human identity produces no finding here: this rule is about
machine writes only. Human registry edits travel the section 26.4 owner-review
lane and are governed there.
"""
from __future__ import annotations

import datetime as _dt
from typing import Any

from reconciler.phase3 import write_scope
from reconciler.phase3.rule_api import DriftRule, Findings

RULE_ID = "D93-MACHINE-WRITE-OUT-OF-SCOPE"
REGISTRY_KEY = "control-plane-writes"

DRIFT_CLASS = "blocking"  # D93, verbatim: "detectable Blocking drift"
LEVEL = 4  # section 53.2, Level 4 - Block


def _machine(commit: dict[str, Any], machine_identities: set[str]) -> str | None:
    for key in ("author_login", "committer_login"):
        login = (commit.get(key) or "").lower()
        if login and login in machine_identities:
            return login
    return None


def _evaluate(context: dict[str, Any]) -> Findings:
    now = context.get("now") or _dt.datetime.now(_dt.timezone.utc)
    allowlist = write_scope.load_allowlist(context.get("write_scope_config"))
    machine_identities = {
        str(m).lower() for m in (context.get("machine_identities") or [])
    }
    findings: Findings = []
    for commit in context.get("commits") or []:
        login = _machine(commit, machine_identities)
        if login is None:
            continue
        for path in write_scope.out_of_scope_paths(
            list(commit.get("changed_paths") or []), allowlist
        ):
            findings.append(
                {
                    "record_schema_version": 1,
                    "finding_id": f"{RULE_ID}:{commit.get('sha', '')[:12]}:{path}",
                    "registry_key": REGISTRY_KEY,
                    "comparison_row": "Reconciler declared write scope (D93)",
                    "declared": f"allowlist={list(allowlist)}",
                    "actual": path,
                    "drift_class": DRIFT_CLASS,
                    "level": LEVEL,
                    "identity": login,
                    "commit_sha": commit.get("sha"),
                    "is_canary": False,
                    "observed_at": now.astimezone(_dt.timezone.utc).isoformat(),
                    "acknowledged_by": None,
                    "acknowledged_at": None,
                }
            )
    return findings


RULE = DriftRule(rule_id=RULE_ID, registry_key=REGISTRY_KEY, evaluate=_evaluate)
PYEOF
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
cat > reconciler/tests/test_write_scope_allowlist.py <<'PYEOF'
import pathlib

import pytest
import yaml

from reconciler.phase3 import write_scope as ws


def test_the_allowlist_loads_from_configuration():
    assert ws.load_allowlist() == ("derived/**",)


def test_a_derived_path_is_in_scope():
    assert ws.in_scope("derived/anchors/records-head.yaml") is True


def test_a_registry_path_is_out_of_scope():
    assert ws.in_scope("registries/people.yaml") is False


def test_a_workflow_path_is_out_of_scope():
    assert ws.in_scope(".github/workflows/deploy-production.yml") is False


def test_an_unrecognised_path_is_out_of_scope_not_in_scope():
    assert ws.in_scope("something/entirely/new.txt") is False


def test_out_of_scope_paths_are_returned_sorted():
    got = ws.out_of_scope_paths(
        ["registries/people.yaml", "derived/x.yaml", "policies.yaml"]
    )
    assert got == ["policies.yaml", "registries/people.yaml"]


def test_an_absent_allowlist_fails_closed(tmp_path):
    with pytest.raises(ws.WriteScopeError):
        ws.load_allowlist(tmp_path / "absent.yaml")


def test_an_empty_allowlist_fails_closed(tmp_path):
    p = tmp_path / "anchoring.yaml"
    p.write_text(yaml.safe_dump({"write_scope_allowlist": []}), encoding="utf-8")
    with pytest.raises(ws.WriteScopeError):
        ws.load_allowlist(p)


def test_the_allowlist_is_never_hard_coded_in_the_module():
    src = pathlib.Path("reconciler/phase3/write_scope.py").read_text(encoding="utf-8")
    assert "derived/" not in src


def test_phase_two_write_scope_guard_is_untouched():
    """Section 3: no Phase 3 task edits a Phase 1 or Phase 2 file."""
    assert pathlib.Path("validators/drift/write_scope_guard.py").is_file()
PYEOF
cat > validators/drift/tests/test_machine_registry_write_rule.py <<'PYEOF'
import datetime as dt

from reconciler.phase3 import discovery as d
from validators.drift.rules import machine_registry_write_rule as r

NOW = dt.datetime(2026, 6, 1, 9, 0, tzinfo=dt.timezone.utc)
MACHINES = ["reconciler-bot"]


def _ctx(paths, login="reconciler-bot"):
    return {
        "now": NOW,
        "machine_identities": MACHINES,
        "commits": [
            {
                "sha": "c" * 40,
                "author_login": login,
                "committer_login": login,
                "changed_paths": paths,
            }
        ],
    }


def test_the_rule_is_discovered_by_glob():
    assert r.RULE_ID in [x.rule_id for x in d.discover_rules()]


def test_a_machine_write_to_a_registry_is_blocking():
    findings = r.RULE.evaluate(_ctx(["registries/people.yaml"]))
    assert len(findings) == 1
    assert findings[0]["drift_class"] == "blocking"


def test_a_machine_registry_write_is_level_4():
    assert r.RULE.evaluate(_ctx(["registries/people.yaml"]))[0]["level"] == 4


def test_a_machine_write_inside_derived_is_not_drift():
    assert r.RULE.evaluate(_ctx(["derived/anchors/records-head.yaml"])) == []


def test_a_machine_workflow_write_is_blocking():
    findings = r.RULE.evaluate(_ctx([".github/workflows/ci.yml"]))
    assert findings[0]["drift_class"] == "blocking"


def test_a_human_write_produces_no_finding_here():
    assert r.RULE.evaluate(_ctx(["registries/people.yaml"], login="a-person")) == []


def test_one_finding_per_out_of_scope_path():
    findings = r.RULE.evaluate(_ctx(["registries/people.yaml", "policies.yaml"]))
    assert len(findings) == 2


def test_the_finding_names_the_identity_and_the_commit():
    f = r.RULE.evaluate(_ctx(["registries/people.yaml"]))[0]
    assert f["identity"] == "reconciler-bot"
    assert f["commit_sha"] == "c" * 40


def test_the_finding_carries_the_acknowledgement_fields():
    f = r.RULE.evaluate(_ctx(["registries/people.yaml"]))[0]
    assert "acknowledged_by" in f and "acknowledged_at" in f


def test_no_commits_yields_no_findings():
    assert r.RULE.evaluate({"now": NOW, "machine_identities": MACHINES}) == []
PYEOF
python3 -m pytest -q reconciler/tests/test_write_scope_allowlist.py validators/drift/tests/test_machine_registry_write_rule.py
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
python3 -m ruff check reconciler validators/drift
git add reconciler validators/drift
git status --porcelain
git commit -m "L3-P3-T06: D93 write-scope allowlist as data and the machine-write drift rule"
git push -u origin lane/3/p3-t06
gh pr create --base integration --head lane/3/p3-t06 \
  --title "L3-P3-T06 write-scope allowlist and machine-write drift rule" \
  --body "Lane 3, Phase 3, task T06. The reconciler write-scope allowlist is read as configuration (DR-3.1 interim default derived/**) and a discovered drift rule raises Blocking, Level 4, on any path a machine identity wrote outside it. Phase 2's write_scope_guard.py is untouched. Owned paths only."
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
| --- | --- | --- | --- |
| 1 | The DR-3.1 configuration is byte-identical to T10's copy | `sha256sum reconciler/config/anchoring.yaml \| cut -d' ' -f1` | `2dffc3c76487e863ea190cbca4bd683a402a947e0d1e2204b0f0f9b71eb215ee` |
| 2 | The allowlist is data, not code | `grep -c "derived/" reconciler/phase3/write_scope.py` | `0` |
| 3 | Twenty tests pass | `python3 -m pytest -q reconciler/tests/test_write_scope_allowlist.py validators/drift/tests/test_machine_registry_write_rule.py 2>&1 \| grep -oE '^[0-9]+ passed'` | `20 passed` |
| 4 | A machine write to a registry is Blocking | `python3 -c "import datetime as d;from validators.drift.rules import machine_registry_write_rule as r;n=d.datetime(2026,6,1,tzinfo=d.timezone.utc);f=r.RULE.evaluate({'now':n,'machine_identities':['bot'],'commits':[{'sha':'x'*40,'author_login':'bot','committer_login':'bot','changed_paths':['registries/people.yaml']}]});print(f[0]['drift_class'], f[0]['level'])"` | `blocking 4` |
| 5 | Phase 2's guard was not edited | `git -C ~/control-plane diff --name-only origin/integration...HEAD \| grep -c "write_scope_guard.py"` | `0` |
| 6 | No foreign path touched | `git -C ~/control-plane diff --name-only origin/integration...HEAD \| grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'` | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd ~/control-plane
sha256sum reconciler/config/anchoring.yaml | cut -d' ' -f1
python3 -m pytest -q reconciler/tests/test_write_scope_allowlist.py validators/drift/tests/test_machine_registry_write_rule.py 2>&1 | grep -oE '^[0-9]+ passed'
python3 -c "from reconciler.phase3 import write_scope as w;print(w.load_allowlist(), w.in_scope('registries/people.yaml'))"
git diff --name-only origin/integration...HEAD | grep -c "write_scope_guard.py" || true
```

Expected output, exactly four lines:

```
2dffc3c76487e863ea190cbca4bd683a402a947e0d1e2204b0f0f9b71eb215ee
20 passed
('derived/**',) False
0
```

### STOP rule

**Stop and open a blocker if any of the following is true.**

* The checksum is not `2dffc3c7…15ee`. The two copies of `reconciler/config/anchoring.yaml` must be identical or T06 and T10 will conflict on merge. Re-create the file from the heredoc exactly; do not hand-edit it.
* The test count is not `20 passed`.
* You are about to widen the allowlist so that a failing test passes. The allowlist is the control (§40.1: the control plane admits *no* machine write except the declared repair scope). Universal STOP preamble rule 5.
* You are about to edit `validators/drift/write_scope_guard.py` or `reconciler/credential/write_scope.yaml`. Those are Phase 2's. Section 3 forbids it.
* `validators/drift/write_scope_guard.py` does not exist on `integration`. Phase 2 has not merged. *Decision needed from L0*: `Has L3 Phase 2 (L3-02-09) merged to integration?`

---

## L3-P3-T07 — §53.7 — control-loop gap detection

| Field | Value |
| --- | --- |
| **Task id** | `L3-P3-T07` |
| **Size** | M |
| **Depends on** | `L3-P3-T03` |
| **Spec anchors** | §53.7 (*"The control loop can fail in two directions. It can go dark — a reconciliation gap, an export gap, or a health-report gap. It can also run and repair against a wrongly-computed declared state"*); §51.2 (*Reconciliation freshness*: *"Red at 48 hours, Level 5 escalation at 72"*; *Health report freshness*: *"Refreshed daily"*, Amber; *Drift detection freshness*: *"Security-class checks at least hourly"*, Red); §53.2 Level 5; **EC-109**; **AT-032** |
| **Files created** | `reconciler/config/gap.yaml`, `reconciler/phase3/gap_detect.py`, `reconciler/tests/test_gap_detect.py` |

**Purpose.** Detect that the loop went dark, and say exactly which window is unverified. This is the input the gap procedure of T08 consumes. It is also the self-observability half of **AT-032**: the operating system detects a failure in its own reconciliation, health job and drift-detection freshness, and does so from recorded timestamps rather than from a human noticing.

Every threshold is read from `reconciler/config/gap.yaml` and every value in that file is a §51.2 quotation. **One threshold is deliberately unarmed**: the export gap. §51.2 does not state an export cadence and the organisation export job belongs to L5 (`ops-vm/**`); the config key is therefore `null` and the detector returns `input_unavailable` for that kind rather than inventing a window. That is a stated gap, routed to L0, not a silent one.

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
git fetch origin
git switch integration
git pull --ff-only origin integration
git switch -c lane/3/p3-t07
mkdir -p reconciler/config
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
cat > reconciler/config/gap.yaml <<'YAMLEOF'
# Control-loop gap thresholds (section 53.7, thresholds from section 51.2).
#
# Section 53.7: "The control loop can fail in two directions. It can go dark -
# a reconciliation gap, an export gap, or a health-report gap. It can also run
# and repair against a wrongly-computed declared state, which completes,
# records clean, and is therefore invisible to every check that asks only
# whether the loop ran."
#
# Every number below is quoted from section 51.2. Do not invent one.
gap_version: 1
spec_refs: ["53.7", "51.2", "53.2", "EC-109", "AT-032"]

kinds:
  reconciliation:
    # 51.2: "Full reconciliation completes at least daily";
    #       "Red at 48 hours, Level 5 escalation at 72".
    expected_max_age_hours: 24
    red_after_hours: 48
    level_5_after_hours: 72
    self_observed: true
  health-report:
    # 51.2: "Refreshed daily"; "Amber; degrade openly rather than show stale
    # data as current".
    expected_max_age_hours: 24
    red_after_hours: null
    level_5_after_hours: null
    self_observed: true
  drift-detection:
    # 51.2: "Security-class checks at least hourly"; response "Red".
    expected_max_age_hours: 1
    red_after_hours: 1
    level_5_after_hours: null
    self_observed: true
  export:
    # 51.2 states no export cadence, and the organisation export job is L5's
    # (ops-vm/**). UNARMED until L0 records the declared cadence: the detector
    # returns input_unavailable rather than inventing a window (SIG-34).
    expected_max_age_hours: null
    red_after_hours: null
    level_5_after_hours: null
    self_observed: false
YAMLEOF
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
cat > reconciler/phase3/gap_detect.py <<'PYEOF'
"""Control-loop gap detection (spec 53.7, thresholds from 51.2).

Two directions of failure, both detected here:
  * the loop went dark - a reconciliation, export or health-report gap;
  * the loop ran and recorded clean while checking nothing (EC-109), which
    T03's verdict function reports as FAILED and which this module converts
    into a gap window.

Detection only. Nothing here repairs, writes a record or notifies.
"""
from __future__ import annotations

import dataclasses
import datetime as _dt
import pathlib
from typing import Any

import yaml

CONFIG = pathlib.Path("reconciler/config/gap.yaml")

LEVEL_ESCALATE = 5  # section 53.2 Level 5
LEVEL_WARN = 2  # section 53.2 Level 2

CLASS_AMBER = "amber"
CLASS_RED = "red"

KIND_VACUOUS_RUN = "vacuous-run"
KIND_LOOP_RAN_WRONG = "loop-ran-wrong"

INPUT_UNAVAILABLE = "input_unavailable"

RECORD_SCHEMA_VERSION = 1


class GapConfigError(RuntimeError):
    pass


@dataclasses.dataclass(frozen=True)
class Gap:
    kind: str
    window_start: str
    window_end: str
    age_hours: float
    drift_class: str
    level: int
    reason: str

    def as_record_payload(self) -> dict[str, Any]:
        return {
            "record_schema_version": RECORD_SCHEMA_VERSION,
            "kind": self.kind,
            "window_start": self.window_start,
            "window_end": self.window_end,
            "age_hours": round(self.age_hours, 3),
            "drift_class": self.drift_class,
            "level": self.level,
            "reason": self.reason,
        }


def load_config(path: pathlib.Path | None = None) -> dict[str, Any]:
    p = path or CONFIG
    if not p.is_file():
        raise GapConfigError(f"gap configuration absent: {p}")
    cfg = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    if not cfg.get("kinds"):
        raise GapConfigError(f"{p} declares no kinds")
    return cfg


def unarmed_kinds(cfg: dict[str, Any] | None = None) -> list[str]:
    """Kinds with no declared threshold. Named, never silently skipped."""
    config = cfg or load_config()
    return sorted(
        k
        for k, v in config["kinds"].items()
        if v.get("expected_max_age_hours") is None
    )


def self_observed_kinds(cfg: dict[str, Any] | None = None) -> list[str]:
    """AT-032: reconciliation, health job and dashboard freshness."""
    config = cfg or load_config()
    return sorted(k for k, v in config["kinds"].items() if v.get("self_observed"))


def _iso(ts: _dt.datetime) -> str:
    return ts.astimezone(_dt.timezone.utc).isoformat()


def detect(
    last_success: dict[str, _dt.datetime],
    now: _dt.datetime,
    cfg: dict[str, Any] | None = None,
) -> tuple[list[Gap], list[str]]:
    """Return (gaps, unavailable_kinds).

    unavailable_kinds names every kind that could not be evaluated - because
    it is unarmed, or because no last-success timestamp was supplied. Section
    52.2's arming discipline: an unevaluated kind is reported as unevaluated,
    never counted as clean.
    """
    config = cfg or load_config()
    gaps: list[Gap] = []
    unavailable: list[str] = []
    for kind, rule in sorted(config["kinds"].items()):
        expected = rule.get("expected_max_age_hours")
        if expected is None:
            unavailable.append(kind)
            continue
        seen = last_success.get(kind)
        if seen is None:
            unavailable.append(kind)
            continue
        if seen.tzinfo is None:
            raise GapConfigError(f"{kind}: timestamp is naive (97.1: UTC with offset)")
        age = (now - seen).total_seconds() / 3600.0
        if age <= float(expected):
            continue
        level_5_after = rule.get("level_5_after_hours")
        red_after = rule.get("red_after_hours")
        if level_5_after is not None and age > float(level_5_after):
            drift_class, level = CLASS_RED, LEVEL_ESCALATE
            reason = f"{kind} silent for {age:.1f}h (51.2 level-5 threshold)"
        elif red_after is not None and age > float(red_after):
            drift_class, level = CLASS_RED, LEVEL_WARN
            reason = f"{kind} silent for {age:.1f}h (51.2 red threshold)"
        else:
            drift_class, level = CLASS_AMBER, LEVEL_WARN
            reason = f"{kind} silent for {age:.1f}h (51.2 freshness objective)"
        gaps.append(
            Gap(
                kind=kind,
                window_start=_iso(seen),
                window_end=_iso(now),
                age_hours=age,
                drift_class=drift_class,
                level=level,
                reason=reason,
            )
        )
    return gaps, sorted(unavailable)


def gap_from_verdict(
    verdict_name: str,
    window_start: _dt.datetime,
    now: _dt.datetime,
    reasons: tuple[str, ...] = (),
) -> Gap | None:
    """A FAILED run is a gap window (EC-109, AT-102).

    The loop ran, reported, and checked nothing. Section 53.2 Level 5 covers
    "the reconciliation job itself failing".
    """
    if verdict_name != "FAILED":
        return None
    return Gap(
        kind=KIND_VACUOUS_RUN,
        window_start=_iso(window_start),
        window_end=_iso(now),
        age_hours=(now - window_start).total_seconds() / 3600.0,
        drift_class=CLASS_RED,
        level=LEVEL_ESCALATE,
        reason="run reported FAILED: " + (", ".join(reasons) or "instrument failure"),
    )


def loop_ran_wrong_gap(
    repair_class_id: str, window_start: _dt.datetime, window_end: _dt.datetime
) -> Gap:
    """Section 53.7: "When the loop ran wrong."

    "A repair class discovered to have written incorrect state is a Level 5
    escalation in its own right (53.2)."
    """
    return Gap(
        kind=KIND_LOOP_RAN_WRONG,
        window_start=_iso(window_start),
        window_end=_iso(window_end),
        age_hours=(window_end - window_start).total_seconds() / 3600.0,
        drift_class=CLASS_RED,
        level=LEVEL_ESCALATE,
        reason=f"repair class {repair_class_id} wrote incorrect state (53.7)",
    )
PYEOF
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
cat > reconciler/tests/test_gap_detect.py <<'PYEOF'
import datetime as dt

import pytest

from reconciler.phase3 import gap_detect as gd

NOW = dt.datetime(2026, 6, 10, 12, 0, tzinfo=dt.timezone.utc)


def _ago(hours):
    return NOW - dt.timedelta(hours=hours)


def test_config_loads():
    assert "reconciliation" in gd.load_config()["kinds"]


def test_a_fresh_loop_reports_no_gap():
    gaps, _ = gd.detect(
        {"reconciliation": _ago(1), "health-report": _ago(1), "drift-detection": _ago(0.5)},
        NOW,
    )
    assert gaps == []


def test_reconciliation_silent_36h_is_amber_level_2():
    gaps, _ = gd.detect({"reconciliation": _ago(36)}, NOW)
    g = next(x for x in gaps if x.kind == "reconciliation")
    assert (g.drift_class, g.level) == ("amber", 2)


def test_reconciliation_silent_50h_is_red():
    gaps, _ = gd.detect({"reconciliation": _ago(50)}, NOW)
    g = next(x for x in gaps if x.kind == "reconciliation")
    assert g.drift_class == "red"


def test_reconciliation_silent_80h_is_level_5():
    gaps, _ = gd.detect({"reconciliation": _ago(80)}, NOW)
    g = next(x for x in gaps if x.kind == "reconciliation")
    assert g.level == 5


def test_health_report_stale_two_days_is_amber():
    gaps, _ = gd.detect({"health-report": _ago(48)}, NOW)
    g = next(x for x in gaps if x.kind == "health-report")
    assert g.drift_class == "amber"


def test_drift_detection_silent_two_hours_is_red():
    gaps, _ = gd.detect({"drift-detection": _ago(2)}, NOW)
    g = next(x for x in gaps if x.kind == "drift-detection")
    assert g.drift_class == "red"


def test_the_gap_window_names_both_ends():
    gaps, _ = gd.detect({"reconciliation": _ago(36)}, NOW)
    g = gaps[0]
    assert g.window_start.endswith("+00:00") and g.window_end.endswith("+00:00")


def test_the_export_kind_is_unarmed_and_named_not_skipped():
    assert "export" in gd.unarmed_kinds()


def test_an_unevaluated_kind_is_reported_unavailable_never_clean():
    _, unavailable = gd.detect({"reconciliation": _ago(1)}, NOW)
    assert "export" in unavailable and "health-report" in unavailable


def test_at032_self_observed_kinds_are_the_three_named_ones():
    assert gd.self_observed_kinds() == [
        "drift-detection",
        "health-report",
        "reconciliation",
    ]


def test_a_failed_run_becomes_a_level_5_gap_window():
    g = gd.gap_from_verdict("FAILED", _ago(24), NOW, ("canary-not-found",))
    assert g is not None and g.level == 5 and g.kind == "vacuous-run"


def test_a_clean_run_produces_no_gap_window():
    assert gd.gap_from_verdict("CLEAN", _ago(24), NOW) is None


def test_a_wrongly_repaired_window_is_level_5():
    g = gd.loop_ran_wrong_gap("codeowners-regeneration", _ago(48), NOW)
    assert g.level == 5 and g.kind == "loop-ran-wrong"


def test_a_naive_timestamp_is_rejected():
    with pytest.raises(gd.GapConfigError):
        gd.detect({"reconciliation": dt.datetime(2026, 6, 1)}, NOW)


def test_payload_carries_the_record_schema_version():
    g = gd.loop_ran_wrong_gap("x", _ago(2), NOW)
    assert g.as_record_payload()["record_schema_version"] == 1
PYEOF
python3 -m pytest -q reconciler/tests/test_gap_detect.py
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
python3 -m ruff check reconciler validators/drift
git add reconciler
git status --porcelain
git commit -m "L3-P3-T07: control-loop gap detection with 51.2 thresholds (53.7, AT-032)"
git push -u origin lane/3/p3-t07
gh pr create --base integration --head lane/3/p3-t07 \
  --title "L3-P3-T07 control-loop gap detection" \
  --body "Lane 3, Phase 3, task T07. Detects reconciliation, health-report and drift-detection gaps against the section 51.2 thresholds, converts a FAILED run into a Level 5 gap window (EC-109), and names the export kind as unarmed rather than silently skipping it. Detection only. Owned paths only."
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
| --- | --- | --- | --- |
| 1 | Sixteen tests pass | `python3 -m pytest -q reconciler/tests/test_gap_detect.py 2>&1 \| grep -oE '^[0-9]+ passed'` | `16 passed` |
| 2 | A 72-hour reconciliation silence escalates to Level 5 | `python3 -c "import datetime as d;from reconciler.phase3 import gap_detect as g;n=d.datetime(2026,6,10,12,tzinfo=d.timezone.utc);print(g.detect({'reconciliation':n-d.timedelta(hours=80)},n)[0][0].level)"` | `5` |
| 3 | AT-032's three self-observed kinds are armed | `python3 -c "from reconciler.phase3 import gap_detect as g;print(g.self_observed_kinds())"` | `['drift-detection', 'health-report', 'reconciliation']` |
| 4 | The unarmed kind is named, not hidden | `python3 -c "from reconciler.phase3 import gap_detect as g;print(g.unarmed_kinds())"` | `['export']` |
| 5 | A FAILED run produces a Level 5 gap window | `python3 -c "import datetime as d;from reconciler.phase3 import gap_detect as g;n=d.datetime(2026,6,10,12,tzinfo=d.timezone.utc);print(g.gap_from_verdict('FAILED',n-d.timedelta(hours=24),n).level)"` | `5` |
| 6 | No foreign path touched | `git -C ~/control-plane diff --name-only origin/integration...HEAD \| grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'` | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd ~/control-plane
python3 -m pytest -q reconciler/tests/test_gap_detect.py 2>&1 | grep -oE '^[0-9]+ passed'
python3 -c "from reconciler.phase3 import gap_detect as g;print(g.self_observed_kinds(), g.unarmed_kinds())"
python3 -c "import datetime as d;from reconciler.phase3 import gap_detect as g;n=d.datetime(2026,6,10,12,tzinfo=d.timezone.utc);print(g.gap_from_verdict('FAILED',n-d.timedelta(hours=24),n).level)"
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'
```

Expected output, exactly four lines:

```
16 passed
['drift-detection', 'health-report', 'reconciliation'] ['export']
5
0
```

### STOP rule

**Stop and open a blocker if any of the following is true.**

* The test count is not `16 passed`.
* You are about to put a number in `gap.yaml` that §51.2 does not state — including an export window. An invented threshold is an invented control. *Decision needed from L0*: `What is the declared organisation-export cadence (SIG-34), and which lane's job records its last success?`
* You are about to make an unevaluated kind report "no gap". §52.2's arming discipline requires it to report as unarmed. Universal STOP preamble rule 5.

---

## L3-P3-T08 — §53.7 — the gap procedure runner

| Field | Value |
| --- | --- |
| **Task id** | `L3-P3-T08` |
| **Size** | L |
| **Depends on** | `L3-P3-T07` |
| **Spec anchors** | §53.7 (the five bullets, verbatim); §46.1 (the recovery list §53.7 mirrors); §53.2 Level 5; §58.4 (postmortem cadence); §26.4 (repair records); **D63**; **AT-102**; **EC-109** |
| **Files created** | `reconciler/phase3/gap_procedure.py`, `reconciler/artifacts/.gitkeep`, `reconciler/tests/test_gap_procedure.py` |

**Purpose.** Run the five-step procedure §53.7 requires when a gap closes, and emit its result as an artifact. All five steps, always, in order:

| # | §53.7 step, verbatim | What this runner produces |
| --- | --- | --- |
| 1 | *"Replay expiries that should have fired during the gap … and revoke or revert anything now overdue"* | A replay **plan**: every assignment `end_date`, temporary access and exception expiry that fell in the window and is now overdue |
| 2 | *"Diff-audit every access grant, merge and production approval made during the gap window against declared state, treating the gap window as unverified rather than presumed clean"* | An audit worklist, one row per grant, merge and production approval in the window, each `unverified` until dispositioned |
| 3 | *"Re-run all standing checks … and confirm clean results, including the seeded canary"* | The re-run verdict from T03. The step passes only on `CLEAN` — canary found, no shortfall |
| 4 | *"Record the gap as an incident at Level 5, with a postmortem on the standard cadence"* | An incident **manifest** at Level 5 for L4's records tooling to write |
| 5 | *"Mark interim records `gap-window` … a gap-window record is not evidence for any gate until re-verification clears the mark"* | A `gap_window_marks` manifest naming every record produced in the window |

**The cross-lane boundary is the whole of steps 4 and 5.** Section 3: `records/**` and `events/**` belong to **L4**; Phase 3 code never writes a record file. This runner emits manifests under `reconciler/artifacts/` — an owned path — and L4's records tooling consumes them. A step that tries to write under `records/` has misread this file.

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
git fetch origin
git switch integration
git pull --ff-only origin integration
git switch -c lane/3/p3-t08
mkdir -p reconciler/artifacts
touch reconciler/artifacts/.gitkeep
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
cat > reconciler/phase3/gap_procedure.py <<'PYEOF'
"""The control-loop gap procedure (spec 53.7).

"When any such gap closes, the escalation role runs the gap procedure,
mirroring the recovery list of Section 46.1."

Five steps, always all five, in order. The runner produces plans and
manifests; it performs no revocation, writes no record and notifies nobody.
Records belong to L4 (PARTITION.md rule 1); revocation is the Level-3 write
path, deferred by 99.6 risk 6.
"""
from __future__ import annotations

import argparse
import dataclasses
import datetime as _dt
import json
import pathlib
from typing import Any, Callable

ARTIFACT_DIR = pathlib.Path("reconciler/artifacts")

STEP_REPLAY_EXPIRIES = "replay-expiries"
STEP_DIFF_AUDIT = "diff-audit"
STEP_RERUN_STANDING_CHECKS = "rerun-standing-checks"
STEP_RECORD_INCIDENT = "record-gap-incident"
STEP_MARK_GAP_WINDOW = "mark-gap-window"

STEPS = (
    STEP_REPLAY_EXPIRIES,
    STEP_DIFF_AUDIT,
    STEP_RERUN_STANDING_CHECKS,
    STEP_RECORD_INCIDENT,
    STEP_MARK_GAP_WINDOW,
)

GAP_WINDOW_MARK = "gap-window"
LEVEL_ESCALATE = 5
RECORD_SCHEMA_VERSION = 1


class GapProcedureError(RuntimeError):
    pass


@dataclasses.dataclass(frozen=True)
class Step:
    step: str
    status: str
    items: tuple[dict[str, Any], ...]
    note: str


@dataclasses.dataclass(frozen=True)
class GapProcedureResult:
    gap_kind: str
    window_start: str
    window_end: str
    steps: tuple[Step, ...]
    complete: bool
    ran_at: str

    def as_manifest(self) -> dict[str, Any]:
        return {
            "record_schema_version": RECORD_SCHEMA_VERSION,
            "manifest_kind": "gap-procedure-result",
            "gap_kind": self.gap_kind,
            "window_start": self.window_start,
            "window_end": self.window_end,
            "complete": self.complete,
            "ran_at": self.ran_at,
            "steps": [
                {
                    "step": s.step,
                    "status": s.status,
                    "item_count": len(s.items),
                    "items": list(s.items),
                    "note": s.note,
                }
                for s in self.steps
            ],
        }


def _in_window(ts: str, start: str, end: str) -> bool:
    return start <= ts <= end


def replay_expiries(expiries: list[dict[str, Any]], start: str, end: str) -> Step:
    """53.7 step 1. A plan, never an execution."""
    overdue = tuple(
        dict(e, action="revoke-or-revert", executed=False)
        for e in expiries
        if _in_window(str(e.get("expires_at", "")), start, end)
    )
    return Step(
        step=STEP_REPLAY_EXPIRIES,
        status="planned",
        items=overdue,
        note="53.7: replay expiries that should have fired during the gap",
    )


def diff_audit(events: list[dict[str, Any]], start: str, end: str) -> Step:
    """53.7 step 2. The window is unverified, never presumed clean."""
    rows = tuple(
        dict(e, disposition="unverified")
        for e in events
        if _in_window(str(e.get("occurred_at", "")), start, end)
        and e.get("kind") in ("access-grant", "merge", "production-approval")
    )
    return Step(
        step=STEP_DIFF_AUDIT,
        status="unverified",
        items=rows,
        note="53.7: treat the gap window as unverified rather than presumed clean",
    )


def rerun_standing_checks(rerun: Callable[[], Any]) -> Step:
    """53.7 step 3. Passes only on CLEAN, which includes the seeded canary."""
    verdict = rerun()
    name = getattr(verdict, "verdict", str(verdict))
    canary = bool(getattr(verdict, "canary_found", False))
    ok = name == "CLEAN" and canary
    return Step(
        step=STEP_RERUN_STANDING_CHECKS,
        status="clean" if ok else "not-clean",
        items=({"verdict": name, "canary_found": canary},),
        note="53.7: confirm clean results, including the seeded canary",
    )


def record_gap_incident(gap: dict[str, Any], now: _dt.datetime) -> Step:
    """53.7 step 4. Emits a manifest; L4 writes the record."""
    item = {
        "manifest_kind": "incident",
        "level": LEVEL_ESCALATE,
        "gap_kind": gap.get("kind"),
        "window_start": gap.get("window_start"),
        "window_end": gap.get("window_end"),
        "postmortem_required": True,
        "postmortem_cadence_ref": "58.4",
        "raised_at": now.astimezone(_dt.timezone.utc).isoformat(),
    }
    return Step(
        step=STEP_RECORD_INCIDENT,
        status="manifest-emitted",
        items=(item,),
        note="53.7: record the gap as an incident at Level 5 (L4 writes it)",
    )


def mark_gap_window(record_paths: list[str]) -> Step:
    """53.7 step 5. Emits the marking manifest; L4 performs the write."""
    items = tuple(
        {"record_path": p, "mark": GAP_WINDOW_MARK, "evidence_for_gates": False}
        for p in sorted(record_paths)
    )
    return Step(
        step=STEP_MARK_GAP_WINDOW,
        status="manifest-emitted",
        items=items,
        note=(
            "53.7: a gap-window record is not evidence for any gate until "
            "re-verification clears the mark"
        ),
    )


def run(
    gap: dict[str, Any],
    inputs: dict[str, Any],
    rerun: Callable[[], Any],
    now: _dt.datetime | None = None,
) -> GapProcedureResult:
    stamp = (now or _dt.datetime.now(_dt.timezone.utc)).astimezone(_dt.timezone.utc)
    start, end = str(gap["window_start"]), str(gap["window_end"])
    steps = (
        replay_expiries(list(inputs.get("expiries") or []), start, end),
        diff_audit(list(inputs.get("events") or []), start, end),
        rerun_standing_checks(rerun),
        record_gap_incident(gap, stamp),
        mark_gap_window(list(inputs.get("window_record_paths") or [])),
    )
    if tuple(s.step for s in steps) != STEPS:
        raise GapProcedureError("the five steps of 53.7 must all run, in order")
    complete = all(s.status != "not-clean" for s in steps)
    return GapProcedureResult(
        gap_kind=str(gap.get("kind", "unknown")),
        window_start=start,
        window_end=end,
        steps=steps,
        complete=complete,
        ran_at=stamp.isoformat(),
    )


def write_manifest(result: GapProcedureResult, out: pathlib.Path) -> pathlib.Path:
    if "records/" in str(out) or "events/" in str(out):
        raise GapProcedureError(
            "refusing to write under records/ or events/: those belong to L4 "
            "(PARTITION.md rule 1)"
        )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result.as_manifest(), indent=2), encoding="utf-8")
    return out


REHEARSAL_GAP = {
    "kind": "vacuous-run",
    "window_start": "2026-06-09T12:00:00+00:00",
    "window_end": "2026-06-10T12:00:00+00:00",
}

REHEARSAL_INPUTS: dict[str, Any] = {
    "expiries": [
        {"id": "ASG-1", "subject": "temp-1", "expires_at": "2026-06-09T18:00:00+00:00"},
        {"id": "ASG-2", "subject": "temp-2", "expires_at": "2026-07-01T00:00:00+00:00"},
    ],
    "events": [
        {"id": "EV-1", "kind": "merge", "occurred_at": "2026-06-09T13:00:00+00:00"},
        {"id": "EV-2", "kind": "access-grant", "occurred_at": "2026-06-09T14:00:00+00:00"},
        {
            "id": "EV-3",
            "kind": "production-approval",
            "occurred_at": "2026-06-09T15:00:00+00:00",
        },
        {"id": "EV-4", "kind": "merge", "occurred_at": "2026-06-11T09:00:00+00:00"},
    ],
    "window_record_paths": [
        "records/deployments/2026-06-09-a.yaml",
        "records/uat/2026-06-09-b.yaml",
    ],
}


class _RehearsalVerdict:
    verdict = "CLEAN"
    canary_found = True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the 53.7 gap procedure.")
    parser.add_argument("--rehearse", action="store_true")
    parser.add_argument("--out", default=str(ARTIFACT_DIR / "gap-procedure.json"))
    args = parser.parse_args(argv)
    if not args.rehearse:
        print("GAP-PROCEDURE requires --rehearse in this phase")
        return 2
    result = run(
        REHEARSAL_GAP,
        REHEARSAL_INPUTS,
        lambda: _RehearsalVerdict(),
        now=_dt.datetime(2026, 6, 10, 12, 0, tzinfo=_dt.timezone.utc),
    )
    write_manifest(result, pathlib.Path(args.out))
    print(f"GAP-PROCEDURE COMPLETE steps={len(result.steps)}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
PYEOF
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
cat > reconciler/tests/test_gap_procedure.py <<'PYEOF'
import datetime as dt
import json
import pathlib

import pytest

from reconciler.phase3 import gap_procedure as gp

NOW = dt.datetime(2026, 6, 10, 12, 0, tzinfo=dt.timezone.utc)


class _Clean:
    verdict = "CLEAN"
    canary_found = True


class _Failed:
    verdict = "FAILED"
    canary_found = False


def _result(rerun=_Clean):
    return gp.run(gp.REHEARSAL_GAP, gp.REHEARSAL_INPUTS, lambda: rerun(), now=NOW)


def test_all_five_steps_run_in_order():
    assert tuple(s.step for s in _result().steps) == gp.STEPS


def test_expiry_replay_selects_only_the_window():
    step = _result().steps[0]
    assert [i["id"] for i in step.items] == ["ASG-1"]


def test_expiry_replay_executes_nothing():
    assert all(i["executed"] is False for i in _result().steps[0].items)


def test_diff_audit_covers_grants_merges_and_production_approvals():
    kinds = sorted({i["kind"] for i in _result().steps[1].items})
    assert kinds == ["access-grant", "merge", "production-approval"]


def test_diff_audit_treats_the_window_as_unverified():
    assert all(i["disposition"] == "unverified" for i in _result().steps[1].items)


def test_diff_audit_excludes_events_outside_the_window():
    assert "EV-4" not in [i["id"] for i in _result().steps[1].items]


def test_standing_checks_pass_only_on_a_clean_canary_run():
    assert _result().steps[2].status == "clean"


def test_a_failed_rerun_leaves_the_procedure_incomplete():
    r = _result(rerun=_Failed)
    assert r.steps[2].status == "not-clean"
    assert r.complete is False


def test_the_incident_manifest_is_level_5():
    assert _result().steps[3].items[0]["level"] == 5


def test_the_incident_manifest_requires_a_postmortem():
    assert _result().steps[3].items[0]["postmortem_required"] is True


def test_window_records_are_marked_gap_window():
    marks = _result().steps[4].items
    assert all(m["mark"] == "gap-window" for m in marks)


def test_a_gap_window_record_is_not_gate_evidence():
    assert all(m["evidence_for_gates"] is False for m in _result().steps[4].items)


def test_the_manifest_carries_the_record_schema_version():
    assert _result().as_manifest()["record_schema_version"] == 1


def test_the_runner_refuses_to_write_under_records():
    with pytest.raises(gp.GapProcedureError):
        gp.write_manifest(_result(), pathlib.Path("records/incidents/x.json"))


def test_the_manifest_writes_to_the_owned_artifact_directory(tmp_path):
    out = gp.write_manifest(_result(), tmp_path / "gap.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["manifest_kind"] == "gap-procedure-result"


def test_the_rehearsal_cli_reports_five_steps(tmp_path, capsys):
    rc = gp.main(["--rehearse", "--out", str(tmp_path / "gap.json")])
    assert rc == 0
    assert capsys.readouterr().out.strip() == "GAP-PROCEDURE COMPLETE steps=5"
PYEOF
python3 -m pytest -q reconciler/tests/test_gap_procedure.py
python3 -m reconciler.phase3.gap_procedure --rehearse --out reconciler/artifacts/gap-procedure-rehearsal.json
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
python3 -m ruff check reconciler validators/drift
rm -f reconciler/artifacts/gap-procedure-rehearsal.json
git add reconciler
git status --porcelain
git commit -m "L3-P3-T08: the 53.7 gap procedure runner - five steps, manifests not records"
git push -u origin lane/3/p3-t08
gh pr create --base integration --head lane/3/p3-t08 \
  --title "L3-P3-T08 the gap procedure runner" \
  --body "Lane 3, Phase 3, task T08. Runs all five steps of section 53.7: replay expiries as a plan, diff-audit the window as unverified, re-run standing checks and pass only on a CLEAN canary run, emit a Level 5 incident manifest, and emit the gap-window marking manifest. Writes manifests under reconciler/artifacts/ and refuses to write under records/ or events/. Owned paths only."
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
| --- | --- | --- | --- |
| 1 | Sixteen tests pass | `python3 -m pytest -q reconciler/tests/test_gap_procedure.py 2>&1 \| grep -oE '^[0-9]+ passed'` | `16 passed` |
| 2 | All five §53.7 steps run | `python3 -m reconciler.phase3.gap_procedure --rehearse --out /tmp/gap.json` | `GAP-PROCEDURE COMPLETE steps=5` |
| 3 | The incident is raised at Level 5 | `python3 -c "import json;print(json.load(open('/tmp/gap.json'))['steps'][3]['items'][0]['level'])"` | `5` |
| 4 | Window records are marked `gap-window` and are not gate evidence | `python3 -c "import json;m=json.load(open('/tmp/gap.json'))['steps'][4]['items'];print(sorted({x['mark'] for x in m}), sorted({x['evidence_for_gates'] for x in m}))"` | `['gap-window'] [False]` |
| 5 | The runner refuses to write a record file | `python3 -m pytest -q reconciler/tests/test_gap_procedure.py -k "refuses_to_write" 2>&1 \| grep -oE '^[0-9]+ passed'` | `1 passed` |
| 6 | No foreign path touched | `git -C ~/control-plane diff --name-only origin/integration...HEAD \| grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'` | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd ~/control-plane
python3 -m pytest -q reconciler/tests/test_gap_procedure.py 2>&1 | grep -oE '^[0-9]+ passed'
python3 -m reconciler.phase3.gap_procedure --rehearse --out /tmp/gap.json
python3 -c "import json;d=json.load(open('/tmp/gap.json'));print(len(d['steps']), d['complete'])"
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'
```

Expected output, exactly four lines:

```
16 passed
GAP-PROCEDURE COMPLETE steps=5
5 True
0
```

### STOP rule

**Stop and open a blocker if any of the following is true.**

* Fewer than five steps run, or the steps run out of order. §53.7 is a list, not a menu.
* The test count is not `16 passed`.
* You are about to make step 1 actually revoke something, or step 4 or 5 write under `records/`. Steps 4 and 5 emit manifests; **L4** writes. A task about to write under `records/` has misread Section 3 and must stop.
* Step 3 would pass on a `DRIFT` or `FAILED` re-run. §53.7 says *"confirm clean results, including the seeded canary"* — `CLEAN` by T03's definition, nothing weaker.

---

## L3-P3-T09 — §53.7 — the "when the loop ran wrong" branch

| Field | Value |
| --- | --- |
| **Task id** | `L3-P3-T09` |
| **Size** | M |
| **Depends on** | `L3-P3-T08` |
| **Spec anchors** | §53.7 (*"When the loop ran wrong … freeze that repair class, enumerate its repairs in the affected window from the repair records of Section 26.4, revert or human-confirm each against the compensating action its change plan was required to name and test (Section 28.1), and mark every record produced in the window `gap-window` until re-verified"*); §53.2 Level 5 (*"a repair class discovered to have written incorrect state"*); §26.4 (repair records); §28.1 (compensating action) |
| **Files created** | `reconciler/phase3/loop_ran_wrong.py`, `reconciler/hooks/repair_freeze_hook.py`, `reconciler/tests/test_loop_ran_wrong.py` |

**Purpose.** §53.7's second branch: *"A loop that completed is not thereby a loop that was right, and without this branch the window's repairs stand as valid gate evidence for as long as nobody asks."* This task freezes the offending repair class, enumerates what it wrote in the window, and refuses to release the freeze until every repair carries a disposition.

**Freeze state is one file per class** — `reconciler/state/freeze/<class-id>.yaml` — because PARTITION.md rule 3 forbids a shared mutable list. The freeze is published into the run context by a discovered hook, so the Level-3 repair path reads it by discovery and no central file is edited.

Two dispositions are permitted, and no third: `reverted`, or `human-confirmed` **naming the compensating action §28.1 required the change plan to state and test**. A `human-confirmed` disposition with no named compensating action is rejected — it is the assertion §53.7 exists to disallow.

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
git fetch origin
git switch integration
git pull --ff-only origin integration
git switch -c lane/3/p3-t09
mkdir -p reconciler/state/freeze reconciler/hooks
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
cat > reconciler/phase3/loop_ran_wrong.py <<'PYEOF'
"""The "when the loop ran wrong" branch of the gap procedure (spec 53.7).

"A repair class discovered to have written incorrect state is a Level 5
escalation in its own right (53.2), and the same window discipline applies:
freeze that repair class, enumerate its repairs in the affected window from
the repair records of Section 26.4, revert or human-confirm each against the
compensating action its change plan was required to name and test (Section
28.1), and mark every record produced in the window gap-window until
re-verified."

Freeze state is one file per class: PARTITION.md rule 3, no shared mutable
file. Freezing is additive; releasing requires a complete disposition set.
"""
from __future__ import annotations

import dataclasses
import datetime as _dt
import pathlib
from typing import Any

import yaml

FREEZE_DIR = pathlib.Path("reconciler/state/freeze")

DISPOSITION_REVERTED = "reverted"
DISPOSITION_HUMAN_CONFIRMED = "human-confirmed"
DISPOSITIONS = (DISPOSITION_REVERTED, DISPOSITION_HUMAN_CONFIRMED)

LEVEL_ESCALATE = 5
GAP_WINDOW_MARK = "gap-window"
RECORD_SCHEMA_VERSION = 1


class FreezeError(RuntimeError):
    pass


@dataclasses.dataclass(frozen=True)
class Freeze:
    class_id: str
    reason: str
    window_start: str
    window_end: str
    frozen_at: str
    level: int = LEVEL_ESCALATE

    def as_payload(self) -> dict[str, Any]:
        return {
            "record_schema_version": RECORD_SCHEMA_VERSION,
            "class_id": self.class_id,
            "reason": self.reason,
            "window_start": self.window_start,
            "window_end": self.window_end,
            "frozen_at": self.frozen_at,
            "level": self.level,
        }


def freeze_path(class_id: str, directory: pathlib.Path | None = None) -> pathlib.Path:
    return (directory or FREEZE_DIR) / f"{class_id}.yaml"


def freeze(
    class_id: str,
    reason: str,
    window_start: str,
    window_end: str,
    now: _dt.datetime,
    directory: pathlib.Path | None = None,
) -> Freeze:
    d = directory or FREEZE_DIR
    d.mkdir(parents=True, exist_ok=True)
    f = Freeze(
        class_id=class_id,
        reason=reason,
        window_start=window_start,
        window_end=window_end,
        frozen_at=now.astimezone(_dt.timezone.utc).isoformat(),
    )
    freeze_path(class_id, d).write_text(
        yaml.safe_dump(f.as_payload(), sort_keys=True), encoding="utf-8"
    )
    return f


def is_frozen(class_id: str, directory: pathlib.Path | None = None) -> bool:
    return freeze_path(class_id, directory).is_file()


def frozen_classes(directory: pathlib.Path | None = None) -> list[str]:
    d = directory or FREEZE_DIR
    if not d.is_dir():
        return []
    return sorted(p.stem for p in d.glob("*.yaml"))


def enumerate_repairs(
    repair_records: list[dict[str, Any]],
    class_id: str,
    window_start: str,
    window_end: str,
) -> list[dict[str, Any]]:
    """Section 26.4 repair records, narrowed to the class and the window."""
    return sorted(
        (
            r
            for r in repair_records
            if r.get("repair_class") == class_id
            and window_start <= str(r.get("repaired_at", "")) <= window_end
        ),
        key=lambda r: str(r.get("repair_id", "")),
    )


def validate_disposition(disposition: dict[str, Any]) -> None:
    kind = disposition.get("disposition")
    if kind not in DISPOSITIONS:
        raise FreezeError(
            f"unknown disposition {kind!r}: 53.7 permits only {list(DISPOSITIONS)}"
        )
    if kind == DISPOSITION_HUMAN_CONFIRMED and not disposition.get(
        "compensating_action"
    ):
        raise FreezeError(
            "a human-confirmed repair must name the compensating action its "
            "change plan was required to name and test (28.1)"
        )


def outstanding_repairs(
    repairs: list[dict[str, Any]], dispositions: list[dict[str, Any]]
) -> list[str]:
    """Repair ids with no valid disposition. Fail closed on an invalid one."""
    for d in dispositions:
        validate_disposition(d)
    done = {str(d.get("repair_id")) for d in dispositions}
    return sorted(
        str(r.get("repair_id")) for r in repairs if str(r.get("repair_id")) not in done
    )


def window_marks(record_paths: list[str]) -> list[dict[str, Any]]:
    return [
        {"record_path": p, "mark": GAP_WINDOW_MARK, "evidence_for_gates": False}
        for p in sorted(record_paths)
    ]


def unfreeze_allowed(
    repairs: list[dict[str, Any]],
    dispositions: list[dict[str, Any]],
    window_records_reverified: bool,
) -> bool:
    """Release the freeze only when nothing is outstanding and the window is
    re-verified. Section 53.7: a gap-window record "is not evidence for any
    gate until re-verification clears the mark".
    """
    if not window_records_reverified:
        return False
    return outstanding_repairs(repairs, dispositions) == []
PYEOF
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
cat > reconciler/hooks/repair_freeze_hook.py <<'PYEOF'
"""Publish the frozen repair classes into the run context (53.7).

Discovered by glob from reconciler/hooks/*.py. Nothing is appended to a
central list (PARTITION.md rule 3).

The hook is fail-closed: if the run context declares a live repair for a
frozen class, the run stops rather than proceeding. 53.7 freezes the class,
and a freeze that a later step may ignore is not a freeze.
"""
from __future__ import annotations

from typing import Any

from reconciler.phase3 import loop_ran_wrong
from reconciler.phase3.rule_api import RunHook


class FrozenRepairClassError(RuntimeError):
    pass


def _run(context: dict[str, Any]) -> dict[str, Any]:
    frozen = loop_ran_wrong.frozen_classes(context.get("freeze_dir"))
    live = [str(c) for c in (context.get("live_repair_classes") or [])]
    collision = sorted(set(frozen) & set(live))
    if collision:
        raise FrozenRepairClassError(
            f"repair classes frozen under 53.7 are declared live: {collision}"
        )
    return {"frozen_repair_classes": frozen}


HOOK = RunHook(hook_id="repair-freeze", phase="pre", run=_run)
PYEOF
cat > reconciler/tests/test_loop_ran_wrong.py <<'PYEOF'
import datetime as dt

import pytest

from reconciler.hooks import repair_freeze_hook as hook
from reconciler.phase3 import loop_ran_wrong as lrw

NOW = dt.datetime(2026, 6, 10, 12, 0, tzinfo=dt.timezone.utc)
START, END = "2026-06-01T00:00:00+00:00", "2026-06-09T00:00:00+00:00"

REPAIRS = [
    {"repair_id": "R-1", "repair_class": "codeowners-regeneration", "repaired_at": "2026-06-02T10:00:00+00:00"},
    {"repair_id": "R-2", "repair_class": "codeowners-regeneration", "repaired_at": "2026-06-03T10:00:00+00:00"},
    {"repair_id": "R-3", "repair_class": "team-membership-sync", "repaired_at": "2026-06-03T10:00:00+00:00"},
    {"repair_id": "R-4", "repair_class": "codeowners-regeneration", "repaired_at": "2026-06-20T10:00:00+00:00"},
]


def test_freezing_writes_one_file_per_class(tmp_path):
    lrw.freeze("codeowners-regeneration", "wrote incorrect state", START, END, NOW, tmp_path)
    assert (tmp_path / "codeowners-regeneration.yaml").is_file()


def test_a_freeze_is_level_5(tmp_path):
    f = lrw.freeze("codeowners-regeneration", "x", START, END, NOW, tmp_path)
    assert f.level == 5


def test_is_frozen_reads_the_directory(tmp_path):
    assert lrw.is_frozen("codeowners-regeneration", tmp_path) is False
    lrw.freeze("codeowners-regeneration", "x", START, END, NOW, tmp_path)
    assert lrw.is_frozen("codeowners-regeneration", tmp_path) is True


def test_frozen_classes_lists_every_freeze_file(tmp_path):
    lrw.freeze("a", "x", START, END, NOW, tmp_path)
    lrw.freeze("b", "x", START, END, NOW, tmp_path)
    assert lrw.frozen_classes(tmp_path) == ["a", "b"]


def test_enumeration_is_narrowed_to_the_class_and_the_window():
    got = lrw.enumerate_repairs(REPAIRS, "codeowners-regeneration", START, END)
    assert [r["repair_id"] for r in got] == ["R-1", "R-2"]


def test_a_repair_with_no_disposition_is_outstanding():
    repairs = lrw.enumerate_repairs(REPAIRS, "codeowners-regeneration", START, END)
    assert lrw.outstanding_repairs(repairs, []) == ["R-1", "R-2"]


def test_a_reverted_repair_is_dispositioned():
    repairs = lrw.enumerate_repairs(REPAIRS, "codeowners-regeneration", START, END)
    d = [{"repair_id": "R-1", "disposition": "reverted"}]
    assert lrw.outstanding_repairs(repairs, d) == ["R-2"]


def test_human_confirmation_without_a_compensating_action_is_rejected():
    with pytest.raises(lrw.FreezeError):
        lrw.validate_disposition({"repair_id": "R-1", "disposition": "human-confirmed"})


def test_human_confirmation_with_a_compensating_action_is_accepted():
    lrw.validate_disposition(
        {
            "repair_id": "R-1",
            "disposition": "human-confirmed",
            "compensating_action": "flag flip CP-14, tested 2026-05-02",
        }
    )


def test_an_unknown_disposition_is_rejected():
    with pytest.raises(lrw.FreezeError):
        lrw.validate_disposition({"repair_id": "R-1", "disposition": "looks-fine"})


def test_unfreeze_is_refused_while_a_repair_is_outstanding():
    repairs = lrw.enumerate_repairs(REPAIRS, "codeowners-regeneration", START, END)
    assert lrw.unfreeze_allowed(repairs, [], True) is False


def test_unfreeze_is_refused_until_the_window_is_reverified():
    repairs = lrw.enumerate_repairs(REPAIRS, "codeowners-regeneration", START, END)
    d = [
        {"repair_id": "R-1", "disposition": "reverted"},
        {"repair_id": "R-2", "disposition": "reverted"},
    ]
    assert lrw.unfreeze_allowed(repairs, d, False) is False
    assert lrw.unfreeze_allowed(repairs, d, True) is True


def test_window_records_are_marked_and_are_not_gate_evidence():
    marks = lrw.window_marks(["records/deployments/a.yaml"])
    assert marks[0]["mark"] == "gap-window"
    assert marks[0]["evidence_for_gates"] is False


def test_the_hook_publishes_the_frozen_set(tmp_path):
    lrw.freeze("codeowners-regeneration", "x", START, END, NOW, tmp_path)
    out = hook.HOOK.run({"freeze_dir": tmp_path, "live_repair_classes": []})
    assert out["frozen_repair_classes"] == ["codeowners-regeneration"]


def test_the_hook_fails_closed_when_a_frozen_class_is_live(tmp_path):
    lrw.freeze("codeowners-regeneration", "x", START, END, NOW, tmp_path)
    with pytest.raises(hook.FrozenRepairClassError):
        hook.HOOK.run(
            {"freeze_dir": tmp_path, "live_repair_classes": ["codeowners-regeneration"]}
        )


def test_the_hook_is_a_pre_phase_hook():
    assert hook.HOOK.phase == "pre"
PYEOF
python3 -m pytest -q reconciler/tests/test_loop_ran_wrong.py
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
python3 -m ruff check reconciler validators/drift
git add reconciler
git status --porcelain
git commit -m "L3-P3-T09: the 53.7 when-the-loop-ran-wrong branch - freeze, enumerate, disposition"
git push -u origin lane/3/p3-t09
gh pr create --base integration --head lane/3/p3-t09 \
  --title "L3-P3-T09 when the loop ran wrong" \
  --body "Lane 3, Phase 3, task T09. Freezes a repair class discovered to have written incorrect state (Level 5), enumerates its repairs in the window from the section 26.4 repair records, requires each to be reverted or human-confirmed against a named compensating action (28.1), and refuses to release the freeze until the window is re-verified. Freeze state is one file per class. Owned paths only."
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
| --- | --- | --- | --- |
| 1 | Sixteen tests pass | `python3 -m pytest -q reconciler/tests/test_loop_ran_wrong.py 2>&1 \| grep -oE '^[0-9]+ passed'` | `16 passed` |
| 2 | A freeze is Level 5 | `python3 -c "import datetime as d,tempfile,pathlib;from reconciler.phase3 import loop_ran_wrong as l;print(l.freeze('c','x','a','b',d.datetime(2026,6,1,tzinfo=d.timezone.utc),pathlib.Path(tempfile.mkdtemp())).level)"` | `5` |
| 3 | Human confirmation without a compensating action is refused | `python3 -m pytest -q reconciler/tests/test_loop_ran_wrong.py -k "without_a_compensating_action" 2>&1 \| grep -oE '^[0-9]+ passed'` | `1 passed` |
| 4 | The freeze hook is discovered by glob | `python3 -c "from reconciler.phase3 import discovery as d;print('repair-freeze' in [h.hook_id for h in d.discover_hooks()])"` | `True` |
| 5 | Freeze state is one file per class | `python3 -c "from reconciler.phase3 import loop_ran_wrong as l;print(l.freeze_path('codeowners-regeneration'))"` | `reconciler/state/freeze/codeowners-regeneration.yaml` |
| 6 | No foreign path touched | `git -C ~/control-plane diff --name-only origin/integration...HEAD \| grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'` | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd ~/control-plane
python3 -m pytest -q reconciler/tests/test_loop_ran_wrong.py 2>&1 | grep -oE '^[0-9]+ passed'
python3 -c "from reconciler.phase3 import discovery as d;print(sorted(h.hook_id for h in d.discover_hooks()))"
python3 -c "from reconciler.phase3 import loop_ran_wrong as l;print(l.DISPOSITIONS)"
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'
```

Expected output, exactly four lines:

```
16 passed
['repair-freeze']
('reverted', 'human-confirmed')
0
```

### STOP rule

**Stop and open a blocker if any of the following is true.**

* The test count is not `16 passed`.
* You are about to add a third disposition — "accepted", "no action needed", "reviewed". §53.7 names two, and each of them costs somebody something. A third is how a wrong window becomes gate evidence again.
* You are about to let `unfreeze_allowed` return `True` with outstanding repairs or an unverified window.
* The freeze hook would be made non-fatal so that a run completes. A freeze a later step may ignore is not a freeze — universal STOP preamble rule 5.

---

## L3-P3-T10 — D107 — anchor the records head SHA and commit count each run

| Field | Value |
| --- | --- |
| **Task id** | `L3-P3-T10` |
| **Size** | M |
| **Depends on** | `L3-P3-T02` |
| **Spec anchors** | **D107** (*"the reconciler anchors the records head SHA into the protected control-plane repository each run"*; *"The object-locked export is the slow anchor; the per-run SHA is the fast one"*); §40.1 (records repository *"No protection rules"*; control plane *"No bypass actor exists"*); §63.1 (immutable history); §97.1 (UTC with offset); §101 #47; **DR-3.1** |
| **Files created** | `reconciler/config/anchoring.yaml`, `reconciler/phase3/anchor.py`, `reconciler/hooks/anchor_hook.py`, `reconciler/tests/test_anchor.py` |

**Purpose.** §63.1's *"Once per reconciliation run, the reconciler records the records repository's default-branch head SHA and commit count into the **control-plane repository**, which is fully protected."* This task computes that anchor and produces its payload, once per run, from a read-only git query against the records clone.

**What this task does not create.** The anchor's destination is `derived/`. STOP lifted: `derived/**` is now owned by L0 (REG-026). See L0-00-03 generator additions. No Phase 3 task creates a file under `derived/` in the repository; the module writes the anchor at run time to the path configuration names and refuses to write anywhere else; the tests write to a temporary directory.

**On `reconciler/config/anchoring.yaml`.** T06 creates the same file with the same bytes, for the reason DR-3.1 gives. The heredoc below is byte-identical to T06's; an add/add of identical content merges cleanly. Do not reformat it. If the file already exists after your rebase, skip the heredoc and check the SHA-256.

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
git fetch origin
git switch integration
git pull --ff-only origin integration
git switch -c lane/3/p3-t10
mkdir -p reconciler/config reconciler/hooks
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
if [ ! -f reconciler/config/anchoring.yaml ]; then
cat > reconciler/config/anchoring.yaml <<'YAMLEOF'
# reconciler/config/anchoring.yaml
#
# DR-3.1 ratified: bytes unchanged. T06 and T10 both assert sha256 `2dffc3c7…`
# — identical content makes the two branches merge correctly.
#
# D107: "the reconciler anchors the records head SHA into the protected
# control-plane repository each run, so a head that does not descend from the
# last anchor is proof of rewriting at Level 5."
# D93:  "The reconciler's own write scope is narrowed to generated derived/**
# files the registries reference, so a machine write to a registry becomes
# detectable Blocking drift rather than an in-scope write."
config_version: 1
spec_refs: ["D107", "D93", "53.2", "63.1", "97.1", "101 #47"]

# Destination of the per-run anchor inside the control-plane repository.
# Written at run time by the reconciler credential. NOT created in the
# repository by any Phase 3 task: derived/** is owned by no lane (DR-3.1).
anchor_path: derived/anchors/records-head.yaml

# The complete set of path globs the reconciler credential may write in the
# control-plane repository. Read as data by T06. Never hard-coded.
write_scope_allowlist:
  - derived/**

# The records clone the anchor is computed from. Read-only in this phase.
records_clone_path: ~/control-plane-records
records_ref: HEAD
YAMLEOF
fi
sha256sum reconciler/config/anchoring.yaml
```

The checksum printed must be exactly:

```
2dffc3c76487e863ea190cbca4bd683a402a947e0d1e2204b0f0f9b71eb215ee  reconciler/config/anchoring.yaml
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
cat > reconciler/phase3/anchor.py <<'PYEOF'
"""Records tamper-evidence anchoring (D107, spec 63.1, invariant 47).

D107: "the reconciler anchors the records head SHA into the protected
control-plane repository each run, so a head that does not descend from the
last anchor is proof of rewriting at Level 5. The object-locked export is the
slow anchor; the per-run SHA is the fast one."

Section 40.1: the records repository carries no protection rules, so its
immutability rests on this anchor plus the no-bypass ruleset. The control-plane
repository is fully protected, which is why the anchor lives there.

Every git command issued here is a read: rev-parse and rev-list. This module
never fetches, never pushes, never checks out.
"""
from __future__ import annotations

import argparse
import dataclasses
import datetime as _dt
import os
import pathlib
import subprocess
from typing import Any

import yaml

CONFIG = pathlib.Path("reconciler/config/anchoring.yaml")

RECORD_SCHEMA_VERSION = 1

READ_ONLY_GIT = ("rev-parse", "rev-list", "cat-file", "merge-base")


class AnchorError(RuntimeError):
    pass


def load_config(path: pathlib.Path | None = None) -> dict[str, Any]:
    p = path or CONFIG
    if not p.is_file():
        raise AnchorError(f"anchoring configuration absent: {p}")
    cfg = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    for key in ("anchor_path", "records_clone_path", "records_ref"):
        if not cfg.get(key):
            raise AnchorError(f"{p} missing key: {key}")
    return cfg


def _git(clone: pathlib.Path, *args: str) -> str:
    if args and args[0] not in READ_ONLY_GIT:
        raise AnchorError(f"refusing a non-read git command: {args[0]}")
    proc = subprocess.run(
        ["git", "-C", str(clone), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise AnchorError(
            f"git {' '.join(args)} failed in {clone}: {proc.stderr.strip()}"
        )
    return proc.stdout.strip()


@dataclasses.dataclass(frozen=True)
class Anchor:
    run_id: str
    records_head_sha: str
    records_commit_count: int
    previous_anchor_sha: str | None
    anchored_at: str

    def as_payload(self) -> dict[str, Any]:
        return {
            "record_schema_version": RECORD_SCHEMA_VERSION,
            "anchor_kind": "records-head",
            "run_id": self.run_id,
            "records_head_sha": self.records_head_sha,
            "records_commit_count": self.records_commit_count,
            "previous_anchor_sha": self.previous_anchor_sha,
            "anchored_at": self.anchored_at,
            "spec_refs": ["D107", "63.1", "101 #47"],
        }


def records_head(clone: pathlib.Path, ref: str = "HEAD") -> tuple[str, int]:
    """The head SHA and the commit count. Two reads, no writes."""
    sha = _git(clone, "rev-parse", ref)
    count = int(_git(clone, "rev-list", "--count", ref))
    if len(sha) != 40:
        raise AnchorError(f"unexpected head sha for {ref} in {clone}: {sha!r}")
    return sha, count


def previous_anchor_sha(anchor_file: pathlib.Path) -> str | None:
    """The last anchored SHA, or None on the first ever run."""
    if not anchor_file.is_file():
        return None
    data = yaml.safe_load(anchor_file.read_text(encoding="utf-8")) or {}
    sha = data.get("records_head_sha")
    return str(sha) if sha else None


def build(
    run_id: str,
    clone: pathlib.Path,
    now: _dt.datetime,
    anchor_file: pathlib.Path,
    ref: str = "HEAD",
) -> Anchor:
    sha, count = records_head(clone, ref)
    return Anchor(
        run_id=run_id,
        records_head_sha=sha,
        records_commit_count=count,
        previous_anchor_sha=previous_anchor_sha(anchor_file),
        anchored_at=now.astimezone(_dt.timezone.utc).isoformat(),
    )


def write(anchor: Anchor, destination: pathlib.Path, expected: pathlib.Path) -> pathlib.Path:
    """Write the anchor, and only to the configured destination.

    D93 narrows the reconciler's write scope; this refusal is the same
    property enforced locally, so a mis-pointed anchor cannot become a write
    somewhere else.
    """
    if pathlib.Path(destination) != pathlib.Path(expected):
        raise AnchorError(
            f"refusing to write the anchor to {destination}: the configured "
            f"destination is {expected}"
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        yaml.safe_dump(anchor.as_payload(), sort_keys=True), encoding="utf-8"
    )
    return destination


def configured_clone(cfg: dict[str, Any]) -> pathlib.Path:
    return pathlib.Path(os.path.expanduser(str(cfg["records_clone_path"])))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compute the D107 records anchor.")
    parser.add_argument("--run-id", default="manual")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    cfg = load_config()
    clone = configured_clone(cfg)
    anchor_file = pathlib.Path(str(cfg["anchor_path"]))
    a = build(
        args.run_id,
        clone,
        _dt.datetime.now(_dt.timezone.utc),
        anchor_file,
        str(cfg["records_ref"]),
    )
    print(f"ANCHOR {a.records_head_sha} count={a.records_commit_count}")
    if not args.dry_run:
        write(a, anchor_file, anchor_file)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
PYEOF
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
cat > reconciler/hooks/anchor_hook.py <<'PYEOF'
"""Anchor the records head once per run (D107).

Discovered by glob from reconciler/hooks/*.py. Runs in the post phase: the
anchor records what the records repository looked like at this run, and is
compared against the previous anchor by the T11 drift rule.

The hook computes and returns the payload. It writes only when the run
explicitly enables the write and names the configured destination - the
destination lives under a path this lane does not own (DR-3.1).
"""
from __future__ import annotations

import datetime as _dt
import pathlib
from typing import Any

from reconciler.phase3 import anchor
from reconciler.phase3.rule_api import RunHook


def _run(context: dict[str, Any]) -> dict[str, Any]:
    cfg = anchor.load_config(context.get("anchoring_config"))
    clone = pathlib.Path(context.get("records_clone") or anchor.configured_clone(cfg))
    anchor_file = pathlib.Path(context.get("anchor_file") or str(cfg["anchor_path"]))
    now = context.get("now") or _dt.datetime.now(_dt.timezone.utc)
    a = anchor.build(
        str(context.get("run_id", "unknown")),
        clone,
        now,
        anchor_file,
        str(cfg["records_ref"]),
    )
    if context.get("anchor_write_enabled"):
        anchor.write(a, anchor_file, anchor_file)
    return {"anchor": a.as_payload(), "anchor_written": bool(context.get("anchor_write_enabled"))}


HOOK = RunHook(hook_id="records-anchor", phase="post", run=_run)
PYEOF
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
cat > reconciler/tests/test_anchor.py <<'PYEOF'
import datetime as dt
import pathlib
import subprocess

import pytest
import yaml

from reconciler.hooks import anchor_hook
from reconciler.phase3 import anchor

NOW = dt.datetime(2026, 6, 10, 12, 0, tzinfo=dt.timezone.utc)


def _repo(tmp_path: pathlib.Path, commits: int = 3) -> pathlib.Path:
    repo = tmp_path / "records"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True, capture_output=True)
    for i in range(commits):
        subprocess.run(
            [
                "git", "-C", str(repo),
                "-c", "user.email=t@example.invalid",
                "-c", "user.name=t",
                "commit", "-q", "--allow-empty", "-m", f"c{i}",
            ],
            check=True,
            capture_output=True,
        )
    return repo


def test_config_loads_the_configured_anchor_path():
    assert anchor.load_config()["anchor_path"] == "derived/anchors/records-head.yaml"


def test_absent_config_fails_closed(tmp_path):
    with pytest.raises(anchor.AnchorError):
        anchor.load_config(tmp_path / "absent.yaml")


def test_head_sha_is_forty_hex_characters(tmp_path):
    sha, _ = anchor.records_head(_repo(tmp_path))
    assert len(sha) == 40


def test_commit_count_is_the_number_of_commits(tmp_path):
    _, count = anchor.records_head(_repo(tmp_path, commits=5))
    assert count == 5


def test_a_non_read_git_command_is_refused(tmp_path):
    with pytest.raises(anchor.AnchorError):
        anchor._git(_repo(tmp_path), "push", "origin", "main")


def test_the_first_anchor_has_no_predecessor(tmp_path):
    a = anchor.build("run-1", _repo(tmp_path), NOW, tmp_path / "anchor.yaml")
    assert a.previous_anchor_sha is None


def test_the_next_anchor_names_the_previous_sha(tmp_path):
    repo = _repo(tmp_path)
    dest = tmp_path / "anchor.yaml"
    first = anchor.build("run-1", repo, NOW, dest)
    anchor.write(first, dest, dest)
    second = anchor.build("run-2", repo, NOW, dest)
    assert second.previous_anchor_sha == first.records_head_sha


def test_the_payload_carries_the_head_sha_and_the_commit_count(tmp_path):
    a = anchor.build("run-1", _repo(tmp_path, commits=4), NOW, tmp_path / "a.yaml")
    p = a.as_payload()
    assert p["records_commit_count"] == 4 and len(p["records_head_sha"]) == 40


def test_the_payload_timestamp_is_utc_with_offset(tmp_path):
    a = anchor.build("run-1", _repo(tmp_path), NOW, tmp_path / "a.yaml")
    assert a.as_payload()["anchored_at"].endswith("+00:00")


def test_the_payload_carries_the_record_schema_version(tmp_path):
    a = anchor.build("run-1", _repo(tmp_path), NOW, tmp_path / "a.yaml")
    assert a.as_payload()["record_schema_version"] == 1


def test_the_anchor_refuses_a_destination_other_than_the_configured_one(tmp_path):
    a = anchor.build("run-1", _repo(tmp_path), NOW, tmp_path / "a.yaml")
    with pytest.raises(anchor.AnchorError):
        anchor.write(a, tmp_path / "elsewhere.yaml", tmp_path / "a.yaml")


def test_the_written_anchor_round_trips(tmp_path):
    dest = tmp_path / "a.yaml"
    a = anchor.build("run-1", _repo(tmp_path), NOW, dest)
    anchor.write(a, dest, dest)
    assert yaml.safe_load(dest.read_text(encoding="utf-8"))["run_id"] == "run-1"


def test_the_hook_is_discovered_and_is_a_post_phase_hook():
    assert anchor_hook.HOOK.hook_id == "records-anchor"
    assert anchor_hook.HOOK.phase == "post"


def test_the_hook_does_not_write_unless_the_run_enables_it(tmp_path):
    repo = _repo(tmp_path)
    dest = tmp_path / "a.yaml"
    out = anchor_hook.HOOK.run(
        {"records_clone": repo, "anchor_file": dest, "now": NOW, "run_id": "r"}
    )
    assert out["anchor_written"] is False
    assert dest.exists() is False


def test_the_hook_writes_when_the_run_enables_it(tmp_path):
    repo = _repo(tmp_path)
    dest = tmp_path / "a.yaml"
    out = anchor_hook.HOOK.run(
        {
            "records_clone": repo,
            "anchor_file": dest,
            "now": NOW,
            "run_id": "r",
            "anchor_write_enabled": True,
        }
    )
    assert out["anchor_written"] is True and dest.is_file()
PYEOF
python3 -m pytest -q reconciler/tests/test_anchor.py
python3 -m reconciler.phase3.anchor --dry-run --run-id smoke
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
python3 -m ruff check reconciler validators/drift
git add reconciler
git status --porcelain
git commit -m "L3-P3-T10: D107 anchor the records head SHA and commit count each run"
git push -u origin lane/3/p3-t10
gh pr create --base integration --head lane/3/p3-t10 \
  --title "L3-P3-T10 records head anchoring" \
  --body "Lane 3, Phase 3, task T10. Computes the D107 per-run anchor - records head SHA and commit count - from read-only git queries, names the previous anchor, and refuses any destination but the configured one. Creates no file under derived/: that path is owned by no lane (DR-3.1). Owned paths only."
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
| --- | --- | --- | --- |
| 1 | The DR-3.1 configuration is byte-identical to T06's copy | `sha256sum reconciler/config/anchoring.yaml \| cut -d' ' -f1` | `2dffc3c76487e863ea190cbca4bd683a402a947e0d1e2204b0f0f9b71eb215ee` |
| 2 | Fifteen tests pass | `python3 -m pytest -q reconciler/tests/test_anchor.py 2>&1 \| grep -oE '^[0-9]+ passed'` | `15 passed` |
| 3 | The anchor computes against the real records clone | `python3 -m reconciler.phase3.anchor --dry-run --run-id smoke \| cut -d' ' -f1` | `ANCHOR` |
| 4 | Only read git commands are permitted | `python3 -c "from reconciler.phase3 import anchor as a;print(a.READ_ONLY_GIT)"` | `('rev-parse', 'rev-list', 'cat-file', 'merge-base')` |
| 5 | No file was created under `derived/` | `git -C ~/control-plane status --porcelain \| grep -c "derived/"` | `0` |
| 6 | No foreign path touched | `git -C ~/control-plane diff --name-only origin/integration...HEAD \| grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'` | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd ~/control-plane
sha256sum reconciler/config/anchoring.yaml | cut -d' ' -f1
python3 -m pytest -q reconciler/tests/test_anchor.py 2>&1 | grep -oE '^[0-9]+ passed'
python3 -m reconciler.phase3.anchor --dry-run --run-id smoke | cut -d' ' -f1
git status --porcelain | grep -c "derived/" || true
```

Expected output, exactly four lines:

```
2dffc3c76487e863ea190cbca4bd683a402a947e0d1e2204b0f0f9b71eb215ee
15 passed
ANCHOR
0
```

### STOP rule

**Stop and open a blocker if any of the following is true.**

* The checksum is not `2dffc3c7…15ee`. T06 and T10 must write identical bytes or the branches conflict.
* `~/control-plane-records` is not a git clone (T00 acceptance criterion 5 already proved it; if it has since gone, stop).
* ~~A file appears under `derived/` in `git status`. That path is owned by no lane.~~ STOP lifted: `derived/**` is now owned by L0 (REG-026). See L0-00-03 generator additions.
* You are about to add a git command that writes — `push`, `commit`, `fetch`, `checkout`. This module reads. The anchor is written by the reconciler credential at run time, to one configured path.
* The test count is not `15 passed`.

---

## L3-P3-T11 — D107 — the non-descendant check at Blocking, Level 5

| Field | Value |
| --- | --- |
| **Task id** | `L3-P3-T11` |
| **Size** | M |
| **Depends on** | `L3-P3-T10` |
| **Spec anchors** | **D107** (*"a head that does not descend from the last anchored SHA is proof of rewriting rather than evidence of it. A non-descendant head is **Blocking drift, Level 5**"*; *"a commit on the default branch that is unsigned, or signed by any other identity, is Blocking drift"*); §53.2 Level 4 and Level 5; §63.1; §33.2 (authorship discipline); §101 #47; §53.1 first-observation precedent |
| **Files created** | `reconciler/phase3/git_ancestry.py`, `validators/drift/rules/records_anchor_rule.py`, `validators/drift/rules/records_signature_rule.py`, `validators/drift/tests/test_records_integrity_rules.py` |

**Purpose.** Turn the anchor into a control. Git history is a hash chain, so *"any rewrite of a past record changes every subsequent SHA"* — a records head that is not a descendant of the last anchored SHA is proof, not suspicion. This task adds the two discovered rules D107 names:

| Rule | Fires when | Class | Level | D107 bullet |
| --- | --- | --- | --- | --- |
| `D107-RECORDS-NON-DESCENDANT` | The current records head does not descend from the last anchored SHA | Blocking | **5** | *"History is anchored where it cannot be rewritten"* |
| `D107-RECORDS-COMMIT-SIGNATURE` | A default-branch commit is unsigned, or signed by an identity other than the declared records-writer | Blocking | 4 | *"Commits are signed by the writing identity"* |

The signature rule is here because the master entry-and-exit criteria route it here: `L4P1-E2` — *"An unsigned or foreign-signed commit on the records repository is detectable as Blocking drift … Detection lands at L3-P3."* L4 owns the store; L3 owns the detector.

**First observation.** On the very first run there is no previous anchor. §53.1's own precedent for this case is CMP-13's: *"A tag with no recorded SHA is recorded on first sight and reported Amber once (first-observation), never silently."* The anchor rule follows it exactly — Amber once, never silence.

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
git fetch origin
git switch integration
git pull --ff-only origin integration
git switch -c lane/3/p3-t11
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
cat > reconciler/phase3/git_ancestry.py <<'PYEOF'
"""Ancestry queries against the records clone (D107).

"Because git history is a hash chain, any rewrite of a past record changes
every subsequent SHA, so a head that does not descend from the last anchored
SHA is proof of rewriting rather than evidence of it."

Fail closed: an object git cannot resolve is NOT treated as an ancestor. A
missing ancestor is exactly what a rewrite looks like.
"""
from __future__ import annotations

import pathlib
import subprocess


class AncestryError(RuntimeError):
    pass


def _git(clone: pathlib.Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(clone), *args], capture_output=True, text=True, check=False
    )


def object_exists(clone: pathlib.Path, sha: str) -> bool:
    return _git(clone, "cat-file", "-e", f"{sha}^{{commit}}").returncode == 0


def is_ancestor(clone: pathlib.Path, ancestor_sha: str, descendant_sha: str) -> bool:
    """True only when git proves ancestry. Anything else is False."""
    if not ancestor_sha or not descendant_sha:
        return False
    if not object_exists(clone, ancestor_sha) or not object_exists(
        clone, descendant_sha
    ):
        return False
    return (
        _git(clone, "merge-base", "--is-ancestor", ancestor_sha, descendant_sha).returncode
        == 0
    )
PYEOF
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
cat > validators/drift/rules/records_anchor_rule.py <<'PYEOF'
"""A non-descendant records head is Blocking drift at Level 5 (D107).

D107: "the reconciler anchors the records head SHA into the protected
control-plane repository each run, so a head that does not descend from the
last anchor is proof of rewriting at Level 5."

Context keys read:
    records_clone     path to the records clone
    records_head_sha  the head observed this run
    last_anchor_sha   the SHA of the previous anchor, or None on first sight
"""
from __future__ import annotations

import datetime as _dt
import pathlib
from typing import Any

from reconciler.phase3 import git_ancestry
from reconciler.phase3.rule_api import DriftRule, Findings

RULE_ID = "D107-RECORDS-NON-DESCENDANT"
REGISTRY_KEY = "records-integrity"

CLASS_BLOCKING = "blocking"
CLASS_AMBER = "amber"
LEVEL_ESCALATE = 5  # section 53.2 Level 5
LEVEL_WARN = 2


def _finding(now: _dt.datetime, **kw: Any) -> dict[str, Any]:
    base = {
        "record_schema_version": 1,
        "registry_key": REGISTRY_KEY,
        "comparison_row": "Records repository head versus last anchor (D107)",
        "is_canary": False,
        "observed_at": now.astimezone(_dt.timezone.utc).isoformat(),
        "acknowledged_by": None,
        "acknowledged_at": None,
    }
    base.update(kw)
    return base


def _evaluate(context: dict[str, Any]) -> Findings:
    now = context.get("now") or _dt.datetime.now(_dt.timezone.utc)
    head = str(context.get("records_head_sha") or "")
    anchor_sha = context.get("last_anchor_sha")
    clone = context.get("records_clone")
    if not head or clone is None:
        return [
            _finding(
                now,
                finding_id=f"{RULE_ID}:input-unavailable",
                drift_class=CLASS_BLOCKING,
                level=LEVEL_ESCALATE,
                declared="an observable records head",
                actual="input_unavailable",
                reason=(
                    "the records head could not be read; section 40.1 requires a "
                    "check that cannot reach the records repository to fail closed "
                    "rather than report zero"
                ),
            )
        ]
    if not anchor_sha:
        return [
            _finding(
                now,
                finding_id=f"{RULE_ID}:first-observation",
                drift_class=CLASS_AMBER,
                level=LEVEL_WARN,
                declared="a previously anchored head",
                actual=head,
                reason=(
                    "no previous anchor: recorded on first sight and reported once, "
                    "never silently (53.1 first-observation precedent)"
                ),
            )
        ]
    if git_ancestry.is_ancestor(pathlib.Path(clone), str(anchor_sha), head):
        return []
    return [
        _finding(
            now,
            finding_id=f"{RULE_ID}:{head[:12]}",
            drift_class=CLASS_BLOCKING,
            level=LEVEL_ESCALATE,
            declared=str(anchor_sha),
            actual=head,
            reason=(
                "the records head does not descend from the last anchored SHA: "
                "proof of rewriting (D107), Blocking at Level 5"
            ),
        )
    ]


RULE = DriftRule(rule_id=RULE_ID, registry_key=REGISTRY_KEY, evaluate=_evaluate)
PYEOF
cat > validators/drift/rules/records_signature_rule.py <<'PYEOF'
"""An unsigned or foreign-signed records commit is Blocking drift (D107).

D107: "The records-writer signs every commit, and a commit on the default
branch that is unsigned, or signed by any other identity, is Blocking drift.
This is the same authorship discipline the Renovate bypass carries (Section
33.2): a scoped grant is a grant to one identity, and the store must carry
that identity's work only."

Detection lands in this lane by the master entry-and-exit criteria (L4P1-E2);
the store itself is L4's.

Context keys read:
    records_commits           [{sha, signature_verified: bool, signer: str}]
    records_writer_identity   the declared signing identity
"""
from __future__ import annotations

import datetime as _dt
from typing import Any

from reconciler.phase3.rule_api import DriftRule, Findings

RULE_ID = "D107-RECORDS-COMMIT-SIGNATURE"
REGISTRY_KEY = "records-integrity"

CLASS_BLOCKING = "blocking"
LEVEL_BLOCK = 4  # section 53.2 Level 4 - Block

REASON_UNSIGNED = "unsigned commit on the records default branch"
REASON_FOREIGN = "commit signed by an identity other than the records-writer"


def _evaluate(context: dict[str, Any]) -> Findings:
    now = context.get("now") or _dt.datetime.now(_dt.timezone.utc)
    declared = str(context.get("records_writer_identity") or "").lower()
    commits = list(context.get("records_commits") or [])
    if not declared:
        return [
            {
                "record_schema_version": 1,
                "finding_id": f"{RULE_ID}:input-unavailable",
                "registry_key": REGISTRY_KEY,
                "comparison_row": "Records commit signature (D107)",
                "declared": "a declared records-writer identity",
                "actual": "input_unavailable",
                "drift_class": CLASS_BLOCKING,
                "level": LEVEL_BLOCK,
                "reason": "no declared records-writer identity; failing closed (40.1)",
                "is_canary": False,
                "observed_at": now.astimezone(_dt.timezone.utc).isoformat(),
                "acknowledged_by": None,
                "acknowledged_at": None,
            }
        ]
    findings: Findings = []
    for commit in commits:
        signer = str(commit.get("signer") or "").lower()
        verified = bool(commit.get("signature_verified"))
        if verified and signer == declared:
            continue
        findings.append(
            {
                "record_schema_version": 1,
                "finding_id": f"{RULE_ID}:{str(commit.get('sha', ''))[:12]}",
                "registry_key": REGISTRY_KEY,
                "comparison_row": "Records commit signature (D107)",
                "declared": declared,
                "actual": signer or "unsigned",
                "drift_class": CLASS_BLOCKING,
                "level": LEVEL_BLOCK,
                "reason": REASON_UNSIGNED if not verified else REASON_FOREIGN,
                "commit_sha": commit.get("sha"),
                "is_canary": False,
                "observed_at": now.astimezone(_dt.timezone.utc).isoformat(),
                "acknowledged_by": None,
                "acknowledged_at": None,
            }
        )
    return findings


RULE = DriftRule(rule_id=RULE_ID, registry_key=REGISTRY_KEY, evaluate=_evaluate)
PYEOF
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
cat > validators/drift/tests/test_records_integrity_rules.py <<'PYEOF'
import datetime as dt
import pathlib
import subprocess

from reconciler.phase3 import discovery as d
from reconciler.phase3 import git_ancestry
from validators.drift.rules import records_anchor_rule as anchor_rule
from validators.drift.rules import records_signature_rule as sig_rule

NOW = dt.datetime(2026, 6, 10, 12, 0, tzinfo=dt.timezone.utc)


def _commit(repo, msg):
    subprocess.run(
        [
            "git", "-C", str(repo),
            "-c", "user.email=t@example.invalid",
            "-c", "user.name=t",
            "commit", "-q", "--allow-empty", "-m", msg,
        ],
        check=True,
        capture_output=True,
    )
    return subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _repo(tmp_path: pathlib.Path) -> pathlib.Path:
    repo = tmp_path / "records"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True, capture_output=True)
    return repo


def test_both_rules_are_discovered_by_glob():
    ids = [r.rule_id for r in d.discover_rules()]
    assert anchor_rule.RULE_ID in ids and sig_rule.RULE_ID in ids


def test_an_appended_head_descends_from_the_anchor(tmp_path):
    repo = _repo(tmp_path)
    first = _commit(repo, "a")
    second = _commit(repo, "b")
    assert git_ancestry.is_ancestor(repo, first, second) is True


def test_a_rewritten_head_does_not_descend(tmp_path):
    repo = _repo(tmp_path)
    first = _commit(repo, "a")
    _commit(repo, "b")
    subprocess.run(
        ["git", "-C", str(repo), "reset", "-q", "--hard", first],
        check=True,
        capture_output=True,
    )
    rewritten = _commit(repo, "b-rewritten")
    subprocess.run(
        ["git", "-C", str(repo), "reset", "-q", "--hard", first],
        check=True,
        capture_output=True,
    )
    orphan = _commit(repo, "c")
    assert git_ancestry.is_ancestor(repo, rewritten, orphan) is False


def test_an_unknown_object_is_not_an_ancestor(tmp_path):
    repo = _repo(tmp_path)
    head = _commit(repo, "a")
    assert git_ancestry.is_ancestor(repo, "0" * 40, head) is False


def test_a_descendant_head_produces_no_finding(tmp_path):
    repo = _repo(tmp_path)
    first = _commit(repo, "a")
    second = _commit(repo, "b")
    out = anchor_rule.RULE.evaluate(
        {"now": NOW, "records_clone": repo, "records_head_sha": second, "last_anchor_sha": first}
    )
    assert out == []


def test_a_non_descendant_head_is_blocking_level_5(tmp_path):
    repo = _repo(tmp_path)
    first = _commit(repo, "a")
    subprocess.run(
        ["git", "-C", str(repo), "checkout", "-q", "--orphan", "other"],
        check=True,
        capture_output=True,
    )
    other = _commit(repo, "orphan")
    out = anchor_rule.RULE.evaluate(
        {"now": NOW, "records_clone": repo, "records_head_sha": other, "last_anchor_sha": first}
    )
    assert len(out) == 1
    assert (out[0]["drift_class"], out[0]["level"]) == ("blocking", 5)


def test_the_first_observation_is_amber_once_never_silent(tmp_path):
    repo = _repo(tmp_path)
    head = _commit(repo, "a")
    out = anchor_rule.RULE.evaluate(
        {"now": NOW, "records_clone": repo, "records_head_sha": head, "last_anchor_sha": None}
    )
    assert len(out) == 1 and out[0]["drift_class"] == "amber"


def test_an_unreadable_records_head_fails_closed():
    out = anchor_rule.RULE.evaluate({"now": NOW})
    assert out[0]["drift_class"] == "blocking" and out[0]["actual"] == "input_unavailable"


def test_a_correctly_signed_commit_produces_no_finding():
    out = sig_rule.RULE.evaluate(
        {
            "now": NOW,
            "records_writer_identity": "records-writer",
            "records_commits": [
                {"sha": "a" * 40, "signature_verified": True, "signer": "records-writer"}
            ],
        }
    )
    assert out == []


def test_an_unsigned_commit_is_blocking():
    out = sig_rule.RULE.evaluate(
        {
            "now": NOW,
            "records_writer_identity": "records-writer",
            "records_commits": [{"sha": "b" * 40, "signature_verified": False, "signer": ""}],
        }
    )
    assert out[0]["drift_class"] == "blocking"
    assert out[0]["reason"] == sig_rule.REASON_UNSIGNED


def test_a_foreign_signed_commit_is_blocking():
    out = sig_rule.RULE.evaluate(
        {
            "now": NOW,
            "records_writer_identity": "records-writer",
            "records_commits": [
                {"sha": "c" * 40, "signature_verified": True, "signer": "somebody-else"}
            ],
        }
    )
    assert out[0]["reason"] == sig_rule.REASON_FOREIGN


def test_a_signature_finding_is_level_4():
    out = sig_rule.RULE.evaluate(
        {
            "now": NOW,
            "records_writer_identity": "records-writer",
            "records_commits": [{"sha": "d" * 40, "signature_verified": False, "signer": ""}],
        }
    )
    assert out[0]["level"] == 4


def test_no_declared_writer_identity_fails_closed():
    out = sig_rule.RULE.evaluate({"now": NOW, "records_commits": []})
    assert out[0]["actual"] == "input_unavailable"


def test_both_rules_count_in_the_records_integrity_bucket():
    assert anchor_rule.REGISTRY_KEY == sig_rule.REGISTRY_KEY == "records-integrity"


def test_findings_carry_the_acknowledgement_fields():
    out = sig_rule.RULE.evaluate(
        {
            "now": NOW,
            "records_writer_identity": "records-writer",
            "records_commits": [{"sha": "e" * 40, "signature_verified": False, "signer": ""}],
        }
    )
    assert "acknowledged_by" in out[0] and "acknowledged_at" in out[0]
PYEOF
python3 -m pytest -q validators/drift/tests/test_records_integrity_rules.py
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
python3 -m ruff check reconciler validators/drift
git add reconciler validators/drift
git status --porcelain
git commit -m "L3-P3-T11: D107 non-descendant head Blocking at Level 5; records commit signature rule"
git push -u origin lane/3/p3-t11
gh pr create --base integration --head lane/3/p3-t11 \
  --title "L3-P3-T11 records tamper-evidence rules" \
  --body "Lane 3, Phase 3, task T11. A records head that does not descend from the last anchored SHA is Blocking drift at Level 5 (D107); an unsigned or foreign-signed records commit is Blocking at Level 4 (D107, routed here by L4P1-E2). First observation is Amber once, never silence. Ancestry fails closed. Owned paths only."
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
| --- | --- | --- | --- |
| 1 | Fifteen tests pass | `python3 -m pytest -q validators/drift/tests/test_records_integrity_rules.py 2>&1 \| grep -oE '^[0-9]+ passed'` | `15 passed` |
| 2 | A non-descendant head is Blocking at Level 5 | `python3 -m pytest -q validators/drift/tests/test_records_integrity_rules.py -k "non_descendant_head_is_blocking" 2>&1 \| grep -oE '^[0-9]+ passed'` | `1 passed` |
| 3 | Both rules are discovered by glob | `python3 -c "from reconciler.phase3 import discovery as d;ids=[r.rule_id for r in d.discover_rules()];print(sum(i.startswith('D107-') for i in ids))"` | `2` |
| 4 | An unreadable records head fails closed | `python3 -c "from validators.drift.rules import records_anchor_rule as r;print(r.RULE.evaluate({})[0]['drift_class'])"` | `blocking` |
| 5 | Lint clean | `python3 -m ruff check reconciler validators/drift` | `All checks passed!` |
| 6 | No foreign path touched | `git -C ~/control-plane diff --name-only origin/integration...HEAD \| grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'` | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd ~/control-plane
python3 -m pytest -q validators/drift/tests/test_records_integrity_rules.py 2>&1 | grep -oE '^[0-9]+ passed'
python3 -c "from reconciler.phase3 import discovery as d;print(sum(r.rule_id.startswith('D107-') for r in d.discover_rules()))"
python3 -c "from validators.drift.rules import records_anchor_rule as r;f=r.RULE.evaluate({});print(f[0]['drift_class'], f[0]['level'])"
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'
```

Expected output, exactly four lines:

```
15 passed
2
blocking 5
0
```

### STOP rule

**Stop and open a blocker if any of the following is true.**

* The test count is not `15 passed`.
* `is_ancestor` would be made to return `True` when git cannot resolve an object. Fail closed: a missing ancestor is what a rewrite looks like.
* You are about to classify a non-descendant head below Blocking, or below Level 5. D107 is explicit: *"A non-descendant head is **Blocking drift, Level 5**."*
* You are about to make the signature rule tolerate an unsigned commit "because signing is not configured yet". An unconfigured signer is `input_unavailable`, which this rule already reports as Blocking. It is not a reason to pass. Universal STOP preamble rule 5.

---

## L3-P3-T12 — D96 — the behavioural envelope: signed run record and published counts

| Field | Value |
| --- | --- |
| **Task id** | `L3-P3-T12` |
| **Size** | L |
| **Depends on** | `L3-P3-T02` |
| **Spec anchors** | **D96**; §40.1 (*"The behavioural envelope"*: *"a **required signed run record** naming the scheduled trigger … a **run-count ceiling per day** (calibrated configuration, initial value: twice the scheduled run count …); an **expected source host**; and **published per-run API-call counts**"*); §51.2 (the schedule the ceiling is calibrated from); §53.1; §99.6 risk 6 |
| **Files created** | `reconciler/config/envelope.yaml`, `reconciler/phase3/envelope.py`, `reconciler/tests/test_envelope.py` |

**Purpose.** §40.1 replaces the near-vacuous *"outside its scheduled window"* rule with four behavioural bounds. This task declares them as calibrated configuration and produces the artifact they are checked against: the run record, its canonical digest, its signature, and its published per-run API-call counts. T13 enforces them.

**Two values are deliberately unarmed, and both are named rather than invented:**

* `expected_source_host` is `null`. The operations VM is subsystem **M**, which PARTITION.md gives to **L5** (`ops-vm/**`), and §40.1 gives no host name. The check reports `input_unavailable` — §52.2's arming discipline — until L0 records the host.
* `signing` has no key material here. The fifth-tier credential and its signing configuration live on the operations VM (§40.1, §99.2 subsystem M) and belong to **L5**. This module signs through an **injected signer**; the default signer refuses, so an unsigned run record is impossible to produce by accident.

**`mutation_cap_per_run` is `0` in this phase, and that is not a placeholder.** §99.6 risk 6 mandates *detect-only first* and no repair class is enabled (L3 Phase 2's exit criterion E3). A reconciler that mutates nothing has a per-run mutation cap of zero; raising it is part of enabling a repair class, which is a governance act in a later phase.

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
git fetch origin
git switch integration
git pull --ff-only origin integration
git switch -c lane/3/p3-t12
mkdir -p reconciler/config
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
cat > reconciler/config/envelope.yaml <<'YAMLEOF'
# The reconciler credential's behavioural envelope (D96, section 40.1).
#
# Section 40.1: "Each fifth-tier credential therefore declares a behavioural
# envelope in its inventory entry, and a run outside it is Blocking drift: a
# required signed run record naming the scheduled trigger, so any run without
# a matching trigger record raises immediately; a run-count ceiling per day
# (calibrated configuration, initial value: twice the scheduled run count,
# recalibrated whenever the schedule changes); an expected source host; and
# published per-run API-call counts."
#
# D96: "a run without a matching scheduled trigger is Blocking."
envelope_version: 1
credential_id: reconciler
spec_refs: ["D96", "40.1", "51.2", "53.1", "99.6"]

# The declared scheduled triggers. Section 40.1: the credential "fires
# nightly, on registry change and at least hourly for security-class checks".
# Section 51.2: "Full reconciliation completes at least daily"; "Security-class
# checks at least hourly".
scheduled_triggers:
  - id: nightly-full-reconciliation
    cadence: daily
  - id: hourly-security-class
    cadence: hourly
  - id: on-registry-merge
    cadence: event

# Run-count ceiling per day. Section 40.1: "initial value: twice the scheduled
# run count, recalibrated whenever the schedule changes".
# 1 nightly + 24 hourly = 25 scheduled runs per day.
scheduled_runs_per_day: 25
run_count_ceiling_multiplier: 2

# UNARMED. Section 40.1 requires an expected source host; it does not name one,
# and the operations VM is L5's (ops-vm/**, subsystem M). Until L0 records it,
# the check reports input_unavailable rather than passing (52.2 arming
# discipline).
expected_source_host: null

# Per-run cap on objects mutated. Section 99.6 risk 6: "Detect-only first;
# repair classes enabled one at a time." No repair class is enabled, so the
# reconciler mutates nothing and the cap is zero. Raising this is part of
# enabling a repair class - a governance act, not an edit.
mutation_cap_per_run: 0

# Section 40.1: "published per-run API-call counts, so read-side abuse ...
# surfaces as a volume anomaly rather than as nothing."
publish_api_call_counts: true
YAMLEOF
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
cat > reconciler/phase3/envelope.py <<'PYEOF'
"""The reconciler behavioural envelope (D96, spec 40.1).

Produces the artifact the envelope is judged against: a run record naming the
scheduled trigger and the source host, carrying the published per-run
API-call counts and the count of objects mutated, with a canonical digest and
a signature.

Signing key material is NOT here. The fifth-tier credential lives on the
operations VM, which is L5's (ops-vm/**, subsystem M). This module signs
through an injected signer and its default signer refuses, so an unsigned run
record cannot be produced by accident.
"""
from __future__ import annotations

import dataclasses
import datetime as _dt
import hashlib
import json
import pathlib
from typing import Any, Callable

import yaml

CONFIG = pathlib.Path("reconciler/config/envelope.yaml")

RECORD_SCHEMA_VERSION = 1
INPUT_UNAVAILABLE = "input_unavailable"


class EnvelopeError(RuntimeError):
    pass


def load_envelope(path: pathlib.Path | None = None) -> dict[str, Any]:
    p = path or CONFIG
    if not p.is_file():
        raise EnvelopeError(f"behavioural envelope absent: {p}")
    cfg = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    if not cfg.get("scheduled_triggers"):
        raise EnvelopeError(f"{p} declares no scheduled_triggers")
    return cfg


def trigger_ids(cfg: dict[str, Any]) -> tuple[str, ...]:
    return tuple(str(t["id"]) for t in cfg["scheduled_triggers"])


def run_count_ceiling(cfg: dict[str, Any]) -> int:
    """Section 40.1: twice the scheduled run count, as calibrated configuration."""
    return int(cfg["scheduled_runs_per_day"]) * int(cfg["run_count_ceiling_multiplier"])


def unarmed_checks(cfg: dict[str, Any]) -> list[str]:
    """Envelope checks with no declared value. Named, never silently passed."""
    out = []
    if cfg.get("expected_source_host") in (None, ""):
        out.append("expected_source_host")
    return sorted(out)


class ApiCallCounter:
    """Published per-run API-call counts (40.1, D96).

    Counts by HTTP method and by resource family, so that read-side abuse -
    which emits no webhook and no event-log entry - shows up as a volume
    anomaly.
    """

    def __init__(self) -> None:
        self._by_method: dict[str, int] = {}
        self._by_resource: dict[str, int] = {}

    def record(self, method: str, resource: str) -> None:
        m = method.upper()
        self._by_method[m] = self._by_method.get(m, 0) + 1
        self._by_resource[resource] = self._by_resource.get(resource, 0) + 1

    @property
    def total(self) -> int:
        return sum(self._by_method.values())

    def published(self) -> dict[str, Any]:
        return {
            "total": self.total,
            "by_method": dict(sorted(self._by_method.items())),
            "by_resource": dict(sorted(self._by_resource.items())),
        }


@dataclasses.dataclass(frozen=True)
class RunRecord:
    run_id: str
    trigger_id: str
    source_host: str | None
    started_at: str
    finished_at: str
    api_call_counts: dict[str, Any]
    objects_mutated: int
    signature: str | None = None

    def unsigned_payload(self) -> dict[str, Any]:
        return {
            "record_schema_version": RECORD_SCHEMA_VERSION,
            "record_kind": "reconciliation-run",
            "credential_id": "reconciler",
            "run_id": self.run_id,
            "trigger_id": self.trigger_id,
            "source_host": self.source_host or INPUT_UNAVAILABLE,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "api_call_counts": self.api_call_counts,
            "objects_mutated": self.objects_mutated,
        }

    def canonical_bytes(self) -> bytes:
        return json.dumps(
            self.unsigned_payload(), sort_keys=True, separators=(",", ":")
        ).encode("utf-8")

    def digest(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()

    def as_payload(self) -> dict[str, Any]:
        payload = self.unsigned_payload()
        payload["digest_sha256"] = self.digest()
        payload["signature"] = self.signature
        return payload


def refusing_signer(_: bytes) -> str:
    """The default signer. Refuses, because the key is not this lane's.

    Section 40.1 requires a *signed* run record. An unsigned record must be
    impossible to produce by accident, so the default is a refusal rather than
    an empty string.
    """
    raise EnvelopeError(
        "no signer configured: the reconciler's fifth-tier signing key lives on "
        "the operations VM (40.1, subsystem M, owned by L5). Inject a signer."
    )


def build_run_record(
    run_id: str,
    trigger_id: str,
    source_host: str | None,
    started_at: _dt.datetime,
    finished_at: _dt.datetime,
    counter: ApiCallCounter,
    objects_mutated: int = 0,
) -> RunRecord:
    for ts in (started_at, finished_at):
        if ts.tzinfo is None:
            raise EnvelopeError("timestamps must be UTC with offset (97.1)")
    return RunRecord(
        run_id=run_id,
        trigger_id=trigger_id,
        source_host=source_host,
        started_at=started_at.astimezone(_dt.timezone.utc).isoformat(),
        finished_at=finished_at.astimezone(_dt.timezone.utc).isoformat(),
        api_call_counts=counter.published(),
        objects_mutated=objects_mutated,
    )


def sign(record: RunRecord, signer: Callable[[bytes], str] = refusing_signer) -> RunRecord:
    return dataclasses.replace(record, signature=signer(record.canonical_bytes()))
PYEOF
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
cat > reconciler/tests/test_envelope.py <<'PYEOF'
import datetime as dt

import pytest

from reconciler.phase3 import envelope as e

START = dt.datetime(2026, 6, 10, 1, 0, tzinfo=dt.timezone.utc)
END = dt.datetime(2026, 6, 10, 1, 5, tzinfo=dt.timezone.utc)


def _counter():
    c = e.ApiCallCounter()
    c.record("GET", "orgs/members")
    c.record("GET", "orgs/members")
    c.record("GET", "repos/branches")
    return c


def _record(trigger="nightly-full-reconciliation", host=None, mutated=0):
    return e.build_run_record("run-1", trigger, host, START, END, _counter(), mutated)


def test_the_envelope_declares_three_scheduled_triggers():
    assert len(e.trigger_ids(e.load_envelope())) == 3


def test_the_run_count_ceiling_is_twice_the_scheduled_run_count():
    assert e.run_count_ceiling(e.load_envelope()) == 50


def test_the_expected_source_host_is_named_as_unarmed():
    assert e.unarmed_checks(e.load_envelope()) == ["expected_source_host"]


def test_the_mutation_cap_is_zero_while_detect_only():
    assert e.load_envelope()["mutation_cap_per_run"] == 0


def test_an_absent_envelope_fails_closed(tmp_path):
    with pytest.raises(e.EnvelopeError):
        e.load_envelope(tmp_path / "absent.yaml")


def test_api_call_counts_are_published_by_method_and_resource():
    published = _counter().published()
    assert published["total"] == 3
    assert published["by_method"]["GET"] == 3
    assert published["by_resource"]["orgs/members"] == 2


def test_the_run_record_names_the_scheduled_trigger():
    assert _record().unsigned_payload()["trigger_id"] == "nightly-full-reconciliation"


def test_an_unknown_source_host_is_reported_unavailable_not_omitted():
    assert _record().unsigned_payload()["source_host"] == "input_unavailable"


def test_the_run_record_publishes_its_api_call_counts():
    assert _record().unsigned_payload()["api_call_counts"]["total"] == 3


def test_timestamps_must_carry_an_offset():
    with pytest.raises(e.EnvelopeError):
        e.build_run_record("r", "t", None, dt.datetime(2026, 6, 10), END, _counter())


def test_the_digest_is_stable_for_the_same_content():
    assert _record().digest() == _record().digest()


def test_the_digest_changes_when_the_trigger_changes():
    assert _record().digest() != _record(trigger="hourly-security-class").digest()


def test_the_default_signer_refuses():
    with pytest.raises(e.EnvelopeError):
        e.sign(_record())


def test_an_injected_signer_produces_a_signed_record():
    signed = e.sign(_record(), signer=lambda b: "sig:" + b[:4].decode())
    assert signed.signature.startswith("sig:")


def test_the_signed_payload_carries_the_digest_and_the_signature():
    signed = e.sign(_record(), signer=lambda b: "sig")
    payload = signed.as_payload()
    assert payload["signature"] == "sig" and len(payload["digest_sha256"]) == 64


def test_the_payload_carries_the_record_schema_version():
    assert _record().as_payload()["record_schema_version"] == 1
PYEOF
python3 -m pytest -q reconciler/tests/test_envelope.py
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
python3 -m ruff check reconciler validators/drift
git add reconciler
git status --porcelain
git commit -m "L3-P3-T12: D96 behavioural envelope - signed run record and published API-call counts"
git push -u origin lane/3/p3-t12
gh pr create --base integration --head lane/3/p3-t12 \
  --title "L3-P3-T12 the behavioural envelope" \
  --body "Lane 3, Phase 3, task T12. Declares the D96 envelope as calibrated configuration - scheduled triggers, run-count ceiling at twice the scheduled run count, expected source host (unarmed and named), zero mutation cap while detect-only - and builds the signed run record with published per-run API-call counts. The default signer refuses; the key is L5's. Owned paths only."
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
| --- | --- | --- | --- |
| 1 | Sixteen tests pass | `python3 -m pytest -q reconciler/tests/test_envelope.py 2>&1 \| grep -oE '^[0-9]+ passed'` | `16 passed` |
| 2 | The ceiling is twice the scheduled run count | `python3 -c "from reconciler.phase3 import envelope as e;print(e.run_count_ceiling(e.load_envelope()))"` | `50` |
| 3 | The unarmed check is named, not hidden | `python3 -c "from reconciler.phase3 import envelope as e;print(e.unarmed_checks(e.load_envelope()))"` | `['expected_source_host']` |
| 4 | The mutation cap is zero while detect-only | `python3 -c "from reconciler.phase3 import envelope as e;print(e.load_envelope()['mutation_cap_per_run'])"` | `0` |
| 5 | An unsigned run record cannot be produced by accident | `python3 -m pytest -q reconciler/tests/test_envelope.py -k "default_signer_refuses" 2>&1 \| grep -oE '^[0-9]+ passed'` | `1 passed` |
| 6 | No foreign path touched | `git -C ~/control-plane diff --name-only origin/integration...HEAD \| grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'` | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd ~/control-plane
python3 -m pytest -q reconciler/tests/test_envelope.py 2>&1 | grep -oE '^[0-9]+ passed'
python3 -c "from reconciler.phase3 import envelope as e;c=e.load_envelope();print(e.run_count_ceiling(c), e.load_envelope()['mutation_cap_per_run'], e.unarmed_checks(c))"
python3 -c "from reconciler.phase3 import envelope as e;print(len(e.trigger_ids(e.load_envelope())))"
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'
```

Expected output, exactly four lines:

```
16 passed
50 0 ['expected_source_host']
3
0
```

### STOP rule

**Stop and open a blocker if any of the following is true.**

* The test count is not `16 passed`.
* You are about to invent an `expected_source_host`. It is not stated by §40.1 and the host is L5's. *Decision needed from L0*: `What is the reconciler credential's expected source host (40.1 behavioural envelope), and which lane records it?`
* You are about to put key material, a private key path, or a token into `reconciler/**`. Fifth-tier credentials live on the operations VM (§40.1). This lane holds none.
* You are about to make `refusing_signer` return an empty string so a test passes. §40.1 requires a *signed* run record; an unsigned one that looks signed is worse than none.
* You are about to raise `mutation_cap_per_run` above `0`. No repair class is enabled; raising the cap is part of enabling one, in a later phase, under §99.6 risk 6.

---

## L3-P3-T13 — D96 — envelope enforcement; unmatched trigger is Blocking

| Field | Value |
| --- | --- |
| **Task id** | `L3-P3-T13` |
| **Size** | M |
| **Depends on** | `L3-P3-T12` |
| **Spec anchors** | **D96** (*"a run without a matching scheduled trigger is Blocking"*); §40.1 (*"a run outside it is Blocking drift"*); §53.2 Level 4; §64.2 fail-closed discipline as applied by §40.1 (*"an alert that cannot fire is a gate that appears to be working and is not"*) |
| **Files created** | `validators/drift/rules/envelope_rule.py`, `reconciler/hooks/envelope_gate_hook.py`, `validators/drift/tests/test_envelope_rule.py` |

**Purpose.** Enforce the four bounds T12 declared. Two mechanisms, deliberately:

* A **discovered drift rule** raises the findings — so an envelope breach is visible on the drift view like any other Blocking finding, and travels the same dispatch and the same counts.
* A **pre-phase run hook** fails the run closed before any comparison, for the two breaches that mean *this run should not be happening at all*: an unmatched scheduled trigger and a missing signature. §40.1's whole argument is that an alert that cannot fire is not a gate; a run that continues after failing its own envelope check is the same thing.

| Breach | Class | Level | Hook stops the run |
| --- | --- | --- | --- |
| No matching scheduled trigger (**D96**) | Blocking | 4 | **Yes** |
| Run record unsigned | Blocking | 4 | **Yes** |
| Daily run count above the ceiling | Blocking | 4 | No |
| Source host differs from the expected host | Blocking | 4 | No |
| Objects mutated above the per-run cap | Blocking | 4 | No |
| Expected source host unarmed | Blocking (`input_unavailable`) | 4 | No |

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
git fetch origin
git switch integration
git pull --ff-only origin integration
git switch -c lane/3/p3-t13
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
cat > validators/drift/rules/envelope_rule.py <<'PYEOF'
"""Behavioural-envelope enforcement (D96, spec 40.1).

D96: "a run without a matching scheduled trigger is Blocking."
Section 40.1: "a run outside it is Blocking drift."

Context keys read:
    run_record      the payload from reconciler.phase3.envelope.RunRecord
    runs_today      integer count of runs by this credential in the UTC day
    envelope_config optional path override for tests
"""
from __future__ import annotations

import datetime as _dt
from typing import Any

from reconciler.phase3 import envelope
from reconciler.phase3.rule_api import DriftRule, Findings

RULE_ID = "D96-ENVELOPE-BREACH"
REGISTRY_KEY = "credential-envelope"

CLASS_BLOCKING = "blocking"
LEVEL_BLOCK = 4  # section 53.2 Level 4 - Block

BREACH_UNMATCHED_TRIGGER = "unmatched-scheduled-trigger"
BREACH_UNSIGNED = "unsigned-run-record"
BREACH_RUN_COUNT = "run-count-ceiling-exceeded"
BREACH_SOURCE_HOST = "unexpected-source-host"
BREACH_MUTATION_CAP = "mutation-cap-exceeded"
BREACH_HOST_UNARMED = "expected-source-host-unarmed"

STOP_THE_RUN = (BREACH_UNMATCHED_TRIGGER, BREACH_UNSIGNED)


def _finding(now: _dt.datetime, breach: str, declared: Any, actual: Any) -> dict[str, Any]:
    return {
        "record_schema_version": 1,
        "finding_id": f"{RULE_ID}:{breach}",
        "registry_key": REGISTRY_KEY,
        "comparison_row": "Reconciler behavioural envelope (D96, 40.1)",
        "breach": breach,
        "declared": declared,
        "actual": actual,
        "drift_class": CLASS_BLOCKING,
        "level": LEVEL_BLOCK,
        "is_canary": False,
        "observed_at": now.astimezone(_dt.timezone.utc).isoformat(),
        "acknowledged_by": None,
        "acknowledged_at": None,
    }


def breaches(
    run_record: dict[str, Any],
    runs_today: int,
    cfg: dict[str, Any],
) -> list[tuple[str, Any, Any]]:
    """Every envelope breach in this run, as (breach, declared, actual)."""
    out: list[tuple[str, Any, Any]] = []
    triggers = envelope.trigger_ids(cfg)
    trigger = run_record.get("trigger_id")
    if trigger not in triggers:
        out.append((BREACH_UNMATCHED_TRIGGER, list(triggers), trigger))
    if not run_record.get("signature"):
        out.append((BREACH_UNSIGNED, "a signed run record", "unsigned"))
    ceiling = envelope.run_count_ceiling(cfg)
    if int(runs_today) > ceiling:
        out.append((BREACH_RUN_COUNT, ceiling, int(runs_today)))
    expected_host = cfg.get("expected_source_host")
    actual_host = run_record.get("source_host")
    if expected_host in (None, ""):
        out.append((BREACH_HOST_UNARMED, "a declared expected source host", actual_host))
    elif actual_host != expected_host:
        out.append((BREACH_SOURCE_HOST, expected_host, actual_host))
    cap = int(cfg.get("mutation_cap_per_run", 0))
    mutated = int(run_record.get("objects_mutated", 0))
    if mutated > cap:
        out.append((BREACH_MUTATION_CAP, cap, mutated))
    return out


def _evaluate(context: dict[str, Any]) -> Findings:
    now = context.get("now") or _dt.datetime.now(_dt.timezone.utc)
    cfg = envelope.load_envelope(context.get("envelope_config"))
    run_record = context.get("run_record")
    if not run_record:
        return [_finding(now, BREACH_UNSIGNED, "a signed run record", "input_unavailable")]
    return [
        _finding(now, breach, declared, actual)
        for breach, declared, actual in breaches(
            run_record, int(context.get("runs_today", 0)), cfg
        )
    ]


RULE = DriftRule(rule_id=RULE_ID, registry_key=REGISTRY_KEY, evaluate=_evaluate)
PYEOF
cat > reconciler/hooks/envelope_gate_hook.py <<'PYEOF'
"""Fail the run closed on the two envelope breaches that invalidate it (D96).

Section 40.1: "an alert that cannot fire is a gate that appears to be working
and is not." A run that continues after failing its own envelope check is the
same thing, so the two breaches that mean this run should not be happening -
no matching scheduled trigger, and an unsigned run record - stop it here,
before any comparison.

Discovered by glob from reconciler/hooks/*.py.
"""
from __future__ import annotations

from typing import Any

from reconciler.phase3 import envelope
from reconciler.phase3.rule_api import RunHook
from validators.drift.rules import envelope_rule


class EnvelopeGateError(RuntimeError):
    pass


def _run(context: dict[str, Any]) -> dict[str, Any]:
    cfg = envelope.load_envelope(context.get("envelope_config"))
    run_record = context.get("run_record")
    if not run_record:
        raise EnvelopeGateError(
            "no signed run record for this run: section 40.1 requires one, and a "
            "run without a matching trigger record raises immediately (D96)"
        )
    found = envelope_rule.breaches(run_record, int(context.get("runs_today", 0)), cfg)
    stopping = sorted(b for b, _, _ in found if b in envelope_rule.STOP_THE_RUN)
    if stopping:
        raise EnvelopeGateError(f"envelope breach stops the run: {stopping}")
    return {"envelope_breaches": sorted(b for b, _, _ in found)}


HOOK = RunHook(hook_id="envelope-gate", phase="pre", run=_run)
PYEOF
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
cat > validators/drift/tests/test_envelope_rule.py <<'PYEOF'
import datetime as dt

import pytest

from reconciler.hooks import envelope_gate_hook as gate
from reconciler.phase3 import discovery as d
from reconciler.phase3 import envelope
from validators.drift.rules import envelope_rule as er

NOW = dt.datetime(2026, 6, 10, 12, 0, tzinfo=dt.timezone.utc)


def _record(trigger="nightly-full-reconciliation", signature="sig", mutated=0, host=None):
    return {
        "record_kind": "reconciliation-run",
        "run_id": "run-1",
        "trigger_id": trigger,
        "source_host": host or envelope.INPUT_UNAVAILABLE,
        "objects_mutated": mutated,
        "signature": signature,
    }


def _breaches(**kw):
    ctx = {"now": NOW, "run_record": _record(**kw.pop("record", {})), **kw}
    return {f["breach"] for f in er.RULE.evaluate(ctx)}


def test_the_rule_is_discovered_by_glob():
    assert er.RULE_ID in [r.rule_id for r in d.discover_rules()]


def test_a_run_without_a_matching_scheduled_trigger_is_blocking():
    ctx = {"now": NOW, "run_record": _record(trigger="somebody-elses-trigger")}
    findings = [f for f in er.RULE.evaluate(ctx) if f["breach"] == er.BREACH_UNMATCHED_TRIGGER]
    assert findings and findings[0]["drift_class"] == "blocking"


def test_an_unmatched_trigger_is_level_4():
    ctx = {"now": NOW, "run_record": _record(trigger="nope")}
    f = next(x for x in er.RULE.evaluate(ctx) if x["breach"] == er.BREACH_UNMATCHED_TRIGGER)
    assert f["level"] == 4


def test_a_matched_trigger_raises_no_trigger_breach():
    assert er.BREACH_UNMATCHED_TRIGGER not in _breaches()


def test_an_unsigned_run_record_is_a_breach():
    assert er.BREACH_UNSIGNED in _breaches(record={"signature": None})


def test_a_run_count_above_the_ceiling_is_a_breach():
    assert er.BREACH_RUN_COUNT in _breaches(runs_today=51)


def test_a_run_count_at_the_ceiling_is_not_a_breach():
    assert er.BREACH_RUN_COUNT not in _breaches(runs_today=50)


def test_a_mutation_above_the_cap_is_a_breach():
    assert er.BREACH_MUTATION_CAP in _breaches(record={"mutated": 1})


def test_no_mutation_is_within_the_cap():
    assert er.BREACH_MUTATION_CAP not in _breaches()


def test_the_unarmed_source_host_is_reported_not_passed():
    assert er.BREACH_HOST_UNARMED in _breaches()


def test_a_missing_run_record_is_blocking():
    findings = er.RULE.evaluate({"now": NOW})
    assert findings[0]["drift_class"] == "blocking"


def test_the_gate_hook_is_a_pre_phase_hook():
    assert gate.HOOK.phase == "pre" and gate.HOOK.hook_id == "envelope-gate"


def test_the_gate_stops_a_run_with_no_matching_trigger():
    with pytest.raises(gate.EnvelopeGateError):
        gate.HOOK.run({"run_record": _record(trigger="nope"), "runs_today": 1})


def test_the_gate_stops_an_unsigned_run():
    with pytest.raises(gate.EnvelopeGateError):
        gate.HOOK.run({"run_record": _record(signature=None), "runs_today": 1})


def test_the_gate_stops_a_run_with_no_run_record():
    with pytest.raises(gate.EnvelopeGateError):
        gate.HOOK.run({"runs_today": 1})


def test_the_gate_lets_a_valid_run_proceed_and_reports_the_rest():
    out = gate.HOOK.run({"run_record": _record(), "runs_today": 1})
    assert er.BREACH_HOST_UNARMED in out["envelope_breaches"]
PYEOF
python3 -m pytest -q validators/drift/tests/test_envelope_rule.py
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
python3 -m ruff check reconciler validators/drift
git add reconciler validators/drift
git status --porcelain
git commit -m "L3-P3-T13: D96 envelope enforcement - unmatched trigger is Blocking and stops the run"
git push -u origin lane/3/p3-t13
gh pr create --base integration --head lane/3/p3-t13 \
  --title "L3-P3-T13 envelope enforcement" \
  --body "Lane 3, Phase 3, task T13. A discovered drift rule raises Blocking, Level 4, on every envelope breach - unmatched scheduled trigger, unsigned run record, run count above the ceiling, unexpected source host, mutation above the cap - and a pre-phase hook fails the run closed on the two breaches that invalidate it. Owned paths only."
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
| --- | --- | --- | --- |
| 1 | Sixteen tests pass | `python3 -m pytest -q validators/drift/tests/test_envelope_rule.py 2>&1 \| grep -oE '^[0-9]+ passed'` | `16 passed` |
| 2 | An unmatched trigger is Blocking at Level 4 | `python3 -c "import datetime as t;from validators.drift.rules import envelope_rule as e;n=t.datetime(2026,6,10,tzinfo=t.timezone.utc);f=[x for x in e.RULE.evaluate({'now':n,'run_record':{'trigger_id':'nope','signature':'s','source_host':'h','objects_mutated':0}}) if x['breach']==e.BREACH_UNMATCHED_TRIGGER];print(f[0]['drift_class'], f[0]['level'])"` | `blocking 4` |
| 3 | The gate stops an unsigned run | `python3 -m pytest -q validators/drift/tests/test_envelope_rule.py -k "gate_stops" 2>&1 \| grep -oE '^[0-9]+ passed'` | `3 passed` |
| 4 | Exactly two breaches stop the run | `python3 -c "from validators.drift.rules import envelope_rule as e;print(e.STOP_THE_RUN)"` | `('unmatched-scheduled-trigger', 'unsigned-run-record')` |
| 5 | Lint clean | `python3 -m ruff check reconciler validators/drift` | `All checks passed!` |
| 6 | No foreign path touched | `git -C ~/control-plane diff --name-only origin/integration...HEAD \| grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'` | `0` |

### SELF-VERIFY

```bash
set -euo pipefail
cd ~/control-plane
python3 -m pytest -q validators/drift/tests/test_envelope_rule.py 2>&1 | grep -oE '^[0-9]+ passed'
python3 -c "from validators.drift.rules import envelope_rule as e;print(e.STOP_THE_RUN)"
python3 -c "from reconciler.phase3 import discovery as d;print(sorted(h.hook_id for h in d.discover_hooks()))"
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'
```

Expected output, exactly four lines:

```
16 passed
('unmatched-scheduled-trigger', 'unsigned-run-record')
['envelope-gate', 'records-anchor', 'repair-freeze']
0
```

### STOP rule

**Stop and open a blocker if any of the following is true.**

* The test count is not `16 passed`.
* The hook list is not `['envelope-gate', 'records-anchor', 'repair-freeze']`. T09 and T10 must be merged to `integration` and this branch rebased on it; if they are not, rebase and re-run. Do not delete a hook to make the list match.
* You are about to make the gate hook non-fatal so a run completes. §40.1: *"an alert that cannot fire is a gate that appears to be working and is not."* Universal STOP preamble rule 5.
* You are about to classify an envelope breach below Blocking. §40.1 says *"a run outside it is Blocking drift"*, and D96 says an unmatched trigger *"is Blocking"*.

---

## L3-P3-T14 — AT-102 acceptance harness and the phase exit gate

| Field | Value |
| --- | --- |
| **Task id** | `L3-P3-T14` |
| **Size** | M |
| **Depends on** | `L3-P3-T03`, `L3-P3-T05`, `L3-P3-T06`, `L3-P3-T08`, `L3-P3-T09`, `L3-P3-T11`, `L3-P3-T13` |
| **Spec anchors** | **AT-102** verbatim; **EC-109**; **D63**; §53.1; §53.7; §52 (SIG-13) |
| **Files created** | `reconciler/tests/test_at102_acceptance.py`, `reconciler/tests/verify_phase3.sh`, `reconciler/PHASE3-EXIT.md` |

**Purpose.** Prove **AT-102** end to end, in one file, against the code the previous thirteen tasks built — not against a mock of it. AT-102 has four clauses and each becomes an assertion:

| AT-102 clause | Assertion |
| --- | --- |
| *"Every reconciliation run must find the deliberately seeded canary drift"* | A healthy run's findings contain the canary, reached by glob discovery |
| *"A run reporting zero findings — the canary included — is a **failed** run"* | Every blinding yields `FAILED`; no blinding yields `CLEAN` |
| *"raises SIG-13 (failed reconciliations)"* | The failed verdict's `signal` is `SIG-13` |
| *"and triggers the gap procedure"* | The failed verdict produces a Level 5 gap window, and the gap procedure runs all five §53.7 steps over it |

**AT-102 is proved here and nowhere else.** No other task in this phase claims it.

**Run this task last.** Its whole-phase count is only correct once the thirteen prior branches are merged to `integration` and this branch is rebased on it.

### Commands

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
git fetch origin
git switch integration
git pull --ff-only origin integration
git switch -c lane/3/p3-t14
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
cat > reconciler/tests/test_at102_acceptance.py <<'PYEOF'
"""AT-102 end to end (spec 53.1, EC-109, D63).

AT-102, verbatim:
    "The seeded reconciliation canary. Every reconciliation run must find the
     deliberately seeded canary drift. A run reporting zero findings - the
     canary included - is a failed run, raises SIG-13 (failed
     reconciliations), and triggers the gap procedure; a reconciler that finds
     nothing is assumed broken, never assumed clean."

This file exercises the real modules: glob discovery, the canary rule, the
verdict function, gap detection and the gap procedure runner.
"""
import datetime as dt

from reconciler.phase3 import discovery, gap_detect, gap_procedure, run_verdict
from reconciler.tests.blinding import blinders

NOW = dt.datetime(2026, 6, 10, 12, 0, tzinfo=dt.timezone.utc)
CTX = {"now": NOW}


def _healthy_verdict():
    findings, counts = blinders.healthy(CTX)
    return run_verdict.decide(findings, counts, NOW)


def _blinded_verdict(name="findings_filtered"):
    findings, counts = blinders.BLINDERS[name](CTX)
    return run_verdict.decide(findings, counts, NOW)


def test_at102_a_healthy_run_finds_the_seeded_canary():
    findings, _ = blinders.healthy(CTX)
    assert run_verdict.canary_found(findings) is True


def test_at102_the_canary_is_reached_by_discovery_not_by_a_list():
    assert "CANARY-DRIFT-001" in [r.rule_id for r in discovery.discover_rules()]


def test_at102_a_healthy_run_is_clean():
    assert _healthy_verdict().verdict == run_verdict.CLEAN


def test_at102_a_run_reporting_zero_findings_is_failed_never_clean():
    verdicts = {
        run_verdict.decide(*blinders.BLINDERS[name](CTX), now=NOW).verdict
        for name in blinders.BLINDERS
    }
    assert verdicts == {run_verdict.FAILED}


def test_at102_a_failed_run_raises_sig_13():
    assert _blinded_verdict().signal == "SIG-13"


def test_at102_a_failed_run_is_level_5():
    assert _blinded_verdict().level == 5


def test_at102_a_failed_run_triggers_the_gap_procedure():
    assert _blinded_verdict().gap_procedure_required is True


def test_at102_the_failed_run_produces_a_level_5_gap_window():
    v = _blinded_verdict()
    gap = gap_detect.gap_from_verdict(
        v.verdict, NOW - dt.timedelta(hours=24), NOW, v.reasons
    )
    assert gap is not None and gap.level == 5


def test_at102_the_gap_procedure_runs_all_five_steps_over_that_window():
    v = _blinded_verdict()
    gap = gap_detect.gap_from_verdict(
        v.verdict, NOW - dt.timedelta(hours=24), NOW, v.reasons
    ).as_record_payload()
    result = gap_procedure.run(
        gap,
        gap_procedure.REHEARSAL_INPUTS,
        lambda: _healthy_verdict(),
        now=NOW,
    )
    assert tuple(s.step for s in result.steps) == gap_procedure.STEPS


def test_at102_the_gap_procedure_reruns_standing_checks_including_the_canary():
    v = _blinded_verdict()
    gap = gap_detect.gap_from_verdict(
        v.verdict, NOW - dt.timedelta(hours=24), NOW, v.reasons
    ).as_record_payload()
    result = gap_procedure.run(
        gap, gap_procedure.REHEARSAL_INPUTS, lambda: _healthy_verdict(), now=NOW
    )
    step = result.steps[2]
    assert step.status == "clean" and step.items[0]["canary_found"] is True
PYEOF
python3 -m pytest -q reconciler/tests/test_at102_acceptance.py
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
cat > reconciler/tests/verify_phase3.sh <<'SHEOF'
#!/usr/bin/env bash
# L3 Phase 3 exit gate. Runs every Phase 3 test file, by name, and nothing else.
# The file list is explicit so that a missing file is a failure rather than a
# smaller number that still looks green.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

FILES="
reconciler/tests/test_p3_entry.py
reconciler/tests/test_p3_discovery.py
reconciler/tests/test_run_verdict.py
reconciler/tests/test_canary_negative.py
reconciler/tests/test_registry_stage.py
reconciler/tests/test_write_scope_allowlist.py
reconciler/tests/test_gap_detect.py
reconciler/tests/test_gap_procedure.py
reconciler/tests/test_loop_ran_wrong.py
reconciler/tests/test_anchor.py
reconciler/tests/test_envelope.py
reconciler/tests/test_at102_acceptance.py
validators/drift/tests/test_canary_loader.py
validators/drift/tests/test_canary_rule.py
validators/drift/tests/test_machine_registry_write_rule.py
validators/drift/tests/test_records_integrity_rules.py
validators/drift/tests/test_envelope_rule.py
"

MISSING=""
for f in $FILES; do
  [ -f "$f" ] || MISSING="$MISSING $f"
done
if [ -n "$MISSING" ]; then
  echo "PHASE3 FAIL missing-test-files:$MISSING"
  exit 1
fi

COUNT=$(python3 -m pytest -q $FILES 2>&1 | grep -oE '^[0-9]+ passed' | grep -oE '^[0-9]+' || true)
if [ "$COUNT" != "217" ]; then
  echo "PHASE3 FAIL test-count=$COUNT expected=217"
  exit 1
fi

CANARY=$(python3 -c "from reconciler.phase3 import discovery as d;print('CANARY-DRIFT-001' in [r.rule_id for r in d.discover_rules()])")
if [ "$CANARY" != "True" ]; then
  echo "PHASE3 FAIL canary-not-discovered"
  exit 1
fi

VERDICT=$(python3 -c "from reconciler.phase3 import run_verdict as v;print(v.decide([]).verdict)")
if [ "$VERDICT" != "FAILED" ]; then
  echo "PHASE3 FAIL zero-findings-not-failed"
  exit 1
fi

HOOKS=$(python3 -c "from reconciler.phase3 import discovery as d;print(','.join(sorted(h.hook_id for h in d.discover_hooks())))")
if [ "$HOOKS" != "envelope-gate,records-anchor,repair-freeze" ]; then
  echo "PHASE3 FAIL hooks=$HOOKS"
  exit 1
fi

FOREIGN=$(git diff --name-only origin/integration...HEAD \
  | grep -vcE '^(reconciler/|tools/provision/|validators/drift/)' || true)
if [ "$FOREIGN" != "0" ]; then
  echo "PHASE3 FAIL foreign-paths=$FOREIGN"
  exit 1
fi

echo "PHASE3 PASS"
SHEOF
chmod +x reconciler/tests/verify_phase3.sh
bash reconciler/tests/verify_phase3.sh
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
cat > reconciler/PHASE3-EXIT.md <<'MDEOF'
# L3 Phase 3 — Instrument Integrity — exit record

Subsystems C and D. Owned paths: reconciler/**, tools/provision/**,
validators/drift/**. Fifteen tasks, T00 to T14.

## What this phase built

| Mechanism | Spec source | Where it lives |
| --- | --- | --- |
| The seeded canary, declared as configuration | 53.1, AT-102, D63 | validators/drift/canary/ |
| The canary as a discovered comparison row | 53.1, EC-109 | validators/drift/rules/canary_rule.py |
| Per-registry comparison counts | 53.1 | reconciler/phase3/counts.py |
| The FAILED-run rule | 53.1, AT-102, 53.2 Level 5, SIG-13 | reconciler/phase3/run_verdict.py |
| Four negative blindings | D63, EC-109 | reconciler/tests/blinding/ |
| Canary-set-first registry staging, one-cycle fleet hold | D93, 26.4, 61.3, 61.5 | reconciler/phase3/registry_stage.py |
| Write-scope allowlist as data; machine-write drift rule | D93, 40.1 | reconciler/phase3/write_scope.py |
| Control-loop gap detection | 53.7, 51.2, AT-032 | reconciler/phase3/gap_detect.py |
| The five-step gap procedure | 53.7, 46.1 | reconciler/phase3/gap_procedure.py |
| The "when the loop ran wrong" branch | 53.7, 28.1, 26.4 | reconciler/phase3/loop_ran_wrong.py |
| The per-run records anchor | D107, 63.1, invariant 47 | reconciler/phase3/anchor.py |
| Non-descendant head, Blocking Level 5; commit signature | D107, L4P1-E2 | validators/drift/rules/records_*_rule.py |
| The behavioural envelope and its signed run record | D96, 40.1 | reconciler/phase3/envelope.py |
| Envelope enforcement; unmatched trigger stops the run | D96, 40.1 | validators/drift/rules/envelope_rule.py |

Acceptance test proved: **AT-102**, by reconciler/tests/test_at102_acceptance.py.
Carried incidentally: AT-032 (self-observability), by gap detection.
Signal raised by this phase's code: **SIG-13** only.

## What this phase deliberately did not do

* No repair class was enabled. Section 99.6 risk 6: detect-only first.
  mutation_cap_per_run is 0 for that reason and for no other.
* No record was written. Every record store belongs to L4; steps 4 and 5 of
  the gap procedure emit manifests for L4's tooling to consume.
* No file was created under derived/ in this phase. DR-3.1 ratified: derived/** is now owned by L0 (REG-026). See L0-00-03 generator additions.

## Open items handed to L0

| Item | Question | Interim default in force |
| --- | --- | --- |
| DR-3.1 | **RATIFIED** — bytes unchanged. T06 and T10 both assert sha256 `2dffc3c7…` — identical content makes the two branches merge correctly. Anchor destination path: derived/anchors/records-head.yaml; write-scope allowlist: ["derived/**"]; derived/** now owned by L0 (REG-026). See L0-00-03 generator additions. | reconciler/config/anchoring.yaml: derived/anchors/records-head.yaml, ["derived/**"] |
| DR-3.2 | The canary finding's drift class and budget treatment | green, counts_against_budget: false |
| D-L3-04(a) | Where the canary is planted against real platform state (filed by Phase 1) | a literal-versus-literal mismatch in canary.yaml |
| Export gap window | The declared organisation-export cadence (SIG-34) and the lane that records its last success | gap.yaml export kind is UNARMED; the detector reports input_unavailable |
| Expected source host | The reconciler credential's expected source host (40.1) | envelope.yaml expected_source_host is null; the check reports input_unavailable |
| Authority delta (26.4) | The CI check that fails a registry diff adding capability or Write without a linked decision record | Not built here. It belongs to validators/registry/**, which is L1's |
| Gap-procedure CLI alias | master/05 L3P3-E5 invokes `reconciler.cli gap-procedure --rehearse` | This phase provides `python -m reconciler.phase3.gap_procedure --rehearse`. Registering a reconciler.cli subcommand would edit a Phase 1 file, which Section 3 forbids |

An open item above is a stated gap, not a silent one. A green suite with an
unarmed check is an honest green: the unarmed checks name themselves through
gap_detect.unarmed_kinds() and envelope.unarmed_checks().
MDEOF
```

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
python3 -m ruff check reconciler validators/drift
bash reconciler/tests/verify_phase3.sh
git add reconciler
git status --porcelain
git commit -m "L3-P3-T14: AT-102 acceptance harness, phase 3 exit gate and exit record"
git push -u origin lane/3/p3-t14
gh pr create --base integration --head lane/3/p3-t14 \
  --title "L3-P3-T14 AT-102 acceptance and phase 3 exit" \
  --body "Lane 3, Phase 3, task T14. Proves AT-102 end to end against the real modules - discovery, the canary rule, the verdict function, gap detection and the gap procedure - and adds the phase exit gate (217 Phase 3 tests, canary discovered, zero findings FAILED, three hooks, no foreign path) and the exit record. Owned paths only."
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
| --- | --- | --- | --- |
| 1 | AT-102 passes end to end | `python3 -m pytest -q reconciler/tests/test_at102_acceptance.py 2>&1 \| grep -oE '^[0-9]+ passed'` | `10 passed` |
| 2 | The whole phase passes: 217 tests | `bash reconciler/tests/verify_phase3.sh` | `PHASE3 PASS` |
| 3 | Zero findings is never a clean run | `python3 -c "from reconciler.phase3 import run_verdict as v;print(v.decide([]).verdict)"` | `FAILED` |
| 4 | All three run hooks are discovered | `python3 -c "from reconciler.phase3 import discovery as d;print(sorted(h.hook_id for h in d.discover_hooks()))"` | `['envelope-gate', 'records-anchor', 'repair-freeze']` |
| 5 | All six Phase 3 drift rules are discovered | `python3 -c "from reconciler.phase3 import discovery as d;print(len(d.discover_rules()))"` | `5` |
| 6 | The exit record carries the open-items section | `grep -c "Open items handed to L0" reconciler/PHASE3-EXIT.md` | `1` |

*(Criterion 5 counts the rules **this phase** publishes into `validators/drift/rules/`: the canary rule, the machine-write rule, the two D107 records rules and the envelope rule — five. Phase 1's comparators are not in this directory and are not counted here. If the number is larger, another lane or a later phase has added a rule file; re-read Section 3 before changing anything.)*

### SELF-VERIFY

```bash
set -euo pipefail
cd ~/control-plane
bash reconciler/tests/verify_phase3.sh
python3 -m pytest -q reconciler/tests/test_at102_acceptance.py 2>&1 | grep -oE '^[0-9]+ passed'
python3 -c "from reconciler.phase3 import discovery as d;print(len(d.discover_rules()), sorted(h.hook_id for h in d.discover_hooks()))"
git diff --name-only origin/integration...HEAD | grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'
```

Expected output, exactly four lines:

```
PHASE3 PASS
10 passed
5 ['envelope-gate', 'records-anchor', 'repair-freeze']
0
```

### STOP rule

**Stop and open a blocker if any of the following is true.**

* `verify_phase3.sh` prints `PHASE3 FAIL missing-test-files: …`. A prior task's branch has not merged to `integration`. Rebase and wait. **Never delete a name from the file list to make the gate pass** — the explicit list exists so that a missing file fails loudly instead of producing a smaller green number.
* `verify_phase3.sh` prints `PHASE3 FAIL test-count=…`. Report the number you got and the number expected. Do not adjust the expected number; adjusting it is how a phase exits with tests that silently stopped running, which is the instrument failure this entire phase is about.
* `PHASE3 FAIL zero-findings-not-failed`. AT-102 is broken. This is the most serious failure in the phase.
* `PHASE3 FAIL canary-not-discovered`. The canary rule file is absent or does not expose `RULE`.
* Any earlier task's branch is unmerged. Rebase and wait — PARTITION.md: *"A lane NEVER merges another lane's branch."*

---

## 5. Phase exit conditions — all must hold before this phase is reported complete

Run these on a `lane/3/p3-t14` branch rebased on an `integration` that carries all fourteen prior task branches.

| # | Condition | Command | Required output |
| --- | --- | --- | --- |
| E1 | All fifteen task commits are on `integration` | `git -C ~/control-plane log --oneline origin/integration \| grep -c "L3-P3-T"` | `15` |
| E2 | The phase gate passes | `bash reconciler/tests/verify_phase3.sh` | `PHASE3 PASS` |
| E3 | A run reporting zero findings is FAILED, at Level 5, raising SIG-13, requiring the gap procedure | `python3 -c "from reconciler.phase3 import run_verdict as v;d=v.decide([]);print(d.verdict, d.level, d.signal, d.gap_procedure_required)"` | `FAILED 5 SIG-13 True` |
| E4 | The seeded canary exists, is labelled, and is a mismatch | `python3 -c "from validators.drift.canary import loader as l;c=l.load();print(c.label, c.declared != c.actual)"` | `SEEDED-CANARY-DO-NOT-REMOVE True` |
| E5 | Every blinding of the instrument is caught | `python3 -c "import datetime as t;from reconciler.phase3 import run_verdict as v;from reconciler.tests.blinding import blinders as b;n=t.datetime(2026,6,10,tzinfo=t.timezone.utc);print(sorted({v.decide(*b.BLINDERS[k]({'now':n}), now=n).verdict for k in b.BLINDERS}))"` | `['FAILED']` |
| E6 | The fleet is never released without one clean, exercised canary cycle | `python3 -m pytest -q reconciler/tests/test_registry_stage.py -k "release or unexercised" 2>&1 \| grep -oE '^[0-9]+ passed'` | `4 passed` |
| E7 | A machine write outside the declared scope is Blocking | `python3 -m pytest -q validators/drift/tests/test_machine_registry_write_rule.py -k "blocking" 2>&1 \| grep -oE '^[0-9]+ passed'` | `2 passed` |
| E8 | The gap procedure runs all five §53.7 steps | `python3 -m reconciler.phase3.gap_procedure --rehearse --out /tmp/gap-exit.json` | `GAP-PROCEDURE COMPLETE steps=5` |
| E9 | A non-descendant records head is Blocking at Level 5 | `python3 -m pytest -q validators/drift/tests/test_records_integrity_rules.py -k "non_descendant_head_is_blocking" 2>&1 \| grep -oE '^[0-9]+ passed'` | `1 passed` |
| E10 | An unmatched scheduled trigger stops the run | `python3 -m pytest -q validators/drift/tests/test_envelope_rule.py -k "gate_stops" 2>&1 \| grep -oE '^[0-9]+ passed'` | `3 passed` |
| E11 | No repair class was enabled by this phase | `python3 -c "from reconciler.phase3 import envelope as e;print(e.load_envelope()['mutation_cap_per_run'])"` | `0` |
| E12 | Nothing was written under `derived/`, `records/` or `events/` | see the path-boundary block below | `0` |
| E13 | No commit in this phase touched a foreign path | see the path-boundary block below | `0` |
| E14 | The exit record exists and names AT-102 | `grep -c "AT-102" reconciler/PHASE3-EXIT.md` | at least `1` |

The path-boundary block, run verbatim — these two commands carry the literal alternation that a table cell cannot:

> ⚠ SUPERSEDED — see L3-06-tasks.md
**Commands**

```bash
set -euo pipefail
cd ~/control-plane
git fetch origin
BASE=$(git merge-base origin/main origin/integration)
git diff --name-only "$BASE"...origin/integration | grep -cE '^(derived/|records/|events/)' || true
git diff --name-only "$BASE"...origin/integration | grep -vcE '^(reconciler/|tools/provision/|validators/drift/)'
```

Expected output, exactly two lines:

```
0
0
```

**E12 and E13 are absolute.** They are the PARTITION.md contract expressed as a command. A phase that passes every other criterion and fails one of these has not exited; it has produced a merge conflict for another lane.

**On the open items.** Six items in `reconciler/PHASE3-EXIT.md` are unanswered by L0, and every one of them is a *named* gap with an interim default in force. None of them blocks exit, and none of them is hidden: `gap_detect.unarmed_kinds()` returns `['export']` and `envelope.unarmed_checks()` returns `['expected_source_host']` on demand, so the phase reports its own coverage honestly. Report that state to L0 exactly as it is. An unarmed check reported as armed would be the same lie the seeded canary exists to catch — a green report from an instrument that was not looking.

**What the next phase inherits.** A reconciler whose silence is now loud: a run that finds nothing is a failed run, a run whose comparison narrowed is a failed run, a records history that was rewritten is Blocking at Level 5, a run that nobody scheduled does not start, and a registry change cannot reach the fleet until one clean, exercised canary cycle says it may. Nothing in this phase repairs anything, and that is the point — §99.6 risk 6 permits auto-repair only after detection has run clean, and the instrument that reports "clean" is now itself under test.

**This phase is complete when E1 through E14 all hold on `integration`, and not before.**
