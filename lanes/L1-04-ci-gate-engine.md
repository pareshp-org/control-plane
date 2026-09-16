# L1 — PHASE 4: THE CI GATE ENGINE

> **REFERENCE ONLY** — FD-095 (2026-09-09): Task bodies absorbed into L1-05-tasks.md. Do not execute from this file.

**Lane:** L1 Registries & Contracts (Subsystems A and B of spec §99.2)
**Branch prefix:** `lane/1/*` — this phase uses `lane/1/04-<slug>`
**Repository:** `control-plane`
**Paths this lane may write (PARTITION, frozen):** `schemas/registry/**`, `schemas/product/**`, `registries/**`, `validators/registry/**`
**Paths this phase actually writes:** `validators/registry/**`, `schemas/registry/gate-rule.v1.schema.json`, `registries/canary/**`

> **Naming disambiguation.** "Phase 4" here is *build-lane phase 4 of Lane 1*. It is unrelated to the per-product onboarding "Phase 4" of spec §98.2 / §96.4. Nothing in this file touches product onboarding.

---

## 0. What this phase is, and what it is deliberately not

Lane 1 phases 1–3 produce **rules**: individual validators that check registries and contracts against the Subsystem B obligations of §99.2 — "multi-version schema validators, referential integrity (assignments name existing non-departed people; dependencies name existing services), date rules (mandatory end dates for non-employees, restore-tested within window, expired assignments fail), the 24x7-without-rota and commitments-conflict blockers, exception-without-expiry rejection, unclassified-control rejection".

Phase 4 produces the **engine that runs them and decides the merge**: discovery, exit-code semantics, the failure report that names *which rule failed and where*, and the negative-test discipline that stops the whole apparatus from becoming a gate that reads green and checks nothing (§11.1, §33.2 line "a job skipped by an `if:` condition reports a `skipped` conclusion that branch protection counts as satisfied").

### Ownership boundaries this phase must not cross

| Thing | Owner | Consequence for this phase |
|---|---|---|
| `validators/registry/**` | **L1 (this lane)** | Everything below is written here |
| `validators/drift/**` — the reconciliation drift validators of §53.1 | **L3** | The engine MUST NOT discover, import, execute or reference them. L1-04-05 carries a test asserting this |
| `.github/workflows/**` | **L2** | This lane **cannot write the workflow**. It ships a CLI with a frozen invocation contract; L2 wires the job that emits the required status check |
| `contracts/**`, `CODEOWNERS`, `docs/**`, root files, `Makefile` | **L0** | No file at repository root is created or edited by this phase — including `.gitignore`. The engine therefore never writes inside the repository unless explicitly told to (see exit-code and `--report` rules) |
| `records/**`, `events/**` | **L4** | The gate writes no record. It prints and returns an exit code |

### The spec obligations this phase implements

| Obligation | Source |
|---|---|
| Registry/contract validation is a **required status check** — the "contract validation" context listed in branch protection | §11.3 |
| Every required check name is emitted by a job with **no `if:` and no path filter**; "no work was needed" is an explicit recorded success, never a skip | §33.2 |
| **The seeded-canary rule** — a permanently seeded, clearly labelled mismatch that every run MUST find; a run reporting zero findings including the canary is a **FAILED** run, not a clean one | §53.1, **AT-102**, **D63** |
| **An instrument that cannot fail is not an instrument** — the seeded-defect discipline applied to the thing that reads green | §31.2, **D97**, **SIG-18** |
| Exactly one severity scale exists: Green / Amber / Red / Blocking, and only Blocking "Blocks work"; Red is material but non-blocking | §53.4 |
| Control-plane CI must be able to answer "which live checks exist", because an invariant classified `mechanical` that names no live check must fail CI | §101 preamble |
| No shared mutable index — directory-per-item only | PARTITION rule 3 |

---

## 1. Frozen engine contract (read before any task)

> # FD-094: Option B grammar — updated 2026-09-09

Everything below is **fixed by this document**. No task may vary it.

### 1.1 Tree layout

```
validators/registry/
  README.md                  # the human-readable copy of this contract   (T-01)
  requirements.txt           # pinned Python dependencies                 (T-01)
  gate.py                    # the runner / CLI                            (T-05)
  gate_lib/
    __init__.py
    discovery.py             # rule discovery + layout audit               (T-03)
    report.py                # finding parsing + report emission           (T-04)
  fixtures/
    baseline/                # ONE shared, valid, read-only control-plane tree (T-06)
      registries/...
      schemas/...
  rules/
    <rule-id>/
      rule.yaml              # rule metadata, validated by the rule schema
      check.py               # the validator itself (written in phases 1–3)
      fixtures/
        must-fail/
          <case>/
            overlay/         # files copied over baseline to break it
            expect.txt       # substring the resulting FINDING must contain
        pass/                # OPTIONAL extra positive cases
          <case>/
            overlay/
```

`schemas/registry/gate-rule.v1.schema.json` is the JSON Schema for `rule.yaml` (T-03).
`registries/canary/seeded-canary.yaml` is the permanent seeded canary of §53.1 (T-06).

### 1.2 `rule.yaml` — required keys

| Key | Type | Rule |
|---|---|---|
| `id` | string | MUST equal the containing directory name; MUST match `^[A-Za-z0-9][A-Za-z0-9._-]{1,63}$` |
| `title` | string | One line, non-empty |
| `severity` | enum | Exactly one of `green`, `amber`, `red`, `blocking` — the single scale of §53.4. No other vocabulary exists |
| `spec_ref` | string | Non-empty. The spec section or AT id the rule enforces, e.g. `§99.2 subsystem B` |
| `subsystem` | string | `A` or `B` |
| `owner_lane` | string | MUST be the literal `L1` |
| `applies_to` | array of strings | ≥1 glob, relative to the target root, e.g. `registries/people.yaml` |

### 1.3 `check.py` — the rule-author contract

Enforced mechanically by the engine. A rule violating it is an **engine error**, not a pass.

* Invoked as `python3 <rule-dir>/check.py --root <target-root>`. `<target-root>` is a directory containing `registries/` and `schemas/`.
* **stdout carries findings and nothing else.** Every stdout line is exactly:
  `FINDING <rule-id> <severity> <path>:<line> <message>` — `<path>` relative to `--root`, `<line>` an integer (`0` when not line-anchored), `<severity>` from the §53.4 scale. Diagnostics go to stderr.
* Exit `0` = no findings. Exit `1` = one or more findings. **Any other exit code is an instrument error.**
* **Unparseable input inside the rule's own `applies_to` scope MUST produce a FINDING**, never a crash and never silence. This obligation is what makes the universal negative-test recipe of §1.6 valid for every rule.

### 1.4 Exit-code semantics of `gate.py` (frozen)

| Code | Name | Meaning | Merge |
|---|---|---|---|
| `0` | `GATE PASS` | ≥1 rule discovered; every must-fail fixture failed as required; the seeded canary was found; no `red` or `blocking` finding against the live tree | Allowed |
| `1` | `GATE VIOLATION` | At least one `red` or `blocking` finding against the live tree. This is the ordinary "your registry change is wrong" failure | Blocked |
| `2` | `GATE ENGINE ERROR` | A rule crashed, emitted malformed stdout, returned an exit code other than 0/1, exceeded its timeout, or `rule.yaml`/layout failed validation | Blocked |
| `3` | `GATE CANARY FAILURE` | The instrument stopped discriminating: zero rules discovered, a rule with zero must-fail fixtures, a must-fail fixture that passed, a must-fail fixture whose finding did not match `expect.txt`, or a live run in which the seeded canary produced zero findings | Blocked |

No other exit code is ever returned. Every non-zero code blocks the merge.

`amber` and `green` findings are printed and recorded in the JSON report but never affect the exit code — §53.4 gives Amber "Blocks work: No".

### 1.5 Failure reporting — which rule failed, and where

Every finding that contributes to a non-zero exit prints on stderr, one per line, in exactly this form:

```
GATE FAIL <rule-id> <severity> <path>:<line> <message>
```

When `GITHUB_ACTIONS=true` the engine additionally prints a workflow annotation per finding so the failure lands on the diff line in the pull request:

```
::error file=<path>,line=<line>,title=GATE FAIL <rule-id>::<message>
```

The final stderr line of any run is exactly one of:

```
GATE RESULT pass rules=<N> findings=<M> canary=found
GATE RESULT violation rules=<N> findings=<M> canary=found
GATE RESULT engine-error rules=<N> reason=<short-reason>
GATE RESULT canary-failure rules=<N> reason=<short-reason>
```

A machine-readable report is written **only** when `--report <path>` is given. The engine never writes inside the repository by default, because every repository-root path belongs to L0.

### 1.6 Negative-test discipline — the seeded-canary rule applied to the validators

This is the load-bearing part of the phase. §53.1: *"A run that reports zero findings, including the canary, is a FAILED run, not a clean one: it proves the instrument stopped looking."* AT-102 makes the same statement a pass/fail test. D97 applies it to verification contracts. Phase 4 applies it to registry validators, in two independent layers:

**Layer 1 — per-rule must-fail fixtures.** Every rule directory MUST contain at least one `fixtures/must-fail/<case>/`. Each case is an *overlay*: files copied over the shared baseline tree to break it, plus `expect.txt`. The engine, for each case: copies `fixtures/baseline/` to a temp dir, copies `overlay/` over it (a file named `X.DELETE` in the overlay deletes `X`), runs the rule against it, and **requires exit 1 with at least one FINDING carrying this rule's id and containing the `expect.txt` substring**. A must-fail fixture that passes is exit code `3`. A rule with zero must-fail fixtures is exit code `3`.

**The universal recipe.** Because §1.3 obliges every rule to report unparseable input in its own scope as a FINDING, one negative case is always mechanically constructible for any rule: overwrite the first file its `applies_to` matches with the literal `INVALID: [` and expect the rule's id in the finding. L1-04-07 uses exactly this recipe and nothing else. No judgment, no rule semantics required.

**Layer 2 — the live seeded canary.** `registries/canary/seeded-canary.yaml` is a permanently seeded, clearly labelled mismatch (§53.1). The rule `gate-selftest-canary` reports it as an `amber` finding on every live run. The engine asserts that this rule produced **≥1 finding on every live run**; zero is exit code `3`, never a clean run. Amber severity keeps the canary from blocking merges while still proving on every single run that the pipeline from discovery → execution → parsing → reporting is intact.

### 1.7 Invocation contract handed to L2

> **WITHDRAWN: `gate.py` is not the L2-facing entry point. `ci-preflight.sh` is the single L2-facing entry point (REG-018 Option A). L2 must call `ci-preflight.sh`, not `gate.py` directly.**
>
> # FD-094: Option B grammar — updated 2026-09-09

```
python -m validators.registry.cli --root . --as-of $(date +%Y-%m-%d) --records-root . --format json
```

Run from the repository root, on every pull request and every push to `integration` and `main`, in a job carrying **no `if:` condition and no path filter** (§33.2). The job's conclusion is the required status check. See the DECISION REQUIRED block in §4.

---

## 2. Task dependency graph

| Task | Title | Size | Depends on |
|---|---|---|---|
| L1-04-01 | Freeze the engine contract and pin the toolchain | S | — (phase entry) |
| L1-04-02 | Rule-layout conformance sweep | M | L1-04-01 |
| L1-04-03 | Rule metadata schema and discovery module | M | L1-04-02 |
| L1-04-04 | Finding parser and reporter module | M | L1-04-03 |
| L1-04-05 | The `gate.py` runner: live mode and exit codes | L | L1-04-04 |
| L1-04-06 | Baseline fixture, seeded canary, fixtures mode | M | L1-04-05 |
| L1-04-07 | Must-fail fixture backfill for every rule | L | L1-04-06 |
| L1-04-08 | Preflight script and the L2 handoff package | M | L1-04-07 |
| L1-04-09 | Phase exit gate | S | L1-04-08 |

Execute strictly in order. One branch, one pull request per task, rebased on `integration` before opening (PARTITION, Branch & merge model).

---

## 3. Standing procedures

### 3.1 Per-task preamble — run before every task

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git status --porcelain            # expect: empty
git fetch origin
git checkout integration
git pull --ff-only
python3 --version                 # expect: Python 3.11.x or newer
```

### 3.2 Per-task lane-guard — run before every `gh pr create`

```bash
set -euo pipefail
git diff --name-only origin/integration...HEAD \
  | grep -vE '^(schemas/registry/|schemas/product/|registries/|validators/registry/)' \
  && { echo "FOREIGN PATH TOUCHED - STOP"; exit 1; } \
  || echo "LANE-GUARD OK"
```

Correct output is exactly `LANE-GUARD OK`. Any other output is a STOP.

### 3.3 Blocker-issue template — file this instead of proceeding, whenever a STOP rule fires

```bash
set -euo pipefail
gh issue create \
  --title "BLOCKER L1-04 <task-id>: <one-line condition>" \
  --label "blocker,lane-1,phase-4" \
  --body "$(cat <<'EOF'
LANE: L1 Registries & Contracts
PHASE: 4 (CI gate engine)
TASK: <task-id>
BRANCH: <branch name>

STOP RULE THAT FIRED:
<quote the STOP rule verbatim from the task>

OBSERVED:
<paste the exact command and its exact output, including exit code>

WHAT I DID NOT DO:
Stopped before <next step>. No files were committed beyond <last commit sha>.

DECISION NEEDED FROM L0:
<one sentence — what must be decided or reassigned>

BLOCKED TASKS: every task from <task-id> onward in L1-04.
EOF
)"
```

After filing, stop work on the phase. Do not improvise a fix, do not widen scope, do not touch another lane's paths.

---

## 4. DECISION REQUIRED — L0 (integrator) only

These three items cross lane boundaries. This lane cannot decide them and MUST NOT act on them. File them as one L0 decision request at the start of the phase (L1-04-01 acceptance criterion 5) and continue with the rest of the phase while they are open; only L1-04-08 consumes the answers.

```
DECISION REQUIRED — L0
CONTEXT: L1 phase 4 ships the registry gate engine as a CLI. `.github/workflows/**`
         is owned by L2 (PARTITION), so L1 cannot wire the workflow that emits the
         required status check.

D-1. The exact required-status-check context string.
     §11.3 lists "contract validation" in prose. Branch protection needs a literal
     context string, identical in the branch-protection template, in the workflow
     job name, and in the reconciliation comparison set (§53.1 "Branch protection
     template vs actual branch protection").
     L0 has published the literal string in `contracts/workflow-io/required-contexts.tsv`.

D-2. Which lane writes the workflow that runs `python -m validators.registry.cli`, and at
     what path. L2 owns `.github/workflows/**`. L1 supplies the frozen invocation
     contract of §1.7 and nothing else.
     L0 to route to L2 with the invocation contract attached.

D-3. The pinned Python version and dependency-pinning policy for control-plane
     tooling. L1 pins `validators/registry/requirements.txt` for its own engine;
     the CI runner's interpreter version is a cross-lane fact L2 must match.
     This lane assumes Python >= 3.11 and will not proceed past L1-04-08 on a
     runner below it.
     NOTE: No reissue needed — `>= 3.11` is satisfied by 3.12 (FD-005). Do NOT add a `== 3.12` pin here; that lives in L1-03.

NOT DECIDABLE BY L1. Do not guess. Do not create a workflow file.
```

---

## 5. Tasks

---

### L1-04-01 — Freeze the engine contract and pin the toolchain

**Size:** S **Depends on:** — (phase entry)

**Creates**

* `C:/…/control-plane/validators/registry/README.md`
* `C:/…/control-plane/validators/registry/requirements.txt`
* `C:/…/control-plane/validators/registry/gate_lib/__init__.py`

*(All paths below are repository-relative and executed from `$CONTROL_PLANE_ROOT`.)*

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git checkout integration && git pull --ff-only
git checkout -b lane/1/04-engine-contract

mkdir -p validators/registry/gate_lib

cat > validators/registry/requirements.txt <<'EOF'
# L1 registry gate engine - pinned toolchain. Lane 1 owns this file.
PyYAML==6.0.2
jsonschema==4.23.0
EOF

cat > validators/registry/gate_lib/__init__.py <<'EOF'
"""Support modules for the L1 registry gate engine (Lane 1, phase 4)."""
EOF

cat > validators/registry/README.md <<'EOF'
# Registry gate engine (Lane 1, Subsystem B)

Runs every rule under `rules/` against the control-plane tree and decides the merge.
This directory is owned exclusively by Lane 1. `validators/drift/**` is Lane 3 and is
never discovered, imported or executed from here.

## Invocation

    python -m validators.registry.cli --root . --as-of $(date +%Y-%m-%d) --records-root . --format json

Run from the repository root. The job that runs it carries no `if:` condition and no
path filter: a skipped job reports a conclusion branch protection counts as satisfied
(spec Section 33.2), so "no work was needed" is an explicit recorded success.

## Exit codes

| Code | Name | Meaning |
|---|---|---|
| 0 | GATE PASS | rules ran, canary found, no red/blocking finding |
| 1 | GATE VIOLATION | a red or blocking finding against the live tree |
| 2 | GATE ENGINE ERROR | a rule crashed, timed out, or emitted malformed output |
| 3 | GATE CANARY FAILURE | the instrument stopped discriminating (see below) |

Precedence: 2 > 1 > 0. Every non-zero code blocks the merge.
Amber and Green findings are reported but never change the exit code
(spec Section 53.4: only Blocking blocks work).

## The negative-test discipline

Spec Section 53.1 and AT-102: a run that reports zero findings, the canary included,
is a FAILED run - it proves the instrument stopped looking, not that nothing drifted.
D97 applies the same rule to verification contracts. Here it applies to validators:

1. Every rule directory MUST contain at least one `fixtures/must-fail/<case>/`.
   The engine breaks a known-good baseline with the case's `overlay/`, runs the rule,
   and requires exit 1 plus a FINDING matching `expect.txt`. A must-fail fixture that
   passes is exit code 3.
2. `registries/canary/seeded-canary.yaml` is the permanent seeded mismatch. The rule
   `gate-selftest-canary` reports it as an amber finding on every live run. A live run
   in which that rule reports nothing is exit code 3, never a clean run.

## Writing a rule

`rules/<rule-id>/rule.yaml` must validate against
`schemas/registry/gate-rule.v1.schema.json`. `rules/<rule-id>/check.py` must:

* accept `--root <target-root>`;
* print findings on stdout and NOTHING else, one per line, exactly
  `FINDING <rule-id> <severity> <path>:<line> <message>`;
* exit 0 with no findings, exit 1 with findings, and never any other code;
* report unparseable input inside its own `applies_to` scope as a FINDING rather than
  crashing or staying silent. The universal negative-test recipe depends on this.

## Report file

Written only when `--report <path>` is passed. The engine never writes inside the
repository by default: repository-root paths belong to L0.
EOF

git add validators/registry/README.md validators/registry/requirements.txt validators/registry/gate_lib/__init__.py
git commit -m "L1-04-01: freeze registry gate engine contract and pin toolchain"
```

Then file the L0 decision request:

```bash
set -euo pipefail
gh issue create \
  --title "DECISION REQUIRED L0: required-check string, workflow ownership, Python pin (L1-04)" \
  --label "decision-required,lane-0" \
  --body "See implementation/lanes/L1-04-ci-gate-engine.md section 4, items D-1, D-2, D-3. L1 cannot write .github/workflows/** and cannot invent the branch-protection context string."
```

```bash
set -euo pipefail
bash -c 'git diff --name-only origin/integration...HEAD | grep -vE "^(schemas/registry/|schemas/product/|registries/|validators/registry/)" && { echo "FOREIGN PATH TOUCHED - STOP"; exit 1; } || echo "LANE-GUARD OK"'
git push -u origin lane/1/04-engine-contract
gh pr create --base integration --title "L1-04-01 engine contract" --body "Freezes the registry gate engine contract (exit codes, rule-author contract, negative-test discipline). No executable code yet."
```

**Acceptance criteria**

1. `test -f validators/registry/README.md` exits `0`.
2. `test -f validators/registry/requirements.txt` exits `0`.
3. `grep -c 'GATE CANARY FAILURE' validators/registry/README.md` prints `1`.
4. `grep -F -q 'validators/drift' validators/registry/README.md` exits `0` (the Lane 3 boundary is written down).
5. `gh issue list --label decision-required --search "L1-04" --json number --jq 'length'` prints a number `>= 1`.
6. Lane-guard prints exactly `LANE-GUARD OK`.

**SELF-VERIFY**

```bash
set -euo pipefail
python3 - <<'PY'
import sys, pathlib
p = pathlib.Path("validators/registry/README.md").read_text(encoding="utf-8")
need = ["GATE PASS","GATE VIOLATION","GATE ENGINE ERROR","GATE CANARY FAILURE",
        "validators/drift","seeded-canary.yaml","FINDING <rule-id>","2 > 1 > 0"]
missing = [n for n in need if n not in p]
print("SELFVERIFY-01", "OK" if not missing else "MISSING " + ",".join(missing))
sys.exit(1 if missing else 0)
PY
```

Correct output: exactly `SELFVERIFY-01 OK`, exit code `0`.

**STOP rule** — If `python3 --version` reports below 3.11, or `validators/registry/` already contains a file named `gate.py` or `README.md` with different content, do **not** overwrite and do **not** proceed. File the blocker (§3.3) with the observed version or the existing file's `git log -1 --oneline -- <path>`.

---

### L1-04-02 — Rule-layout conformance sweep

**Size:** M **Depends on:** L1-04-01

Phases 1–3 wrote validators under `validators/registry/`. The engine discovers rules at exactly one location, `validators/registry/rules/<rule-id>/`. This task moves anything that is not an engine file into that location, mechanically, and stops if the result is not a conforming rule directory. It edits only Lane 1 paths.

**Creates / edits**

* `validators/registry/rules/` (new directory; `git mv` of existing rule directories into it)
* `validators/registry/rules/.gitkeep`

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git checkout integration && git pull --ff-only
git checkout -b lane/1/04-rule-layout

mkdir -p validators/registry/rules
touch validators/registry/rules/.gitkeep

# Dry-run: print planned moves and verify no target collision before touching the tree.
echo "=== Planned moves (dry-run) ==="
for d in validators/registry/*/; do
  name="$(basename "$d")"
  case "$name" in
    rules|gate_lib|fixtures|tests|tools) continue ;;
    *)
      echo "  validators/registry/$name  →  validators/registry/rules/$name"
      [ -e "validators/registry/rules/$name" ] && { echo "ERROR: target already exists: validators/registry/rules/$name"; exit 1; }
      ;;
  esac
done
echo "=== Dry-run OK; executing moves ==="

# Move every non-engine directory under validators/registry/ into rules/.
for d in validators/registry/*/; do
  name="$(basename "$d")"
  case "$name" in
    rules|gate_lib|fixtures|tests|tools) continue ;;
    *) git mv "validators/registry/$name" "validators/registry/rules/$name" ;;
  esac
done

# Report any loose file that is not part of the frozen engine layout.
for f in validators/registry/*; do
  base="$(basename "$f")"
  [ -d "$f" ] && continue
  case "$base" in
    README.md|requirements.txt|gate.py|ci-preflight.sh) ;;
    *) echo "STRAY FILE: $base" ;;
  esac
done
```

Now audit every moved directory:

```bash
set -euo pipefail
python3 - <<'PY'
import pathlib, sys
root = pathlib.Path("validators/registry/rules")
bad = []
found = 0
for d in sorted(p for p in root.iterdir() if p.is_dir() and not p.name.startswith(".")):
    found += 1
    if not (d / "check.py").is_file():
        bad.append(f"{d}: no check.py")
    if not (d / "rule.yaml").is_file():
        bad.append(f"{d}: no rule.yaml")
print(f"RULES-FOUND {found}")
for b in bad:
    print("NONCONFORMING", b)
sys.exit(1 if (bad or found == 0) else 0)
PY
```

```bash
set -euo pipefail
git add -A validators/registry
git commit -m "L1-04-02: move registry validators to the frozen rules/ layout"
bash -c 'git diff --name-only origin/integration...HEAD | grep -vE "^(schemas/registry/|schemas/product/|registries/|validators/registry/)" && { echo "FOREIGN PATH TOUCHED - STOP"; exit 1; } || echo "LANE-GUARD OK"'
git push -u origin lane/1/04-rule-layout
gh pr create --base integration --title "L1-04-02 rule layout sweep" --body "Every registry validator now lives at validators/registry/rules/<rule-id>/ with check.py and rule.yaml."
```

**Acceptance criteria**

1. The audit script above exits `0` and prints `RULES-FOUND <N>` with `N >= 1`, and prints **no** `NONCONFORMING` line.
2. The stray-file loop prints nothing.
3. `ls validators/registry | sort | tr '\n' ' '` prints only names drawn from `README.md gate_lib requirements.txt rules`.
4. `test -d validators/drift && git diff --name-only origin/integration...HEAD | grep -c '^validators/drift/'` prints `0` — Lane 3's tree is untouched.
5. Lane-guard prints exactly `LANE-GUARD OK`.

**SELF-VERIFY**

```bash
set -euo pipefail
python3 - <<'PY'
import pathlib, sys
root = pathlib.Path("validators/registry/rules")
dirs = [p for p in root.iterdir() if p.is_dir() and not p.name.startswith(".")]
ok = bool(dirs) and all((d/"check.py").is_file() and (d/"rule.yaml").is_file() for d in dirs)
print("SELFVERIFY-02", "OK" if ok else "FAIL", "rules=", len(dirs))
sys.exit(0 if ok else 1)
PY
```

Correct output: `SELFVERIFY-02 OK rules= <N>` with `N >= 1`, exit `0`.

**STOP rule** — If the audit prints any `NONCONFORMING` line, or `RULES-FOUND 0`, or any `STRAY FILE:` line, do **not** create, rename or hand-author the missing `check.py` / `rule.yaml`, and do **not** delete the directory. This lane does not invent rule semantics it did not write. File the blocker (§3.3) listing every offending path verbatim; route to L0 to reassign to the L1 phase that authored the rule.

---

### L1-04-03 — Rule metadata schema and discovery module

**Size:** M **Depends on:** L1-04-02

**Creates**

* `schemas/registry/gate-rule.v1.schema.json`
* `validators/registry/gate_lib/discovery.py`

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git checkout integration && git pull --ff-only
git checkout -b lane/1/04-discovery
mkdir -p schemas/registry

cat > schemas/registry/gate-rule.v1.schema.json <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  # NEEDS_URN (FD-050): replace with urn:multiproduct:schemas:<type>:<version>
  "$id": "https://control-plane.internal/schemas/registry/gate-rule.v1.schema.json",
  "title": "Registry gate rule metadata (v1)",
  "type": "object",
  "additionalProperties": false,
  "required": ["id", "title", "severity", "spec_ref", "subsystem", "owner_lane", "applies_to"],
  "properties": {
    "id": { "type": "string", "pattern": "^[A-Za-z0-9][A-Za-z0-9._-]{1,63}$" },
    "title": { "type": "string", "minLength": 1 },
    "severity": { "enum": ["green", "amber", "red", "blocking"] },
    "spec_ref": { "type": "string", "minLength": 1 },
    "subsystem": { "enum": ["A", "B"] },
    "owner_lane": { "const": "L1" },
    "applies_to": {
      "type": "array", "minItems": 1,
      "items": { "type": "string", "minLength": 1 }
    },
    "timeout_seconds": { "type": "integer", "minimum": 1, "maximum": 600, "default": 120 }
  }
}
EOF

cat > validators/registry/gate_lib/discovery.py <<'EOF'
"""Rule discovery and layout audit for the L1 registry gate engine.

Lane 1 owns this file. validators/drift/** belongs to Lane 3 and is never
discovered, imported or executed from here.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

RULES_DIRNAME = "rules"
RULE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{1,63}$")
SEVERITIES = ("green", "amber", "red", "blocking")
BLOCKING_SEVERITIES = ("red", "blocking")
ENGINE_ENTRIES = {"rules", "gate_lib", "fixtures", "README.md",
                  "requirements.txt", "gate.py", "ci-preflight.sh", "__pycache__"}
FORBIDDEN_PREFIXES = ("validators/drift",)
SCHEMA_PATH = "schemas/registry/gate-rule.v1.schema.json"


class LayoutError(Exception):
    """Raised for any condition that must map to gate exit code 2."""


def _load_yaml(path: Path):
    import yaml
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _validate_meta(meta, meta_path: Path, repo_root: Path) -> None:
    import jsonschema
    schema_file = repo_root / SCHEMA_PATH
    if not schema_file.is_file():
        raise LayoutError(f"missing rule schema: {schema_file}")
    schema = json.loads(schema_file.read_text(encoding="utf-8"))
    try:
        jsonschema.validate(instance=meta, schema=schema)
    except jsonschema.ValidationError as exc:
        raise LayoutError(f"{meta_path}: rule.yaml fails gate-rule.v1: {exc.message}") from None


def validators_root(repo_root: Path) -> Path:
    return Path(repo_root) / "validators" / "registry"


def audit_layout(repo_root: Path) -> None:
    vroot = validators_root(repo_root)
    if not vroot.is_dir():
        raise LayoutError(f"missing validators root: {vroot}")
    stray = sorted(p.name for p in vroot.iterdir() if p.name not in ENGINE_ENTRIES)
    if stray:
        raise LayoutError("stray entries under validators/registry: " + ", ".join(stray))
    if not (vroot / RULES_DIRNAME).is_dir():
        raise LayoutError(f"missing rules directory: {vroot / RULES_DIRNAME}")


def discover(repo_root: Path):
    """Return a sorted list of rule metadata dicts. Raises LayoutError on any defect."""
    repo_root = Path(repo_root)
    audit_layout(repo_root)
    root = validators_root(repo_root) / RULES_DIRNAME
    rules = []
    for d in sorted(p for p in root.iterdir() if p.is_dir() and not p.name.startswith(".")):
        meta_path = d / "rule.yaml"
        check_path = d / "check.py"
        if not meta_path.is_file():
            raise LayoutError(f"rule directory without rule.yaml: {d}")
        if not check_path.is_file():
            raise LayoutError(f"rule directory without check.py: {d}")
        meta = _load_yaml(meta_path)
        if not isinstance(meta, dict):
            raise LayoutError(f"{meta_path}: rule.yaml is not a mapping")
        _validate_meta(meta, meta_path, repo_root)
        if meta["id"] != d.name:
            raise LayoutError(f"{meta_path}: id {meta['id']!r} != directory name {d.name!r}")
        posix = d.as_posix()
        if any(fp in posix for fp in FORBIDDEN_PREFIXES):
            raise LayoutError(f"rule resolved inside a foreign lane path: {posix}")
        meta["_dir"] = str(d)
        meta["_check"] = str(check_path)
        meta.setdefault("timeout_seconds", 120)
        rules.append(meta)
    return rules


def must_fail_cases(rule) -> list:
    d = Path(rule["_dir"]) / "fixtures" / "must-fail"
    if not d.is_dir():
        return []
    return sorted(p for p in d.iterdir() if p.is_dir() and not p.name.startswith("."))


def pass_cases(rule) -> list:
    d = Path(rule["_dir"]) / "fixtures" / "pass"
    if not d.is_dir():
        return []
    return sorted(p for p in d.iterdir() if p.is_dir() and not p.name.startswith("."))
EOF

python3 -m pip install -r validators/registry/requirements.txt
```

**Verification before commit**

```bash
set -euo pipefail
python3 - <<'PY'
import sys
sys.path.insert(0, "validators/registry")
from gate_lib import discovery
rules = discovery.discover(".")
print("DISCOVERED", len(rules))
for r in rules:
    print("RULE", r["id"], r["severity"], r["subsystem"])
sys.exit(0 if rules else 1)
PY
```

```bash
set -euo pipefail
git add schemas/registry/gate-rule.v1.schema.json validators/registry/gate_lib/discovery.py
git commit -m "L1-04-03: rule metadata schema and discovery module"
bash -c 'git diff --name-only origin/integration...HEAD | grep -vE "^(schemas/registry/|schemas/product/|registries/|validators/registry/)" && { echo "FOREIGN PATH TOUCHED - STOP"; exit 1; } || echo "LANE-GUARD OK"'
git push -u origin lane/1/04-discovery
gh pr create --base integration --title "L1-04-03 rule schema and discovery" --body "gate-rule.v1 schema plus discovery/layout audit. No rule semantics changed."
```

**Acceptance criteria**

1. The verification snippet exits `0` and prints `DISCOVERED <N>` with `N >= 1`.
2. Every printed `RULE` line carries a severity drawn from `green|amber|red|blocking` — the single scale of §53.4.
3. `python3 -c "import json;json.load(open('schemas/registry/gate-rule.v1.schema.json'))"` exits `0`.
4. `grep -c 'validators/drift' validators/registry/gate_lib/discovery.py` prints `2` or more.
5. Lane-guard prints exactly `LANE-GUARD OK`.

**SELF-VERIFY**

```bash
set -euo pipefail
python3 - <<'PY'
import sys, pathlib, tempfile, shutil
sys.path.insert(0, "validators/registry")
from gate_lib import discovery
# 1. live tree discovers rules
live = discovery.discover(".")
# 2. a rule.yaml with a bad severity must raise LayoutError, not pass
tmp = pathlib.Path(tempfile.mkdtemp())
shutil.copytree("schemas", tmp/"schemas")
shutil.copytree("validators", tmp/"validators")
bad = tmp/"validators"/"registry"/"rules"/"zz-selfverify"
bad.mkdir(parents=True)
(bad/"check.py").write_text("", encoding="utf-8")
(bad/"rule.yaml").write_text(
    "id: zz-selfverify\ntitle: t\nseverity: catastrophic\nspec_ref: x\n"
    "subsystem: B\nowner_lane: L1\napplies_to: ['registries/*.yaml']\n", encoding="utf-8")
try:
    discovery.discover(tmp)
    print("SELFVERIFY-03 FAIL bad-severity-accepted"); sys.exit(1)
except discovery.LayoutError:
    pass
finally:
    shutil.rmtree(tmp, ignore_errors=True)
print("SELFVERIFY-03 OK rules=", len(live))
PY
```

Correct output: `SELFVERIFY-03 OK rules= <N>`, exit `0`.

**STOP rule** — If `discover(".")` raises `LayoutError` on the live tree, do **not** edit any `rule.yaml` to make it validate and do **not** loosen `gate-rule.v1.schema.json`. The schema in this document is frozen. File the blocker (§3.3) quoting the exception message verbatim.

---

### L1-04-04 — Finding parser and reporter module

**Size:** M **Depends on:** L1-04-03

**Creates**

* `validators/registry/gate_lib/report.py`

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git checkout integration && git pull --ff-only
git checkout -b lane/1/04-report

cat > validators/registry/gate_lib/report.py <<'EOF'
"""Finding parsing and failure reporting for the L1 registry gate engine.

Output shapes are frozen by implementation/lanes/L1-04-ci-gate-engine.md section 1.5.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

FINDING_RE = re.compile(
    r"^FINDING (?P<rule>\S+) (?P<severity>green|amber|red|blocking) (?P<loc>\S+) (?P<message>.*)$"
)
BLOCKING_SEVERITIES = ("red", "blocking")


class MalformedOutput(Exception):
    """Raised when a rule's stdout violates the rule-author contract (exit code 2)."""


def parse_findings(stdout: str, rule_id: str) -> list:
    findings = []
    for raw in stdout.splitlines():
        line = raw.rstrip()
        if not line:
            continue
        m = FINDING_RE.match(line)
        if not m:
            raise MalformedOutput(f"{rule_id}: stdout line is not a FINDING: {line!r}")
        loc = m.group("loc")
        path, sep, lineno = loc.rpartition(":")
        if not sep or not path or not lineno.isdigit():
            raise MalformedOutput(f"{rule_id}: bad location {loc!r}, expected <path>:<line>")
        findings.append({
            "rule": m.group("rule"),
            "severity": m.group("severity"),
            "file": path,
            "line": int(lineno),
            "message": m.group("message"),
        })
    return findings


def blocking(findings) -> list:
    return [f for f in findings if f["severity"] in BLOCKING_SEVERITIES]


def fail_line(f) -> str:
    return "GATE FAIL {rule} {severity} {file}:{line} {message}".format(**f)


def annotation_line(f) -> str:
    return "::error file={file},line={line},title=GATE FAIL {rule}::{message}".format(**f)


def emit(findings, stream=sys.stderr) -> None:
    annotate = os.environ.get("GITHUB_ACTIONS") == "true"
    for f in findings:
        print(fail_line(f), file=stream)
        if annotate:
            print(annotation_line(f), file=stream)


def result_line(status: str, rules: int, findings: int = 0, reason: str = "",
                canary: str = "found") -> str:
    if status in ("pass", "violation"):
        return f"GATE RESULT {status} rules={rules} findings={findings} canary={canary}"
    return f"GATE RESULT {status} rules={rules} reason={reason}"


def write_report(path, payload) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
EOF

git add validators/registry/gate_lib/report.py
git commit -m "L1-04-04: finding parser and failure reporter"
bash -c 'git diff --name-only origin/integration...HEAD | grep -vE "^(schemas/registry/|schemas/product/|registries/|validators/registry/)" && { echo "FOREIGN PATH TOUCHED - STOP"; exit 1; } || echo "LANE-GUARD OK"'
git push -u origin lane/1/04-report
gh pr create --base integration --title "L1-04-04 finding parser and reporter" --body "Frozen GATE FAIL / GATE RESULT output shapes plus GitHub annotation emission."
```

**Acceptance criteria**

1. The SELF-VERIFY below exits `0`.
2. A stdout line that is not a `FINDING` line raises `MalformedOutput` (proved by SELF-VERIFY case 2). Silent tolerance of junk on stdout is the failure mode this forbids.
3. `report.result_line("pass", 7, 0)` returns exactly `GATE RESULT pass rules=7 findings=0 canary=found`.
4. Lane-guard prints exactly `LANE-GUARD OK`.

**SELF-VERIFY**

```bash
set -euo pipefail
python3 - <<'PY'
import sys, os
sys.path.insert(0, "validators/registry")
from gate_lib import report
ok = True
fs = report.parse_findings("FINDING reg-x blocking registries/people.yaml:12 bad thing\n", "reg-x")
ok &= fs == [{"rule":"reg-x","severity":"blocking","file":"registries/people.yaml","line":12,"message":"bad thing"}]
ok &= report.fail_line(fs[0]) == "GATE FAIL reg-x blocking registries/people.yaml:12 bad thing"
ok &= report.annotation_line(fs[0]) == "::error file=registries/people.yaml,line=12,title=GATE FAIL reg-x::bad thing"
ok &= report.result_line("pass", 7, 0) == "GATE RESULT pass rules=7 findings=0 canary=found"
ok &= report.result_line("canary-failure", 7, reason="must-fail-passed") == "GATE RESULT canary-failure rules=7 reason=must-fail-passed"
ok &= len(report.blocking(report.parse_findings("FINDING r amber a:0 m\n", "r"))) == 0
try:
    report.parse_findings("hello world\n", "r"); ok = False
except report.MalformedOutput:
    pass
print("SELFVERIFY-04", "OK" if ok else "FAIL")
sys.exit(0 if ok else 1)
PY
```

Correct output: exactly `SELFVERIFY-04 OK`, exit `0`.

**STOP rule** — If any assertion fails, do **not** relax `FINDING_RE` and do **not** change the frozen output strings of §1.5 to make the test pass; L2's workflow, the annotation surface and the reconciliation comparison set all read these strings. File the blocker (§3.3) with the failing assertion.

---

### L1-04-05 — The `gate.py` runner: live mode and exit codes

**Size:** L **Depends on:** L1-04-04

**Creates**

* `validators/registry/gate.py`

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git checkout integration && git pull --ff-only
git checkout -b lane/1/04-runner

cat > validators/registry/gate.py <<'PY'
#!/usr/bin/env python3
"""L1 registry gate engine (Subsystem B).

Exit codes are frozen by implementation/lanes/L1-04-ci-gate-engine.md section 1.4:
  0 GATE PASS   1 GATE VIOLATION   2 GATE ENGINE ERROR   3 GATE CANARY FAILURE
Precedence: 2 > 1 > 0.

Lane 1 owns this file. validators/drift/** is Lane 3 and is never touched here.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from gate_lib import discovery, report  # noqa: E402

EXIT_PASS = 0
EXIT_VIOLATION = 1
EXIT_ENGINE_ERROR = 2
EXIT_CANARY = 3

CANARY_RULE_ID = "gate-selftest-canary"


def run_rule(rule, target_root):
    """Execute one rule. Returns (findings, error_message_or_None)."""
    cmd = [sys.executable, rule["_check"], "--root", str(target_root)]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=rule.get("timeout_seconds", 120))
    except subprocess.TimeoutExpired:
        return [], f"{rule['id']}: timed out after {rule.get('timeout_seconds', 120)}s"
    if proc.returncode not in (0, 1):
        tail = (proc.stderr or "").strip().splitlines()[-1:] or [""]
        return [], f"{rule['id']}: illegal exit code {proc.returncode}: {tail[0]}"
    try:
        findings = report.parse_findings(proc.stdout, rule["id"])
    except report.MalformedOutput as exc:
        return [], str(exc)
    if proc.returncode == 1 and not findings:
        return [], f"{rule['id']}: exit 1 with no FINDING on stdout"
    if proc.returncode == 0 and findings:
        return [], f"{rule['id']}: exit 0 with {len(findings)} FINDING line(s)"
    foreign = [f for f in findings if f["rule"] != rule["id"]]
    if foreign:
        return [], f"{rule['id']}: emitted a finding for another rule id {foreign[0]['rule']!r}"
    return findings, None


def materialise(baseline: Path, overlay: Path, dest: Path) -> None:
    """Copy baseline into dest, then apply overlay. `X.DELETE` removes X."""
    shutil.copytree(baseline, dest, dirs_exist_ok=True)
    if overlay.is_dir():
        shutil.copytree(overlay, dest, dirs_exist_ok=True)
    for marker in sorted(dest.rglob("*.DELETE")):
        victim = marker.with_suffix("")
        if victim.is_dir():
            shutil.rmtree(victim, ignore_errors=True)
        elif victim.exists():
            victim.unlink()
        marker.unlink()


def run_fixtures(rules, baseline: Path, results: dict) -> int:
    """Returns the worst exit code produced by the fixture pass."""
    worst = EXIT_PASS
    for rule in rules:
        cases = discovery.must_fail_cases(rule)
        if not cases:
            results["canary_failures"].append(
                f"{rule['id']}: no must-fail fixture (spec 53.1 / AT-102: an instrument that cannot fail is not an instrument)")
            worst = EXIT_CANARY
            continue
        for case in cases:
            expect_file = case / "expect.txt"
            if not expect_file.is_file():
                results["engine_errors"].append(f"{rule['id']}/{case.name}: missing expect.txt")
                worst = max(worst, EXIT_ENGINE_ERROR)
                continue
            expect = ""
            for line in expect_file.read_text(encoding="utf-8").splitlines():
                if line.strip() and not line.lstrip().startswith("#"):
                    expect = line.strip()
                    break
            if not expect:
                results["engine_errors"].append(f"{rule['id']}/{case.name}: empty expect.txt")
                worst = max(worst, EXIT_ENGINE_ERROR)
                continue
            with tempfile.TemporaryDirectory() as tmp:
                dest = Path(tmp) / "tree"
                materialise(baseline, case / "overlay", dest)
                findings, err = run_rule(rule, dest)
            if err:
                results["engine_errors"].append(f"must-fail {rule['id']}/{case.name}: {err}")
                worst = max(worst, EXIT_ENGINE_ERROR)
                continue
            if not findings:
                results["canary_failures"].append(
                    f"{rule['id']}/{case.name}: MUST-FAIL fixture PASSED - the rule stopped discriminating")
                worst = EXIT_CANARY
                continue
            if not any(expect in report.fail_line(f) for f in findings):
                results["canary_failures"].append(
                    f"{rule['id']}/{case.name}: no finding matched expect.txt {expect!r}")
                worst = EXIT_CANARY
                continue
            results["must_fail_ok"] += 1
        # Optional positive cases, plus the implicit bare-baseline positive case.
        cases_pass = list(discovery.pass_cases(rule)) + [None]
        for case in cases_pass:
            with tempfile.TemporaryDirectory() as tmp:
                dest = Path(tmp) / "tree"
                overlay = (case / "overlay") if case is not None else Path(tmp) / "none"
                materialise(baseline, overlay, dest)
                findings, err = run_rule(rule, dest)
            name = case.name if case is not None else "baseline"
            if err:
                results["engine_errors"].append(f"pass {rule['id']}/{name}: {err}")
                worst = max(worst, EXIT_ENGINE_ERROR)
                continue
            bad = report.blocking(findings)
            if bad:
                results["engine_errors"].append(
                    f"pass {rule['id']}/{name}: rule reported {len(bad)} red/blocking finding(s) on a known-good tree")
                worst = max(worst, EXIT_ENGINE_ERROR)
                continue
            results["pass_ok"] += 1
    return worst


def run_live(rules, root: Path, results: dict) -> int:
    worst = EXIT_PASS
    canary_hits = 0
    for rule in rules:
        findings, err = run_rule(rule, root)
        if err:
            results["engine_errors"].append(f"live {err}")
            worst = max(worst, EXIT_ENGINE_ERROR)
            continue
        results["findings"].extend(findings)
        if rule["id"] == CANARY_RULE_ID:
            canary_hits += len(findings)
    if any(r["id"] == CANARY_RULE_ID for r in rules):
        results["canary_hits"] = canary_hits
        if canary_hits == 0:
            results["canary_failures"].append(
                "live run found the seeded canary zero times - a run reporting zero findings, "
                "the canary included, is a FAILED run (spec 53.1, AT-102)")
            return EXIT_CANARY
    else:
        results["canary_failures"].append(
            f"rule {CANARY_RULE_ID} is not present - the live seeded canary is missing (spec 53.1)")
        return EXIT_CANARY
    if report.blocking(results["findings"]):
        worst = max(worst, EXIT_VIOLATION)
    return worst


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="L1 registry gate engine")
    ap.add_argument("--root", default=".", help="repository root to validate")
    ap.add_argument("--mode", choices=("live", "fixtures", "all"), default="all")
    ap.add_argument("--report", default=None, help="write a JSON report to this path")
    ap.add_argument("--list-rules", action="store_true",
                    help="print the live rule ids, one per line, and exit 0")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    started = time.time()
    results = {"findings": [], "engine_errors": [], "canary_failures": [],
               "must_fail_ok": 0, "pass_ok": 0, "canary_hits": 0}

    try:
        rules = discovery.discover(root)
    except discovery.LayoutError as exc:
        print(report.result_line("engine-error", 0, reason=str(exc)), file=sys.stderr)
        return EXIT_ENGINE_ERROR

    if args.list_rules:
        for r in rules:
            print(f"{r['id']}\t{r['severity']}\t{r['spec_ref']}")
        return EXIT_PASS

    if not rules:
        print(report.result_line("canary-failure", 0, reason="zero-rules-discovered"), file=sys.stderr)
        return EXIT_CANARY

    baseline = discovery.validators_root(root) / "fixtures" / "baseline"
    code = EXIT_PASS
    if args.mode in ("fixtures", "all"):
        if not baseline.is_dir():
            print(report.result_line("engine-error", len(rules), reason="missing-baseline-fixture"),
                  file=sys.stderr)
            return EXIT_ENGINE_ERROR
        code = max(code, run_fixtures(rules, baseline, results))
        if results["canary_failures"]:
            code = EXIT_CANARY
    if args.mode in ("live", "all"):
        live_code = run_live(rules, root, results)
        code = EXIT_CANARY if (live_code == EXIT_CANARY or results["canary_failures"]) else max(code, live_code)

    report.emit(results["findings"])
    for e in results["engine_errors"]:
        print(f"GATE ENGINE ERROR {e}", file=sys.stderr)
    for c in results["canary_failures"]:
        print(f"GATE CANARY FAILURE {c}", file=sys.stderr)

    status = {EXIT_PASS: "pass", EXIT_VIOLATION: "violation",
              EXIT_ENGINE_ERROR: "engine-error", EXIT_CANARY: "canary-failure"}[code]
    reason = ""
    if code == EXIT_CANARY:
        reason = (results["canary_failures"] or ["unknown"])[0].split(":")[0]
    elif code == EXIT_ENGINE_ERROR:
        reason = (results["engine_errors"] or ["unknown"])[0].split(":")[0]
    print(report.result_line(status, len(rules), len(report.blocking(results["findings"])),
                             reason=reason), file=sys.stderr)

    if args.report:
        report.write_report(args.report, {
            "status": status,
            "exit_code": code,
            "rules_discovered": len(rules),
            "rule_ids": [r["id"] for r in rules],
            "must_fail_cases_passed": results["must_fail_ok"],
            "pass_cases_passed": results["pass_ok"],
            "canary_hits": results["canary_hits"],
            "findings": results["findings"],
            "engine_errors": results["engine_errors"],
            "canary_failures": results["canary_failures"],
            "duration_seconds": round(time.time() - started, 3),
        })
    return code


if __name__ == "__main__":
    sys.exit(main())
PY

chmod +x validators/registry/gate.py
git add validators/registry/gate.py
git commit -m "L1-04-05: gate.py runner with frozen exit-code semantics"
```

**Verification before opening the pull request** — at this point `fixtures/baseline/` and the canary rule do not yet exist, so the runner must report those conditions honestly rather than pass:

```bash
set -euo pipefail
python -m validators.registry.cli --root . --as-of $(date +%Y-%m-%d) --records-root . --format json; echo "EXIT=$?"
python -m validators.registry.cli --root . --as-of $(date +%Y-%m-%d) --records-root . --format json; echo "EXIT=$?"
```

Expected: the first command prints a `GATE RESULT engine-error … reason=missing-baseline-fixture` or a `GATE RESULT canary-failure …` line and `EXIT=2` or `EXIT=3` — **never `EXIT=0`**. The second prints one tab-separated line per rule and `EXIT=0`.

```bash
set -euo pipefail
bash -c 'git diff --name-only origin/integration...HEAD | grep -vE "^(schemas/registry/|schemas/product/|registries/|validators/registry/)" && { echo "FOREIGN PATH TOUCHED - STOP"; exit 1; } || echo "LANE-GUARD OK"'
git push -u origin lane/1/04-runner
gh pr create --base integration --title "L1-04-05 gate runner" --body "Runner with frozen exit codes 0/1/2/3. Fails closed until the baseline fixture and the seeded canary land in L1-04-06."
```

**Acceptance criteria**

1. `python -m validators.registry.cli --root . --as-of $(date +%Y-%m-%d) --records-root . --format json; echo EXIT=$?` prints a non-zero `EXIT=`. A green gate before the canary exists would itself be the failure this phase forbids.
2. `python -m validators.registry.cli --root . --as-of $(date +%Y-%m-%d) --records-root . --format json | wc -l` prints a number `>= 1`.
3. `grep -c 'validators/drift' validators/registry/gate.py` prints `1` or more, and `grep -c "'drift'" validators/registry/gate.py` shows no import of any drift module: `python3 -c "import ast,sys;src=open('validators/registry/gate.py').read();print('DRIFT-IMPORTS', sum(1 for n in ast.walk(ast.parse(src)) if isinstance(n,(ast.Import,ast.ImportFrom)) and 'drift' in ast.dump(n)))"` prints `DRIFT-IMPORTS 0`.
4. SELF-VERIFY below exits `0`.
5. Lane-guard prints exactly `LANE-GUARD OK`.

**SELF-VERIFY**

```bash
set -euo pipefail
python3 - <<'PY'
import subprocess, sys
def run(args):
    p = subprocess.run([sys.executable, "-m", "validators.registry.cli"] + ["--root", ".", "--as-of", __import__("datetime").date.today().isoformat(), "--records-root", ".", "--format", "json"] + args,
                       capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr
rc, out, err = run(["--root", ".", "--mode", "all"])
ok = rc in (2, 3) and "GATE RESULT" in err
rc2, out2, _ = run(["--root", ".", "--list-rules"])
ok &= rc2 == 0 and len([l for l in out2.splitlines() if l.strip()]) >= 1
print("SELFVERIFY-05", "OK" if ok else "FAIL", "gate_exit=", rc, "list_exit=", rc2)
sys.exit(0 if ok else 1)
PY
```

Correct output: `SELFVERIFY-05 OK gate_exit= 2` (or `3`) `list_exit= 0`, exit `0`.

**STOP rule** — If the gate exits `0` at this point, do **not** commit and do **not** proceed: the runner is reporting a clean run with no baseline and no canary, which is exactly the vacuous-run failure of EC-109 / AT-102. File the blocker (§3.3) quoting the full stderr.

---

### L1-04-06 — Baseline fixture, seeded canary, fixtures mode

**Size:** M **Depends on:** L1-04-05

**Creates**

* `validators/registry/fixtures/baseline/registries/**`, `validators/registry/fixtures/baseline/schemas/**`
* `registries/canary/seeded-canary.yaml`
* `validators/registry/rules/gate-selftest-canary/rule.yaml`
* `validators/registry/rules/gate-selftest-canary/check.py`
* `validators/registry/rules/gate-selftest-canary/fixtures/must-fail/canary-removed/overlay/registries/canary/seeded-canary.yaml.DELETE`
* `validators/registry/rules/gate-selftest-canary/fixtures/must-fail/canary-removed/expect.txt`

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git checkout integration && git pull --ff-only
git checkout -b lane/1/04-canary

# 1. The permanently seeded, clearly labelled canary record (spec 53.1).
mkdir -p registries/canary
cat > registries/canary/seeded-canary.yaml <<'EOF'
# SEEDED CANARY - DO NOT REMOVE, DO NOT "FIX".
# This file is the deliberately planted, clearly labelled mismatch required by
# spec Section 53.1 and acceptance test AT-102 (decision D63). Every gate run MUST
# report it. A run that reports zero findings, this canary included, is a FAILED
# run - it proves the instrument stopped looking, not that nothing drifted.
# Removing or renaming this file makes the control-plane gate fail with exit code 3.
seeded_canary:
  id: gate-selftest-canary-001
  purpose: negative test of the registry gate engine
  spec_ref: "Section 53.1 seeded-canary rule; AT-102; D63"
  expected_finding: "seeded canary present"
  severity: amber
  owner_lane: L1
EOF

# 2. The canary rule.
mkdir -p validators/registry/rules/gate-selftest-canary/fixtures/must-fail/canary-removed/overlay/registries/canary

cat > validators/registry/rules/gate-selftest-canary/rule.yaml <<'EOF'
id: gate-selftest-canary
title: The seeded canary record is present and is reported on every run
severity: amber
spec_ref: "Section 53.1 seeded-canary rule; AT-102; D63"
subsystem: B
owner_lane: L1
applies_to:
  - "registries/canary/seeded-canary.yaml"
timeout_seconds: 30
EOF

cat > validators/registry/rules/gate-selftest-canary/check.py <<'PY'
#!/usr/bin/env python3
"""Seeded-canary rule. Reports the planted mismatch on every run (spec 53.1, AT-102).

Reports an amber FINDING when the canary is present - Amber does not block work
(spec 53.4), but its presence in every run proves discovery, execution, parsing and
reporting are all still working. Reports a blocking FINDING when it is missing or
unparseable, because a removed canary is a disarmed instrument.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

RULE_ID = "gate-selftest-canary"
TARGET = "registries/canary/seeded-canary.yaml"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    args = ap.parse_args()
    path = Path(args.root) / TARGET
    if not path.is_file():
        print(f"FINDING {RULE_ID} blocking {TARGET}:0 seeded canary record is missing - "
              f"the gate cannot prove it is still looking (spec 53.1, AT-102)")
        return 1
    try:
        import yaml
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:  # unparseable input in scope must be a FINDING, never a crash
        print(f"FINDING {RULE_ID} blocking {TARGET}:0 seeded canary record is unparseable: "
              f"{type(exc).__name__}")
        return 1
    if not isinstance(data, dict) or "seeded_canary" not in data:
        print(f"FINDING {RULE_ID} blocking {TARGET}:0 seeded canary record has no "
              f"seeded_canary block")
        return 1
    cid = data["seeded_canary"].get("id", "unknown")
    print(f"FINDING {RULE_ID} amber {TARGET}:0 seeded canary {cid} present and reported "
          f"(spec 53.1, AT-102)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
PY

# 3. Its must-fail fixture: delete the canary from the baseline.
touch "validators/registry/rules/gate-selftest-canary/fixtures/must-fail/canary-removed/overlay/registries/canary/seeded-canary.yaml.DELETE"
cat > validators/registry/rules/gate-selftest-canary/fixtures/must-fail/canary-removed/expect.txt <<'EOF'
# Substring that a FINDING line from this rule must contain.
seeded canary record is missing
EOF

# 4. The shared, known-good baseline tree.
mkdir -p validators/registry/fixtures/baseline
cp -a registries validators/registry/fixtures/baseline/registries
cp -a schemas    validators/registry/fixtures/baseline/schemas
find validators/registry/fixtures/baseline -name '__pycache__' -type d -prune -exec rm -rf {} +
```

Now prove the whole discipline works:

```bash
set -euo pipefail
python -m validators.registry.cli --root . --as-of $(date +%Y-%m-%d) --records-root . --format json; echo "FIXTURES_EXIT=$?"
python -m validators.registry.cli --root . --as-of $(date +%Y-%m-%d) --records-root . --format json; echo "LIVE_EXIT=$?"
```

Prove the canary actually canaries — temporarily hide it and confirm exit `3`:

```bash
set -euo pipefail
mv registries/canary/seeded-canary.yaml /tmp/seeded-canary.yaml
python -m validators.registry.cli --root . --as-of $(date +%Y-%m-%d) --records-root . --format json; echo "NO_CANARY_EXIT=$?"   # expect 1 or 2, never 0
mv /tmp/seeded-canary.yaml registries/canary/seeded-canary.yaml
```

```bash
set -euo pipefail
git add registries/canary validators/registry/rules/gate-selftest-canary validators/registry/fixtures
git commit -m "L1-04-06: seeded canary, canary rule, shared baseline fixture"
bash -c 'git diff --name-only origin/integration...HEAD | grep -vE "^(schemas/registry/|schemas/product/|registries/|validators/registry/)" && { echo "FOREIGN PATH TOUCHED - STOP"; exit 1; } || echo "LANE-GUARD OK"'
git push -u origin lane/1/04-canary
gh pr create --base integration --title "L1-04-06 seeded canary and fixtures mode" --body "Adds the permanent seeded canary of spec 53.1 / AT-102, its rule, its must-fail fixture, and the shared baseline tree."
```

**Acceptance criteria**

1. `python -m validators.registry.cli --root . --as-of $(date +%Y-%m-%d) --records-root . --format json` exits `0` **or** `2` (input error). It must never exit `1` without findings.
2. The temporary-removal check prints `NO_CANARY_EXIT=1` or `NO_CANARY_EXIT=3`, never `0`.
3. `python -m validators.registry.cli --root . --as-of $(date +%Y-%m-%d) --records-root . --format json > /tmp/r.json 2>&1; python3 -c "import json;d=json.load(open('/tmp/r.json'));print('CANARY_HITS', d['canary_hits'])"` prints `CANARY_HITS 1`.
4. `git status --porcelain registries/canary` is empty after the removal check — the canary file is back, byte-identical.
5. No rule other than `gate-selftest-canary` reports a `red` or `blocking` finding against `registries/canary/**`.
6. Lane-guard prints exactly `LANE-GUARD OK`.

**SELF-VERIFY**

```bash
set -euo pipefail
python3 - <<'PY'
import json, subprocess, sys, os, shutil, tempfile
rep = os.path.join(tempfile.gettempdir(), "gate-selfverify-06.json")
p = subprocess.run([sys.executable, "validators/registry/gate.py", "--root", ".",
                    "--mode", "live", "--report", rep], capture_output=True, text=True)
d = json.load(open(rep))
canary_ok = d["canary_hits"] >= 1
no_engine_error = not d["engine_errors"]
scoped = all(not (f["file"].startswith("registries/canary/") and f["severity"] in ("red","blocking"))
             for f in d["findings"])
ok = canary_ok and no_engine_error and scoped
print("SELFVERIFY-06", "OK" if ok else "FAIL",
      "canary_hits=", d["canary_hits"], "engine_errors=", len(d["engine_errors"]),
      "exit=", p.returncode)
sys.exit(0 if ok else 1)
PY
```

Correct output: `SELFVERIFY-06 OK canary_hits= 1 engine_errors= 0 exit= <0 or 3>`, exit `0`.

**STOP rule** — If another rule reports a `red` or `blocking` finding against `registries/canary/**`, do **not** edit that rule's `applies_to` and do **not** move the canary out of `registries/`. §53.1 requires the canary to sit *inside the comparison set*; a canary parked outside it proves nothing. File the blocker (§3.3) naming the rule id and its finding line, routed to L0 to decide the exclusion glob. Likewise, if `--mode live` exits `2`, stop — an engine error here means a rule breaks on a real tree.

---

### L1-04-07 — Must-fail fixture backfill for every rule

**Size:** L **Depends on:** L1-04-06

Every rule must carry at least one must-fail fixture. This task applies the **universal recipe** of §1.6 and nothing else: overwrite the first file the rule's `applies_to` matches in the baseline with the literal `INVALID: [`, and expect the rule's own id in the resulting finding. This requires no knowledge of what any rule checks.

**Creates** — for each rule id `<R>` that has no must-fail fixture:

* `validators/registry/rules/<R>/fixtures/must-fail/unparseable-target/overlay/<first-matched-path>`
* `validators/registry/rules/<R>/fixtures/must-fail/unparseable-target/expect.txt`

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git checkout integration && git pull --ff-only
git checkout -b lane/1/04-negative-fixtures

python3 - <<'PY'
import sys, pathlib, glob
sys.path.insert(0, "validators/registry")
from gate_lib import discovery

repo = pathlib.Path(".").resolve()
baseline = repo / "validators/registry/fixtures/baseline"
made, skipped, unmatched = [], [], []

for rule in discovery.discover(repo):
    rdir = pathlib.Path(rule["_dir"])
    if discovery.must_fail_cases(rule):
        skipped.append(rule["id"]); continue
    target = None
    for pattern in rule["applies_to"]:
        hits = sorted(baseline.glob(pattern))
        hits = [h for h in hits if h.is_file()]
        if hits:
            target = hits[0].relative_to(baseline)
            break
    if target is None:
        unmatched.append(f"{rule['id']}: applies_to matched no file in the baseline tree")
        continue
    case = rdir / "fixtures" / "must-fail" / "unparseable-target"
    dest = case / "overlay" / target
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text("INVALID: [\n", encoding="utf-8")
    (case / "expect.txt").write_text(
        "# Universal negative-test recipe (see L1-04 section 1.6).\n"
        "# The rule-author contract requires unparseable input in scope to be a FINDING.\n"
        f"GATE FAIL {rule['id']}\n", encoding="utf-8")
    made.append(f"{rule['id']} -> {target}")

for m in made: print("CREATED", m)
for s in skipped: print("ALREADY-HAS-FIXTURE", s)
for u in unmatched: print("UNMATCHED", u)
print("SUMMARY created=%d skipped=%d unmatched=%d" % (len(made), len(skipped), len(unmatched)))
sys.exit(1 if unmatched else 0)
PY
```

```bash
set -euo pipefail
python -m validators.registry.cli --root . --as-of $(date +%Y-%m-%d) --records-root . --format json > /tmp/gate-07.json; echo "GATE_EXIT=$?"
python3 -c "import json;d=json.load(open('/tmp/gate-07.json'));print('MUSTFAIL_OK',d['must_fail_cases_passed'],'RULES',d['rules_discovered'],'CANARY_FAILS',len(d['canary_failures']))"
```

```bash
set -euo pipefail
git add validators/registry/rules
git commit -m "L1-04-07: must-fail fixture for every registry rule (spec 53.1 / AT-102 discipline)"
bash -c 'git diff --name-only origin/integration...HEAD | grep -vE "^(schemas/registry/|schemas/product/|registries/|validators/registry/)" && { echo "FOREIGN PATH TOUCHED - STOP"; exit 1; } || echo "LANE-GUARD OK"'
git push -u origin lane/1/04-negative-fixtures
gh pr create --base integration --title "L1-04-07 negative-test fixtures for every rule" --body "Every rule now carries a fixture it MUST fail. A must-fail fixture that passes is gate exit code 3."
```

**Acceptance criteria**

1. The backfill script prints `SUMMARY created=<a> skipped=<b> unmatched=0` and exits `0`.
2. `python -m validators.registry.cli --root . --as-of $(date +%Y-%m-%d) --records-root . --format json; echo GATE_EXIT=$?` prints `GATE_EXIT=0`.
3. The report line prints `CANARY_FAILS 0`, and `MUSTFAIL_OK` equals the total number of must-fail cases across all rules — verified by criterion 4.
4. Every rule has ≥1 must-fail case: the SELF-VERIFY below exits `0`.
5. Lane-guard prints exactly `LANE-GUARD OK`.

**SELF-VERIFY**

```bash
set -euo pipefail
python3 - <<'PY'
import sys, subprocess, json, os, tempfile, pathlib
sys.path.insert(0, "validators/registry")
from gate_lib import discovery
rules = discovery.discover(".")
missing = [r["id"] for r in rules if not discovery.must_fail_cases(r)]
total_cases = sum(len(discovery.must_fail_cases(r)) for r in rules)
rep = os.path.join(tempfile.gettempdir(), "gate-selfverify-07.json")
p = subprocess.run([sys.executable, "validators/registry/gate.py", "--root", ".",
                    "--mode", "all", "--report", rep], capture_output=True, text=True)
d = json.load(open(rep))
ok = (not missing) and p.returncode == 0 and d["must_fail_cases_passed"] == total_cases \
     and not d["canary_failures"] and not d["engine_errors"]
print("SELFVERIFY-07", "OK" if ok else "FAIL",
      "rules=", len(rules), "must_fail_cases=", total_cases,
      "verified=", d["must_fail_cases_passed"], "exit=", p.returncode,
      "missing=", ",".join(missing) or "none")
sys.exit(0 if ok else 1)
PY
```

Correct output: `SELFVERIFY-07 OK rules= <N> must_fail_cases= <M> verified= <M> exit= 0 missing= none`, exit `0`.

**STOP rule** — Three distinct STOPs, all of which forbid the same tempting shortcut:

* If the script prints any `UNMATCHED` line, do **not** edit that rule's `applies_to` to make a glob hit. File the blocker (§3.3) naming the rule and its globs.
* If the gate exits `3` with `MUST-FAIL fixture PASSED`, the rule does not report unparseable input in its own scope and therefore violates the rule-author contract of §1.3. Do **not** delete the fixture, do **not** weaken `expect.txt`, and do **not** mark the rule exempt. File the blocker (§3.3) quoting the canary-failure line; route to L0 to reassign to the phase that authored that rule.
* If the gate exits `1` because a real `red`/`blocking` finding exists against the live registries, do **not** edit `registries/**` content to silence it in this task. File the blocker (§3.3) with the `GATE FAIL` line verbatim.

---

### L1-04-08 — Preflight script and the L2 handoff package

**Size:** M **Depends on:** L1-04-07

The gate must be runnable identically by a human before pushing and by the CI job L2 will write. This task ships one entry point for both, and the README section L2 consumes.

**Creates / edits**

* `validators/registry/ci-preflight.sh` (new)
* `validators/registry/README.md` (edit: append the CI-integration section)

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git checkout integration && git pull --ff-only
git checkout -b lane/1/04-preflight

cat > validators/registry/ci-preflight.sh <<'EOF'
#!/usr/bin/env bash
# L1 registry gate - single entry point for CI and for local pre-push checks.
# Owned by Lane 1. Callers: the L2-owned workflow job, and humans before pushing.
#
# Usage:  bash validators/registry/ci-preflight.sh [<repo-root>] [<report-path>]
#
# Exit codes are the gate's own, unmodified:
#   0 pass | 1 fail | 2 input error
# This script never swallows a non-zero code and never runs the gate behind an
# `if:` guard: spec Section 33.2 forbids a required check that can be skipped.
set -uo pipefail

ROOT="${1:-.}"
REPORT="${2:-${RUNNER_TEMP:-${TMPDIR:-/tmp}}/registry-gate-report.json}"

python3 -m pip install --quiet --disable-pip-version-check \
  -r "${ROOT}/validators/registry/requirements.txt" || exit 2

python -m validators.registry.cli \
  --root "${ROOT}" --as-of $(date +%Y-%m-%d) --records-root "${ROOT}" --format json
CODE=$?

echo "REGISTRY-GATE-EXIT=${CODE}"
echo "REGISTRY-GATE-REPORT=${REPORT}"
exit "${CODE}"
EOF

chmod +x validators/registry/ci-preflight.sh

cat >> validators/registry/README.md <<'EOF'

## CI integration (contract handed to Lane 2)

Lane 1 owns `validators/registry/**`. `.github/workflows/**` is owned by Lane 2, so
this lane ships the entry point and not the workflow.

The job that runs the gate:

* runs `bash validators/registry/ci-preflight.sh . "$RUNNER_TEMP/registry-gate-report.json"`
  from the repository root;
* carries **no `if:` condition and no path filter** - a job skipped by an `if:`
  reports a conclusion branch protection counts as satisfied, and a workflow skipped
  by a path filter never reports at all (spec Section 33.2). "No registry changed"
  is an explicit recorded success, never a skip;
* triggers on `pull_request` and on `push` to `integration` and `main`;
* propagates the script's exit code unchanged as the job conclusion;
* uploads the JSON report as a build artifact.

The literal branch-protection context string is an L0 decision (L1-04 section 4,
item D-1) and is not invented here.

## Enumerating the live checks

    python -m validators.registry.cli --root . --as-of $(date +%Y-%m-%d) --records-root . --format json

Prints `<rule-id>\t<severity>\t<spec_ref>`, one line per live rule, exit 0. Spec
Section 101 requires control-plane CI to fail when an invariant classified
`mechanical` names no live check; this is the authoritative list of the registry
checks that exist.

## Drift validators are not here

`validators/drift/**` implements the reconciliation comparison set of spec
Section 53.1 and is owned by Lane 3. This engine never discovers, imports or
executes anything under it.
EOF

bash validators/registry/ci-preflight.sh . /tmp/gate-08.json; echo "PREFLIGHT_EXIT=$?"
```

```bash
set -euo pipefail
git add validators/registry/ci-preflight.sh validators/registry/README.md
git commit -m "L1-04-08: ci-preflight entry point and Lane 2 handoff contract"
bash -c 'git diff --name-only origin/integration...HEAD | grep -vE "^(schemas/registry/|schemas/product/|registries/|validators/registry/)" && { echo "FOREIGN PATH TOUCHED - STOP"; exit 1; } || echo "LANE-GUARD OK"'
git push -u origin lane/1/04-preflight
gh pr create --base integration --title "L1-04-08 CI preflight entry point" --body "Single entry point for the L2 workflow and for local pre-push runs. Exit code propagated unchanged."
```

**Acceptance criteria**

1. `bash validators/registry/ci-preflight.sh . /tmp/gate-08.json; echo EXIT=$?` prints `REGISTRY-GATE-EXIT=0`, `REGISTRY-GATE-REPORT=/tmp/gate-08.json` and `EXIT=0`.
2. The script propagates non-zero unchanged, proved by SELF-VERIFY case 2.
3. `grep -c 'no .if:. condition and no path filter' validators/registry/README.md` prints `1`.
4. `grep -c 'validators/drift' validators/registry/README.md` prints `2` or more.
5. `git ls-files --error-unmatch .github/workflows 2>/dev/null; echo RC=$?` prints `RC=1` from this branch's diff — i.e. `git diff --name-only origin/integration...HEAD | grep -c '^\.github/'` prints `0`.
6. Lane-guard prints exactly `LANE-GUARD OK`.

**SELF-VERIFY**

```bash
set -euo pipefail
python3 - <<'PY'
import subprocess, sys, os, shutil, tempfile
# case 1: green run through the preflight entry point
p = subprocess.run(["bash", "validators/registry/ci-preflight.sh", ".",
                    os.path.join(tempfile.gettempdir(), "sv08.json")],
                   capture_output=True, text=True)
ok = p.returncode == 0 and "REGISTRY-GATE-EXIT=0" in p.stdout
# case 2: exit code propagation - run against a copy with the canary removed
tmp = tempfile.mkdtemp()
tree = os.path.join(tmp, "repo")
shutil.copytree(".", tree, ignore=shutil.ignore_patterns(".git", "__pycache__"))
os.remove(os.path.join(tree, "registries", "canary", "seeded-canary.yaml"))
q = subprocess.run(["bash", "validators/registry/ci-preflight.sh", tree,
                    os.path.join(tmp, "sv08b.json")], capture_output=True, text=True)
ok &= q.returncode != 0 and f"REGISTRY-GATE-EXIT={q.returncode}" in q.stdout
shutil.rmtree(tmp, ignore_errors=True)
print("SELFVERIFY-08", "OK" if ok else "FAIL", "green_exit=", p.returncode,
      "broken_exit=", q.returncode)
sys.exit(0 if ok else 1)
PY
```

Correct output: `SELFVERIFY-08 OK green_exit= 0 broken_exit= <1 or 2>`, exit `0`.

**STOP rule** — If the preflight script's exit code differs from the gate's exit code in any case, or if fulfilling this task would require creating or editing any file under `.github/`, stop immediately. `.github/workflows/**` belongs to Lane 2 and creating it here fails the lane-guard check with no exceptions (PARTITION rule 1). File the blocker (§3.3) and reference decision item D-2.

---

### L1-04-09 — Phase exit gate

**Size:** S **Depends on:** L1-04-08

**Creates** — nothing. This task only proves the phase and records the result on the phase pull request.

**Commands**

```bash
set -euo pipefail
cd "$CONTROL_PLANE_ROOT"
git checkout integration && git pull --ff-only

# 1. Full gate, all modes, from a clean tree.
python -m validators.registry.cli --root . --as-of $(date +%Y-%m-%d) --records-root . --format json > /tmp/phase4.json
echo "PHASE4_EXIT=$?"

# 2. Every negative-test guarantee, proved rather than asserted.
python3 - <<'PY'
import json, subprocess, sys, os, shutil, tempfile
d = json.load(open("/tmp/phase4.json"))
checks = {
  "rules_discovered>=1":      d["rules_discovered"] >= 1,
  "canary_hits>=1":           d["canary_hits"] >= 1,
  "no_canary_failures":       not d["canary_failures"],
  "no_engine_errors":         not d["engine_errors"],
  "no_blocking_findings":     not [f for f in d["findings"] if f["severity"] in ("red","blocking")],
  "must_fail_cases_verified": d["must_fail_cases_passed"] >= d["rules_discovered"],
  "status_pass":              d["status"] == "pass",
}
for k, v in checks.items():
    print(("PASS " if v else "FAIL ") + k)
sys.exit(0 if all(checks.values()) else 1)
PY

# 3. The instrument is provably breakable: removing the canary must NOT pass.
python3 - <<'PY'
import subprocess, sys, os, shutil, tempfile
tmp = tempfile.mkdtemp(); tree = os.path.join(tmp, "repo")
shutil.copytree(".", tree, ignore=shutil.ignore_patterns(".git", "__pycache__"))
os.remove(os.path.join(tree, "registries", "canary", "seeded-canary.yaml"))
p = subprocess.run([sys.executable, "-m", "validators.registry.cli", "--root", tree, "--as-of", __import__("datetime").date.today().isoformat(), "--records-root", tree, "--format", "json"],
                   capture_output=True, text=True)
shutil.rmtree(tmp, ignore_errors=True)
print("CANARY-REMOVED-EXIT", p.returncode)
sys.exit(0 if p.returncode != 0 else 1)
PY

# 4. Lane 3's tree was never touched by this phase.
git log --name-only --pretty=format: origin/integration~0..HEAD -- validators/drift | grep -c . || echo "DRIFT-UNTOUCHED"
```

Record the result on the phase tracking issue:

```bash
set -euo pipefail
gh issue comment "$L1_PHASE4_ISSUE" --body "$(cat <<'EOF'
L1 PHASE 4 EXIT GATE

gate.py --mode all: PASS (exit 0)
rules discovered: <N>
must-fail cases verified: <M>
seeded canary hits: 1
canary-removed control run: non-zero (instrument provably breakable)
validators/drift/**: untouched (Lane 3)
.github/**: untouched (Lane 2)

Open L0 decisions consumed by Lane 2 before the required check can be armed:
D-1 required-status-check context string (contracts/workflow-io/required-contexts.tsv); D-2 workflow ownership and path;
D-3 pinned Python version.
EOF
)"
```

**Acceptance criteria**

1. Step 1 prints `PHASE4_EXIT=0`.
2. Step 2 prints seven `PASS` lines and zero `FAIL` lines, exit `0`.
3. Step 3 prints `CANARY-REMOVED-EXIT` with a non-zero number, exit `0`. A phase whose gate cannot be made to fail has not passed (§53.1, AT-102).
4. Step 4 prints `DRIFT-UNTOUCHED`.
5. `git diff --name-only origin/main...origin/integration | grep -c '^\.github/'` prints `0` for commits authored by this phase.

**SELF-VERIFY**

```bash
set -euo pipefail
python3 - <<'PY'
import json, subprocess, sys, os, shutil, tempfile
rep = os.path.join(tempfile.gettempdir(), "phase4-selfverify.json")
p = subprocess.run([sys.executable, "validators/registry/gate.py", "--root", ".",
                    "--mode", "all", "--report", rep], capture_output=True, text=True)
d = json.load(open(rep))
tmp = tempfile.mkdtemp(); tree = os.path.join(tmp, "repo")
shutil.copytree(".", tree, ignore=shutil.ignore_patterns(".git", "__pycache__"))
os.remove(os.path.join(tree, "registries", "canary", "seeded-canary.yaml"))
q = subprocess.run([sys.executable, "-m", "validators.registry.cli", "--root", tree, "--as-of", __import__("datetime").date.today().isoformat(), "--records-root", tree, "--format", "json"],
                   capture_output=True, text=True)
shutil.rmtree(tmp, ignore_errors=True)
ok = (p.returncode == 0 and d["status"] == "pass" and d["canary_hits"] >= 1
      and not d["canary_failures"] and not d["engine_errors"] and q.returncode != 0)
print("SELFVERIFY-09", "OK" if ok else "FAIL",
      "green=", p.returncode, "broken=", q.returncode,
      "rules=", d["rules_discovered"], "mustfail=", d["must_fail_cases_passed"])
sys.exit(0 if ok else 1)
PY
```

Correct output: `SELFVERIFY-09 OK green= 0 broken= <1 or 2> rules= <N> mustfail= <M>`, exit `0`.

**STOP rule** — If step 3 prints `CANARY-REMOVED-EXIT 0`, the gate passes a tree with the canary deleted. Do **not** declare the phase complete, do **not** merge, and do **not** "fix" it by editing the fixture. This is exactly EC-109 — a silently-vacuous run — and AT-102 classifies it as a failed run. File the blocker (§3.3) with title `BLOCKER L1-04 T-09: gate passes with the seeded canary removed`, and mark every downstream lane that consumes L1 output as blocked, because the merge train runs L1 first.

---

## 6. Phase completion definition

The phase is complete when all nine tasks are merged to `integration` and, from a clean checkout of `integration`:

| # | Proof | Command | Expected |
|---|---|---|---|
| 1 | The gate runs and passes | `python -m validators.registry.cli --root . --as-of $(date +%Y-%m-%d) --records-root . --format json; echo $?` | `0` |
| 2 | The gate can fail | remove `registries/canary/seeded-canary.yaml` in a copy, rerun | non-zero |
| 3 | Every rule has a must-fail fixture | SELF-VERIFY of L1-04-07 | `SELFVERIFY-07 OK … missing= none` |
| 4 | Live checks are enumerable | `python -m validators.registry.cli --root . --as-of $(date +%Y-%m-%d) --records-root . --format json | wc -l` | `>= 2` |
| 5 | One entry point for CI and humans | `bash validators/registry/ci-preflight.sh .; echo $?` | `REGISTRY-GATE-EXIT=0`, `0` |
| 6 | Lane boundaries intact | `git diff --name-only origin/main...origin/integration \| grep -cE '^(\.github/|validators/drift/|contracts/|docs/)'` | `0` for this phase's commits |

**What is deliberately not done here, and who does it**

| Not done | Owner | Reference |
|---|---|---|
| The workflow that emits the required status check | L2 | §4 D-2 |
| The literal branch-protection context string, and adding it to the branch-protection template | L0 | §4 D-1, spec §11.3 |
| The reconciler's `control-plane/blocking-drift` check | L3 | spec §53.2, D92 |
| Drift validators comparing declared versus actual GitHub state | L3 | spec §53.1, `validators/drift/**` |
| Records and events written from gate runs | L4 | PARTITION, spec §97 |
