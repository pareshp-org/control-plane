<!-- Task IDs renamed to charter format L5-FF-TT by Session 12 (FD-037 corollary) -->
> **[AUTHORITATIVE — FD-B1-L5 2026-09-02]**
> This is the authoritative task plan for Lane 5. All competing plans are superseded.

# L5-01 — GitHub Organisation and Access Model (Phase 1)

**Lane:** L5 — Access, Infra and Ops (subsystems K, L, M, Q, R of spec §99.2)
**Phase:** 1 (spec §98.2, "Phase 1 — Foundation (Week 1)")
**Spec sections implemented here:** §11, §11.1, §11.2, §11.3, §11.4; the access subset of the §98.2 Phase 1 completion check; §95.2 bootstrap arming pattern; §33.4 deployment branch and tag policy; decisions **D101**, **D73**, **D53**, **D89**, **D106**; signal **SIG-03**; invariants **#9**, **#79**, **#87**; acceptance tests **AT-108**/**AT-110** are named where this file produces their preconditions only.
**Repository:** `control-plane`.
**Paths this file writes:** `access/**` only.

---

## 0. Scope, boundaries and reading order

### 0.1 What this file is

A task list. Each task is executable by a low-cost AI developer with no repository context and no judgment authority. Every task states its exact file paths, its literal commands in order, acceptance criteria each provable by one command with unambiguous output, a SELF-VERIFY block with the expected output printed literally, a STOP rule, a size and its dependencies by task id.

### 0.2 Path ownership — non-negotiable

`Code/implementation/PARTITION.md` is FROZEN. L5 owns `access/**`, `infra/**`, `ops-vm/**`, `notify/**`, `assets/**`. **This file writes only `access/**`.** The other four L5 path roots belong to other L5 phase files and are out of scope here.

The following paths are **forbidden** to every task in this file. A task that appears to need one has hit a STOP condition:

| Forbidden path | Owner | Why a task might mistakenly reach for it |
|---|---|---|
| `CODEOWNERS` (repository root) | L0 | This file builds the CODEOWNERS **generator** and its output for *product* repositories. It never writes the control-plane repository's own root `CODEOWNERS`. |
| `contracts/**` | L0, frozen at Phase 0 | A lane needing a contract change files a Contract Change Request; it never edits `contracts/**` (PARTITION rule 2). |
| `registries/**`, `schemas/registry/**`, `schemas/product/**` | L1 | The CODEOWNERS generator consumes registry-derived data as a **JSON input document supplied on the command line**, never by reading `registries/**` (PARTITION rule 4). |
| `.github/workflows/**` | L2 | This file declares required-status-check *policy*. The workflows that emit those check contexts are L2's. |
| `reconciler/**`, `tools/provision/**`, `validators/drift/**` | L3 | This file declares the access state the reconciler compares against and the provisioning applies. It contains no reconciler or provisioner code. |
| `control-plane-records` repository, `schemas/records/**` | L4 | Append-only enforcement on the records repository (D107) is declared by the lane that owns that repository. This file cites D107 and configures nothing there. |
| `docs/**`, `Makefile`, root files | L0 | — |

### 0.3 The cross-lane interface this file exposes

Two artifacts leave `access/**` for other lanes to consume, and both are consumed as **published artifacts**, never by reaching into this lane's source tree (PARTITION rule 4):

1. **`access/codeowners/generate_codeowners.py`** — invoked with a JSON input document path. The document shape is fixed by `access/schemas/codeowners-input.schema.json` (task **L5-01-06**). L3 provisioning constructs that document from the registries and calls the generator.
2. **`access/tools/render_protection_payload.py`** — turns `access/branch-protection/branch-protection.yaml` plus a profile name into the literal GitHub branch-protection API payload. L3 provisioning and the L5 apply runbooks both call it.

If either shape conflicts with something `contracts/**` already publishes, that is a STOP condition and a Contract Change Request, not an edit.

### 0.4 The three facts this phase exists to make mechanical

1. **A Read-only approval does not satisfy branch protection (§11.1).** A Cross-Reviewer holding only Read can open a pull request, comment, and submit a review that visually reads as an approval — and the merge stays blocked. Therefore **Cross-Reviewers require Write**, and least privilege is preserved by branch protection, not by withholding Write.
2. **The plan-tier posture is settled (§11.4, D73).** Branch protection or rulesets on private repositories require the Team plan; this is non-negotiable and is the one item that forces a paid plan. Environment deployment protection rules — required reviewers, wait timers — are an Enterprise feature on private repositories and are **not depended on**. The production-approval mechanism of record is the §27.2 workflow-identity gate.
3. **Gates arm in an order that can be satisfied (D101).** Teams grant Write **before** branch protection is armed. Arming a Code-Owner-and-approval gate while no Team grants Write leaves nobody whose approval counts, and §95.4 names the result exactly: a team that experiences its merges mysteriously breaking.

### 0.5 Reading order for the executor

Read §0.6 (conventions), §0.7 (blocker protocol), then execute tasks **L5-01-01 → L5-01-15 in order**. Do not skip. Do not reorder. Every task depends on the ones listed in its `Depends on` row and on nothing else.

### 0.6 Conventions binding on every task

| Rule | Value |
|---|---|
| Shell | Git Bash (POSIX `sh`). Every fenced `bash` block is copy-pasteable as written. |
| Working directory | The root of the `control-plane` working copy. Every task begins by setting it. |
| Branch naming | `lane/5/p1-<task-suffix>` — one branch per task, short-lived, rebased on `integration` before PR (PARTITION §"Branch & merge model"). |
| Merge target | `integration`. L5 never merges to `main`. L5 never merges or rebases another lane's branch. |
| Python | `python3` on PATH, 3.12 exact (FD-005). Dependencies pinned in `access/tools/requirements.txt`. |
| Repository names | **Never hard-coded.** §11 binds: "Repositories are enumerated dynamically from the product registry. No workflow, dashboard or script contains a hard-coded list of repository names." Apply scripts enumerate with `gh api --paginate`. Configuration files carry policy, never repository lists. |
| Organisation login | Never committed. Supplied at apply time in `$ORG_LOGIN`. |
| Additive-only | Prefer new files over editing existing ones (PARTITION rule 5). |
| Commit trailer | Every commit in this lane ends with `Lane: L5` on its own line. |

### 0.7 Blocker protocol

Task **L5-01-01** creates `access/tools/blocker.sh`. Its body is the blocker-issue template, reproduced here so it is readable before it exists:

```
title: BLOCKER <TASK_ID>: <one line>
labels: blocker, lane-5
body:
  task_id:               <e.g. L5-01-07>
  lane:                  L5
  plan_file:             Code/implementation/lanes/L5-01-org-and-access.md
  trigger:               <the STOP condition that fired, copied verbatim from the task>
  command_run:           <the exact command>
  observed_output:       <the exact output, unedited>
  expected_output:       <the expected output, copied from the task's SELF-VERIFY block>
  blocked_because:       <one sentence of fact; propose no design>
  requires_decision_from: L0 integrator
```

Every STOP rule in this file is discharged by running:

```bash
set -euo pipefail
bash access/tools/blocker.sh <TASK_ID> "<one-line title>" "<trigger>" "<command_run>" "<observed_output>" "<expected_output>" "<blocked_because>"
```

**A STOP is absolute.** Do not work around it, do not substitute a value, do not proceed to the next task. File the blocker and stop.

### 0.8 Task index

| Task | Title | Size | Depends on |
|---|---|---|---|
| L5-01-01 | Lane skeleton, preflight and blocker helper | S | — |
| L5-01-02 | Access-config schema harness and validator | M | T01 |
| L5-01-03 | `organisation.yaml` — single org, base Read, enforced 2FA | M | T02 |
| L5-01-04 | `permission-semantics.yaml` — the §11.1 verified table, machine-checked | M | T02 |
| L5-01-05 | `teams.yaml` — Teams derived from registries, the §11.2 person-class table | M | T04 |
| L5-01-06 | Human-only CODEOWNERS generator with executed negative tests | L | T05 |
| L5-01-07 | `branch-protection.yaml` — the full §11.3 checklist, unarmed/armed profiles, payload renderer | L | T04 |
| L5-01-08 | `deployment-policies.yaml` — §33.4 deployment branch and tag policy | M | T07 |
| L5-01-09 | `plan-tier.yaml` — the §11.4 table with a depended-on checker | M | T07 |
| L5-01-10 | D101 arming order and the arming-order gate | L | T05, T06, T07 |
| L5-01-11 | Owner continuity and break-glass escrow declaration | S | T03 |
| L5-01-12 | Apply runbooks — dry-run by default, `gh` commands in arming order | L | T03, T05, T07, T08, T10 |
| L5-01-13 | Phase 1 access completion check — offline assertions plus the negative-test register | M | T03–T11 |
| L5-01-14 | Per-repository transition note template and generator (§95.4) | S | T12 |
| L5-01-15 | Lane integration PR | S | T13, T14 |

---

## L5-01-01 — Lane skeleton, preflight and blocker helper

| Field | Value |
|---|---|
| Size | S |
| Depends on | — |
| Writes | `access/README.md`, `access/tools/requirements.txt`, `access/tools/blocker.sh`, `access/.gitkeep` files |
| Spec | PARTITION §"The five build lanes"; §11 |

**Commands**

```bash
set -e
cd "$(git rev-parse --show-toplevel)"
export CONTROL_PLANE_ROOT="$PWD"
echo "CONTROL_PLANE_ROOT=$CONTROL_PLANE_ROOT"
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/5/p1-skeleton
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
python --version
python3 -c "import sys; sys.exit(0 if sys.version_info[:2] == (3, 12) else 1)" \
  || { echo "STOP: Python 3.12 required (FD-005); got $(python3 --version 2>&1)"; exit 1; }
echo "PREFLIGHT python OK"
command -v gh >/dev/null && echo "PREFLIGHT gh OK" || echo "PREFLIGHT gh FAIL"
command -v git >/dev/null && echo "PREFLIGHT git OK" || echo "PREFLIGHT git FAIL"
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
mkdir -p access/model access/codeowners \
         access/branch-protection access/environments access/plan-tier \
         access/arming access/runbooks access/checks access/schemas \
         access/tools access/testdata/codeowners access/testdata/arming
for d in access/model access/codeowners \
         access/branch-protection access/environments access/plan-tier \
         access/arming access/runbooks access/checks access/schemas \
         access/tools access/testdata/codeowners access/testdata/arming; do
  touch "$d/.gitkeep"
done
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/tools/requirements.txt <<'EOF'
# Pinned. access/** tooling only. Do not add a dependency without a Contract
# Change Request; §101 invariant 85 pins tooling, and an unpinned validator is
# a validator whose behaviour is not declared state.
PyYAML==6.0.2
jsonschema==4.23.0
EOF
python -m pip install --user -r access/tools/requirements.txt
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/tools/blocker.sh <<'EOF'
#!/usr/bin/env bash
# Blocker-issue template for lane L5, plan file
# Code/implementation/lanes/L5-01-org-and-access.md.
# Usage:
#   bash access/tools/blocker.sh TASK_ID TITLE TRIGGER COMMAND OBSERVED EXPECTED REASON
# A STOP rule is absolute: file the blocker and stop. Do not work around it.
set -eu
if [ "$#" -ne 7 ]; then
  echo "usage: blocker.sh TASK_ID TITLE TRIGGER COMMAND OBSERVED EXPECTED REASON" >&2
  exit 64
fi
TASK_ID="$1"; TITLE="$2"; TRIGGER="$3"; CMD="$4"; OBS="$5"; EXP="$6"; WHY="$7"
BODY="task_id:                ${TASK_ID}
lane:                   L5
plan_file:              Code/implementation/lanes/L5-01-org-and-access.md
trigger:                ${TRIGGER}
command_run:            ${CMD}
observed_output:        ${OBS}
expected_output:        ${EXP}
blocked_because:        ${WHY}
requires_decision_from: L0 integrator"
if command -v gh >/dev/null 2>&1; then
  gh issue create --title "BLOCKER ${TASK_ID}: ${TITLE}" \
                  --label blocker --label lane-5 --body "${BODY}"
else
  mkdir -p access/checks/blockers
  OUT="access/checks/blockers/${TASK_ID}.blocker.txt"
  printf 'BLOCKER %s: %s\n%s\n' "${TASK_ID}" "${TITLE}" "${BODY}" > "${OUT}"
  echo "gh unavailable; blocker written to ${OUT}" >&2
fi
echo "BLOCKER FILED ${TASK_ID}"
EOF
chmod +x access/tools/blocker.sh
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/README.md <<'EOF'
# `access/` — the access-control architecture (subsystem L, spec §99.2)

Owned exclusively by lane **L5** (`Code/implementation/PARTITION.md`, FROZEN).
No other lane writes any path under `access/`.

## What lives here

| Directory | Holds | Spec |
|---|---|---|
| `model/` | Permission model, person-class → Team → Write derivation; organisation-level declared state (base Read, 2FA, Owner continuity); the §11.1 verified permission-semantics table; Teams derivation rules | §11, §11.1, §11.2 |
| `codeowners/` | The human-only CODEOWNERS generator and its machine-identity denylist | §11.3, D53 |
| `branch-protection/` | The §11.3 branch-protection checklist as declared state, with the unarmed and armed profiles of §95.2 | §11.3, §95.2 |
| `environments/` | The deployment branch and tag policy for every environment | §33.4 |
| `plan-tier/` | The §11.4 plan-tier facts and the checker that proves nothing depends on an Enterprise-only feature | §11.4, D73 |
| `arming/` | The D101 arming order and the gate that refuses an unsatisfiable arming | D101, §98.2 |
| `runbooks/` | The `gh` apply runbooks. Dry-run by default; `--apply` requires credentials no build agent holds | §98.2 |
| `checks/` | The Phase 1 access completion check and the negative-test register | §98.2 |
| `schemas/` | One JSON Schema per configuration document. Each declares `x-target` | — |
| `tools/` | Validators, renderers and the blocker helper | — |
| `testdata/` | Fixtures. Never applied to a real organisation | — |

## Binding rules for anything added here

1. **No repository names.** §11: repositories are enumerated dynamically from the
   product registry; no script contains a hard-coded list of repository names.
2. **No organisation login.** Supplied at apply time in `$ORG_LOGIN`.
3. **No secrets, no tokens, no API keys.** §101 invariant 84.
4. **Every YAML document under `access/` (outside `testdata/`) has a schema in
   `access/schemas/` declaring it as `x-target`.** `access/tools/validate_access_config.py`
   fails on any document that does not.
5. **Read-only approval never satisfies branch protection.** §11.1. Any document
   here that implies otherwise is wrong.
EOF
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
git add access
git commit -m "$(printf 'L5-01-01: access/ skeleton, pinned tooling deps, blocker helper\n\nLane: L5\n')"
git push -u origin lane/5/p1-skeleton
```

### Acceptance criteria

| # | Criterion | Proving command | Expected output |
|---|---|---|---|
| A1 | Python 3.12 exact present | `python3 -c "import sys;print('OK' if sys.version_info[:2]==(3,12) else 'FAIL')"` | `OK` |
| A2 | Pinned deps installed and importable | `python -c "import yaml, jsonschema; print('OK')"` | `OK` |
| A3 | `gh` present | `command -v gh >/dev/null && echo OK \|\| echo FAIL` | `OK` |
| A4 | All twelve `access/` directories exist | `ls -d access/*/ access/testdata/*/ \| wc -l \| tr -d ' '` | `12` |
| A5 | Blocker helper is executable and self-documents | `bash access/tools/blocker.sh 2>&1 \| head -1` | `usage: blocker.sh TASK_ID TITLE TRIGGER COMMAND OBSERVED EXPECTED REASON` |
| A6 | No path outside `access/` was touched | `git diff --name-only origin/integration...HEAD \| grep -cv '^access/' \| tr -d ' '` | `0` |
| A7 | Branch name conforms | `git rev-parse --abbrev-ref HEAD` | `lane/5/p1-skeleton` |

### SELF-VERIFY

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
python3 -c "import sys;print('A1 ' + ('OK' if sys.version_info[:2]==(3,12) else 'FAIL'))"
python -c "import yaml, jsonschema; print('A2 OK')"
{ command -v gh >/dev/null && echo "A3 OK"; } || echo "A3 FAIL"
echo "A4 $(ls -d access/*/ access/testdata/*/ | wc -l | tr -d ' ')"   # expected: 12
echo "A5 $(bash access/tools/blocker.sh 2>&1 | head -1)"
echo "A6 $(git diff --name-only origin/integration...HEAD | grep -cv '^access/' | tr -d ' ')"
echo "A7 $(git rev-parse --abbrev-ref HEAD)"
```

Expected output, exactly:

```
A1 OK
A2 OK
A3 OK
A4 12
A5 usage: blocker.sh TASK_ID TITLE TRIGGER COMMAND OBSERVED EXPECTED REASON
A6 0
A7 lane/5/p1-skeleton
```

### STOP

Stop and file a blocker if any of the following is true.

- `A1` prints `FAIL` — Python is not exactly 3.12 (FD-005).
- `A2` raises `ModuleNotFoundError` and `python -m pip install --user -r access/tools/requirements.txt` fails a second time.
- `A3` prints `FAIL` — `gh` is absent. Every apply runbook in this file depends on it.
- `A6` prints anything other than `0` — a file outside `access/` was staged. Do not `git rm` your way out of it; the lane-guard check exists because a lane touching a foreign path is a partition violation.
- The branch `lane/5/p1-skeleton` already exists on `origin` with commits you did not author.

```bash
set -euo pipefail
bash access/tools/blocker.sh L5-01-01 "preflight failed" "<paste the failing criterion line, e.g. A3 FAIL>" "<the command you ran>" "<its exact output>" "<the expected line from the SELF-VERIFY block>" "<one sentence of fact>"
```

---

## L5-01-02 — Access-config schema harness and validator

| Field | Value |
|---|---|
| Size | M |
| Depends on | L5-01-01 |
| Writes | `access/tools/validate_access_config.py`, `access/schemas/README.md` |
| Spec | PARTITION rule 3 (no shared mutable file); §101 invariant 87 |

Every configuration document added by tasks T03–T13 is validated by this one tool. There is **no shared index file**: each schema declares the document it governs in an `x-target` key, so adding a document means adding a file, never editing a list. That is PARTITION rule 3 applied inside the lane.

**Commands**

```bash
set -e
cd "$(git rev-parse --show-toplevel)"
export CONTROL_PLANE_ROOT="$PWD"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/5/p1-schema-harness
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/tools/validate_access_config.py <<'PYEOF'
#!/usr/bin/env python
"""Validate every access/** configuration document against its JSON Schema.

Discovery rule, binding: every access/schemas/*.schema.json declares "x-target",
the repository-relative path of the single YAML document it governs. There is no
shared index; adding a document means adding a schema file. Any YAML document
under access/ that no schema targets is a FAILURE, not an omission -- an
unvalidated access declaration is declared state nothing checks.

Exit 0 on success, 1 on any failure.
"""
import glob
import json
import os
import sys

import yaml
from jsonschema import Draft202012Validator

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SCHEMA_GLOB = os.path.join(ROOT, "access", "schemas", "*.schema.json")
CONFIG_GLOB = os.path.join(ROOT, "access", "**", "*.yaml")
EXCLUDED = (os.path.join(ROOT, "access", "testdata") + os.sep,)


def rel(path):
    return os.path.relpath(path, ROOT).replace(os.sep, "/")


def main():
    failures = []
    targets = set()
    schemas = sorted(glob.glob(SCHEMA_GLOB))
    if not schemas:
        print("FAIL no schema files found under access/schemas/")
        print("ACCESS CONFIG VALIDATION FAILED (1)")
        return 1
    for schema_path in schemas:
        try:
            with open(schema_path, "r", encoding="utf-8") as handle:
                schema = json.load(handle)
        except ValueError as exc:
            failures.append("%s is not valid JSON: %s" % (rel(schema_path), exc))
            continue
        target = schema.get("x-target")
        if not target:
            failures.append("%s declares no x-target" % rel(schema_path))
            continue
        target_abs = os.path.abspath(os.path.join(ROOT, target.replace("/", os.sep)))
        targets.add(target_abs)
        if not os.path.exists(target_abs):
            failures.append("%s targets a missing document: %s" % (rel(schema_path), target))
            continue
        with open(target_abs, "r", encoding="utf-8") as handle:
            document = yaml.safe_load(handle)
        errors = sorted(
            Draft202012Validator(schema).iter_errors(document),
            key=lambda err: list(err.path),
        )
        if errors:
            for err in errors:
                where = "/".join(str(part) for part in err.path) or "(root)"
                failures.append("%s: %s at %s" % (target, err.message, where))
        else:
            print("PASS schema %s" % target)
    for config_path in sorted(glob.glob(CONFIG_GLOB, recursive=True)):
        config_abs = os.path.abspath(config_path)
        if config_abs.startswith(EXCLUDED):
            continue
        if config_abs not in targets:
            failures.append("unschemad access document: %s" % rel(config_abs))
    if failures:
        for failure in failures:
            print("FAIL %s" % failure)
        print("ACCESS CONFIG VALIDATION FAILED (%d)" % len(failures))
        return 1
    print("ACCESS CONFIG VALIDATION PASSED (%d documents)" % len(targets))
    return 0


if __name__ == "__main__":
    sys.exit(main())
PYEOF
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/schemas/README.md <<'EOF'
# `access/schemas/`

One JSON Schema per configuration document under `access/`.

**Every schema MUST declare `x-target`** — the repository-relative path of the
single YAML document it governs. `access/tools/validate_access_config.py`
discovers documents through `x-target` and through nothing else. There is no
index file, because a shared mutable index is exactly what PARTITION rule 3
forbids: directory-per-item only.

A YAML document under `access/` that no schema targets fails validation. That is
deliberate. An access declaration nothing validates is declared state nothing
checks, and §101 invariant 87 requires every security policy to be enforced by
the platform wherever the platform can enforce it.

`access/testdata/` is excluded from the unschemad-document check; fixtures are
inputs to tests, not declared state.

Schemas are Draft 2020-12. Every schema sets `"additionalProperties": false` at
every object level, so a typo in a key is a failure rather than a silently
ignored line.
EOF
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
python access/tools/validate_access_config.py; echo "exit=$?"
```

At this point the tool has no schemas and **must** report failure. That is the intended first observation: the harness proves it fails before any task proves it passes.

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
git add access
git commit -m "$(printf 'L5-01-02: access-config schema harness and validator\n\nLane: L5\n')"
git push -u origin lane/5/p1-schema-harness
```

### Acceptance criteria

| # | Criterion | Proving command | Expected output |
|---|---|---|---|
| B1 | Validator parses and runs | `python -c "import ast,sys;ast.parse(open('access/tools/validate_access_config.py').read());print('OK')"` | `OK` |
| B2 | With zero schemas the validator FAILS (negative test) | `python access/tools/validate_access_config.py \| tail -1` | `ACCESS CONFIG VALIDATION FAILED (1)` |
| B3 | Its exit code is non-zero | `python access/tools/validate_access_config.py >/dev/null; echo $?` | `1` |
| B4 | Discovery is by `x-target`, with no index file | `grep -c 'x-target' access/tools/validate_access_config.py` | `3` |
| B5 | `testdata` is excluded | `grep -c 'testdata' access/tools/validate_access_config.py` | `1` |
| B6 | No path outside `access/` touched | `git diff --name-only origin/integration...HEAD \| grep -cv '^access/' \| tr -d ' '` | `0` |

### SELF-VERIFY

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
echo "B1 $(python -c "import ast;ast.parse(open('access/tools/validate_access_config.py').read());print('OK')")"
echo "B2 $(python access/tools/validate_access_config.py | tail -1)"
ec=0; python access/tools/validate_access_config.py >/dev/null 2>&1 || ec=$?; echo "B3 $ec"
echo "B4 $(grep -c 'x-target' access/tools/validate_access_config.py)"
echo "B5 $(grep -c 'testdata' access/tools/validate_access_config.py)"
echo "B6 $(git diff --name-only origin/integration...HEAD | grep -cv '^access/' | tr -d ' ')"
```

Expected output, exactly:

```
B1 OK
B2 ACCESS CONFIG VALIDATION FAILED (1)
B3 1
B4 3
B5 1
B6 0
```

### STOP

Stop and file a blocker if any of the following is true.

- `B2` prints `ACCESS CONFIG VALIDATION PASSED (...)`. A validator that passes with zero schemas will pass with zero enforcement, and every later task's evidence is worthless.
- `B3` prints `0`.
- `import jsonschema` raises. Re-run the install from T01 once; if it fails again, stop.
- The validator crashes with a traceback rather than printing a `FAIL` line.

```bash
set -euo pipefail
bash access/tools/blocker.sh L5-01-02 "schema harness does not fail closed" "<the failing criterion line>" "python access/tools/validate_access_config.py" "<its exact output>" "ACCESS CONFIG VALIDATION FAILED (1)" "<one sentence of fact>"
```

---

## L5-01-03 — `organisation.yaml` — single org, base Read, enforced 2FA

| Field | Value |
|---|---|
| Size | M |
| Depends on | L5-01-02 |
| Writes | `access/model/organisation.yaml`, `access/schemas/organisation.schema.json` |
| Spec | §11; §11.2; §64 ("New repositories are created private… safe defaults, activation explicit"); D53; §98.2 Phase 1 completion check |

Three organisation-level facts become declared state here, and nothing else does. Owner continuity is task **L5-01-11**; it is referenced from this document and declared in its own file, because a shared mutable file is exactly what PARTITION rule 3 forbids.

The organisation login is not in this file. §0.6 binds: it is supplied at apply time in `$ORG_LOGIN`. The document records `login_source: env:ORG_LOGIN` and nothing more.

**Commands**

```bash
set -e
cd "$(git rev-parse --show-toplevel)"
export CONTROL_PLANE_ROOT="$PWD"
git fetch origin
git checkout integration
git pull --ff-only origin integration
test -f access/tools/validate_access_config.py || { echo "MISSING DEPENDENCY L5-01-02"; exit 1; }
git checkout -b lane/5/p1-organisation
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/model/organisation.yaml <<'YAMLEOF'
# access/model/organisation.yaml
# Spec Section 11 and Section 11.2. Organisation-level declared state.
# No organisation login appears here: it is supplied at apply time in $ORG_LOGIN.
# No repository name appears here: repositories are enumerated dynamically from
# the product registry (Section 11).
document: organisation
spec_sections: ["11", "11.2", "64"]
decisions: ["D53"]

organisation:
  count: 1
  login_source: env:ORG_LOGIN
  personal_accounts_as_product_homes: prohibited
  repository_enumeration: dynamic_from_product_registry
  hard_coded_repository_lists: forbidden
  rationale: >-
    All products live in one company-owned GitHub organisation. Personal
    accounts are prohibited as product homes - company IP must not depend on an
    individual's login (Section 11).

base_permission:
  value: read
  applies_to: every_organisation_member
  rationale: >-
    A small team benefits far more from being able to help each other than it
    loses to an internal threat that is largely theoretical (Section 11.2).
  contractor_exception: >-
    Temporary specialists and contractors are the exception: their access is
    scoped explicitly and they are not granted organisation-wide Read unless
    their scope requires it (Section 11.2).
  client_isolation_mechanism: a_separate_organisation_under_company_control
  client_isolation_is_not: restricting_reads_inside_this_organisation

two_factor:
  organisation_enforced: true
  stays_enabled: true
  member_without_two_factor: cannot_be_a_member
  strong_factor_required_for:
    - founder
    - organisation_owner
    - "capability:platform-admin"
  accepted_strong_factors:
    - hardware_security_key
    - passkey
  weaker_second_factors_rejected_for_those_holders: true
  rationale: >-
    The organisation setting requiring 2FA is enabled and stays enabled; an
    account without 2FA cannot be a member. The Founder, organisation Owners
    and holders of the platform-admin capability authenticate with hardware
    security keys or passkeys, not weaker second factors (Section 11.2, D53).

access_removal:
  mechanism: remove_the_person_from_the_organisation
  effect: removes_all_access_in_one_action
  rationale: >-
    This is the security argument against split accounts (Section 11).

machine_approval:
  actions_can_approve_pull_requests: false
  rationale: >-
    No machine approval satisfies a gate. CODEOWNERS is generated to contain
    human identities only, so the required Code Owner review must come from a
    human, and the Phase 1 completion check verifies this negatively
    (Section 11.3, Section 98.2, D53).

new_repository_defaults:
  visibility: private
  branch_protection: applied_from_the_template_at_creation
  environment_access: none
  third_party_app_access: none
  principle: safe_defaults_activation_explicit
  spec_section: "64"

owner_continuity:
  declared_in: access/model/owner-continuity.yaml
  task: L5-01-11
  rule: >-
    A second organisation Owner - or an escrowed break-glass owner credential -
    exists as part of founder continuity; organisation ownership is never a
    population of one with no recovery path (Section 11.2, Section 14).
YAMLEOF
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/schemas/organisation.schema.json <<'JSONEOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  # NEEDS_URN (FD-050): replace with urn:multiproduct:schemas:<type>:<version>
  "$id": "https://control-plane.invalid/access/organisation.schema.json",
  "x-target": "access/model/organisation.yaml",
  "title": "Organisation-level declared access state (spec Section 11, Section 11.2)",
  "type": "object",
  "additionalProperties": false,
  "required": ["document", "spec_sections", "decisions", "organisation",
               "base_permission", "two_factor", "access_removal",
               "machine_approval", "new_repository_defaults", "owner_continuity"],
  "properties": {
    "document": {"const": "organisation"},
    "spec_sections": {"type": "array", "items": {"type": "string"}, "minItems": 1},
    "decisions": {"type": "array", "items": {"type": "string"}},
    "organisation": {
      "type": "object",
      "additionalProperties": false,
      "required": ["count", "login_source", "personal_accounts_as_product_homes",
                   "repository_enumeration", "hard_coded_repository_lists", "rationale"],
      "properties": {
        "count": {"const": 1},
        "login_source": {"const": "env:ORG_LOGIN"},
        "personal_accounts_as_product_homes": {"const": "prohibited"},
        "repository_enumeration": {"const": "dynamic_from_product_registry"},
        "hard_coded_repository_lists": {"const": "forbidden"},
        "rationale": {"type": "string"}
      }
    },
    "base_permission": {
      "type": "object",
      "additionalProperties": false,
      "required": ["value", "applies_to", "rationale", "contractor_exception",
                   "client_isolation_mechanism", "client_isolation_is_not"],
      "properties": {
        "value": {"const": "read"},
        "applies_to": {"const": "every_organisation_member"},
        "rationale": {"type": "string"},
        "contractor_exception": {"type": "string"},
        "client_isolation_mechanism": {"const": "a_separate_organisation_under_company_control"},
        "client_isolation_is_not": {"const": "restricting_reads_inside_this_organisation"}
      }
    },
    "two_factor": {
      "type": "object",
      "additionalProperties": false,
      "required": ["organisation_enforced", "stays_enabled", "member_without_two_factor",
                   "strong_factor_required_for", "accepted_strong_factors",
                   "weaker_second_factors_rejected_for_those_holders", "rationale"],
      "properties": {
        "organisation_enforced": {"const": true},
        "stays_enabled": {"const": true},
        "member_without_two_factor": {"const": "cannot_be_a_member"},
        "strong_factor_required_for": {
          "type": "array",
          "minItems": 3,
          "uniqueItems": true,
          "items": {"enum": ["founder", "organisation_owner", "capability:platform-admin"]}
        },
        "accepted_strong_factors": {
          "type": "array",
          "minItems": 2,
          "uniqueItems": true,
          "items": {"enum": ["hardware_security_key", "passkey"]}
        },
        "weaker_second_factors_rejected_for_those_holders": {"const": true},
        "rationale": {"type": "string"}
      }
    },
    "access_removal": {
      "type": "object",
      "additionalProperties": false,
      "required": ["mechanism", "effect", "rationale"],
      "properties": {
        "mechanism": {"const": "remove_the_person_from_the_organisation"},
        "effect": {"const": "removes_all_access_in_one_action"},
        "rationale": {"type": "string"}
      }
    },
    "machine_approval": {
      "type": "object",
      "additionalProperties": false,
      "required": ["actions_can_approve_pull_requests", "rationale"],
      "properties": {
        "actions_can_approve_pull_requests": {"const": false},
        "rationale": {"type": "string"}
      }
    },
    "new_repository_defaults": {
      "type": "object",
      "additionalProperties": false,
      "required": ["visibility", "branch_protection", "environment_access",
                   "third_party_app_access", "principle", "spec_section"],
      "properties": {
        "visibility": {"const": "private"},
        "branch_protection": {"const": "applied_from_the_template_at_creation"},
        "environment_access": {"const": "none"},
        "third_party_app_access": {"const": "none"},
        "principle": {"const": "safe_defaults_activation_explicit"},
        "spec_section": {"type": "string"}
      }
    },
    "owner_continuity": {
      "type": "object",
      "additionalProperties": false,
      "required": ["declared_in", "task", "rule"],
      "properties": {
        "declared_in": {"const": "access/model/owner-continuity.yaml"},
        "task": {"const": "L5-01-11"},
        "rule": {"type": "string"}
      }
    }
  }
}
JSONEOF
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
python access/tools/validate_access_config.py
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
git add access
git commit -m "$(printf 'L5-01-03: organisation.yaml - single org, base Read, enforced 2FA\n\nLane: L5\n')"
git push -u origin lane/5/p1-organisation
```

### Acceptance criteria

| # | Criterion | Proving command | Expected output |
|---|---|---|---|
| C1 | The document validates and it is the only one | `python access/tools/validate_access_config.py \| tail -1` | `ACCESS CONFIG VALIDATION PASSED (1 documents)` |
| C2 | Exactly one organisation | `python -c "import yaml;print(yaml.safe_load(open('access/model/organisation.yaml'))['organisation']['count'])"` | `1` |
| C3 | Base permission is Read | `python -c "import yaml;print(yaml.safe_load(open('access/model/organisation.yaml'))['base_permission']['value'])"` | `read` |
| C4 | 2FA is organisation-enforced | `python -c "import yaml;print(yaml.safe_load(open('access/model/organisation.yaml'))['two_factor']['organisation_enforced'])"` | `True` |
| C5 | Hardware keys or passkeys for exactly the three holder classes | `python -c "import yaml;print(len(yaml.safe_load(open('access/model/organisation.yaml'))['two_factor']['strong_factor_required_for']))"` | `3` |
| C6 | No organisation login is committed | `grep -cE '^[[:space:]]*login:' access/model/organisation.yaml \| tr -d ' '` | `0` |
| C7 | A stray key is rejected (negative test) | see SELF-VERIFY | `1` |
| C8 | No path outside `access/` touched | `git diff --name-only origin/integration...HEAD \| grep -cv '^access/' \| tr -d ' '` | `0` |

### SELF-VERIFY

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
echo "C1 $(python access/tools/validate_access_config.py | tail -1)"
echo "C2 $(python -c "import yaml;print(yaml.safe_load(open('access/model/organisation.yaml'))['organisation']['count'])")"
echo "C3 $(python -c "import yaml;print(yaml.safe_load(open('access/model/organisation.yaml'))['base_permission']['value'])")"
echo "C4 $(python -c "import yaml;print(yaml.safe_load(open('access/model/organisation.yaml'))['two_factor']['organisation_enforced'])")"
echo "C5 $(python -c "import yaml;print(len(yaml.safe_load(open('access/model/organisation.yaml'))['two_factor']['strong_factor_required_for']))")"
echo "C6 $(grep -cE '^[[:space:]]*login:' access/model/organisation.yaml | tr -d ' ')"
trap 'git checkout -- access/model/organisation.yaml' EXIT
printf '\nstray_key: true\n' >> access/model/organisation.yaml
ec=0; python access/tools/validate_access_config.py >/dev/null 2>&1 || ec=$?; echo "C7 $ec"
git checkout -- access/model/organisation.yaml
trap - EXIT
echo "C8 $(git diff --name-only origin/integration...HEAD | grep -cv '^access/' | tr -d ' ')"
```

Expected output, exactly:

```
C1 ACCESS CONFIG VALIDATION PASSED (1 documents)
C2 1
C3 read
C4 True
C5 3
C6 0
C7 1
C8 0
```

### STOP

Stop and file a blocker if any of the following is true.

- `C1` prints a `FAILED` line. Read the `FAIL` lines above it: the schema and the document disagree, and the fix is in whichever of the two you mistyped — never in loosening `additionalProperties`.
- `C7` prints `0`. `additionalProperties: false` is not in force somewhere, and a typo in a key would then be silently ignored.
- `C6` prints anything other than `0` — an organisation login reached the document. Remove it; it is supplied at apply time in `$ORG_LOGIN` (§0.6).
- You are tempted to add a repository name, a person's login, or a token to this document. All three are STOP conditions, not omissions.

```bash
set -euo pipefail
bash access/tools/blocker.sh L5-01-03 "organisation.yaml does not validate" "<the failing criterion line>" "python access/tools/validate_access_config.py" "<its exact output>" "ACCESS CONFIG VALIDATION PASSED (1 documents)" "<one sentence of fact>"
```

---

## L5-01-04 — `permission-semantics.yaml` — the §11.1 verified table, machine-checked

| Field | Value |
|---|---|
| Size | M |
| Depends on | L5-01-02 |
| Writes | `access/model/permission-semantics.yaml`, `access/schemas/permission-semantics.schema.json`, `access/tools/check_permission_semantics.py` |
| Spec | §11.1 in full; §98.2 Phase 1 completion check ("an approval from a Read-only account does **not** satisfy branch protection while an approval from a Write-holding Cross-Reviewer does") |

§11.1 is transcribed, never inferred. The table is titled *"verified, not assumed"*, and the whole point of writing it down is that the two rows a designer would guess wrong sit next to each other:

* **Submit a review (comment, approve, request changes)** — Read: **Yes**.
* **Approval counts toward required approving reviews** — Read: **No**.

A Cross-Reviewer holding only Read therefore submits something that visually reads as an approval and the merge stays blocked. `check_permission_semantics.py` asserts that pair mechanically, so a later edit that "simplifies" the table fails CI rather than fails silently.

**Commands**

```bash
set -e
cd "$(git rev-parse --show-toplevel)"
export CONTROL_PLANE_ROOT="$PWD"
git fetch origin
git checkout integration
git pull --ff-only origin integration
test -f access/tools/validate_access_config.py || { echo "MISSING DEPENDENCY L5-01-02"; exit 1; }
git checkout -b lane/5/p1-permission-semantics
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/model/permission-semantics.yaml <<'YAMLEOF'
# access/model/permission-semantics.yaml
# Spec Section 11.1, "GitHub permission semantics - verified, not assumed".
# Verified against GitHub documentation on protected branches, pull request
# reviews and organisation repository roles. This table is TRANSCRIBED from the
# specification. It is never inferred, never simplified and never re-derived.
document: permission-semantics
spec_sections: ["11.1"]
levels: [read, triage, write, maintain, admin]

capabilities:
  - id: view_and_clone_code
    label: "View and clone code"
    by_level: {read: true, triage: true, write: true, maintain: true, admin: true}

  - id: comment_on_a_pull_request
    label: "Comment on a pull request"
    by_level: {read: true, triage: true, write: true, maintain: true, admin: true}

  - id: submit_a_review
    label: "Submit a review (comment, approve, request changes)"
    by_level: {read: true, triage: true, write: true, maintain: true, admin: true}

  - id: approval_counts_toward_required_approving_reviews
    label: "Approval counts toward required approving reviews"
    emphasised_in_spec: true
    by_level: {read: false, triage: false, write: true, maintain: true, admin: true}

  - id: request_reviewers_on_a_pull_request
    label: "Request reviewers on a pull request"
    by_level: {read: false, triage: true, write: true, maintain: true, admin: true}

  - id: push_branches_to_the_repository
    label: "Push branches to the repository"
    by_level: {read: false, triage: false, write: true, maintain: true, admin: true}

  - id: mark_a_draft_pull_request_ready_for_review
    label: "Mark a draft pull request ready for review"
    by_level: {read: false, triage: false, write: true, maintain: true, admin: true}

  - id: merge_into_a_protected_branch
    label: "Merge into a protected branch"
    by_level:
      read: false
      triage: false
      write: "Only when all protection rules are satisfied"
      maintain: "Only when all protection rules are satisfied"
      admin: "May bypass only if explicitly permitted"

  - id: deploy_to_a_protected_environment
    label: "Deploy to a protected environment"
    by_level:
      read: "Governed by Environment protection rules, not by repository role"
      triage: "Governed by Environment protection rules, not by repository role"
      write: "Governed by Environment protection rules, not by repository role"
      maintain: "Governed by Environment protection rules, not by repository role"
      admin: "Governed by Environment protection rules, not by repository role"

consequence:
  read_only_reviewer_can:
    - open a pull request
    - read it
    - comment on it
    - submit a review that visually reads as an approval
  read_only_reviewer_cannot:
    - satisfy required approving reviews
  result: the_merge_stays_blocked
  failure_mode: >-
    Any design assuming "Read is sufficient for cross-review" fails silently and
    produces exactly the outcome this operating system exists to prevent: a gate
    that appears to be working and is not (Section 11.1).

therefore:
  cross_reviewer_minimum_permission: write
  least_privilege_preserved_by: branch_protection
  least_privilege_not_preserved_by: withholding_write
  write_does_not_permit:
    - merging into a protected branch unless every protection rule is satisfied
    - deploying to a protected environment
  security_boundary_lives_in:
    - branch_protection
    - workflow_identity_gate
  workflow_identity_gate_spec_section: "27.2"
  environment_protection_rules: an_added_layer_where_the_plan_tier_provides_them
YAMLEOF
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/schemas/permission-semantics.schema.json <<'JSONEOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  # NEEDS_URN (FD-050): replace with urn:multiproduct:schemas:<type>:<version>
  "$id": "https://control-plane.invalid/access/permission-semantics.schema.json",
  "x-target": "access/model/permission-semantics.yaml",
  "title": "The verified GitHub permission-semantics table (spec Section 11.1)",
  "type": "object",
  "additionalProperties": false,
  "required": ["document", "spec_sections", "levels", "capabilities", "consequence", "therefore"],
  "$defs": {
    "cell": {"oneOf": [{"type": "boolean"}, {"type": "string", "minLength": 1}]},
    "row": {
      "type": "object",
      "additionalProperties": false,
      "required": ["read", "triage", "write", "maintain", "admin"],
      "properties": {
        "read": {"$ref": "#/$defs/cell"},
        "triage": {"$ref": "#/$defs/cell"},
        "write": {"$ref": "#/$defs/cell"},
        "maintain": {"$ref": "#/$defs/cell"},
        "admin": {"$ref": "#/$defs/cell"}
      }
    }
  },
  "properties": {
    "document": {"const": "permission-semantics"},
    "spec_sections": {"type": "array", "items": {"type": "string"}, "minItems": 1},
    "levels": {
      "type": "array",
      "minItems": 5,
      "maxItems": 5,
      "items": {"enum": ["read", "triage", "write", "maintain", "admin"]}
    },
    "capabilities": {
      "type": "array",
      "minItems": 9,
      "maxItems": 9,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["id", "label", "by_level"],
        "properties": {
          "id": {"type": "string", "pattern": "^[a-z0-9_]+$"},
          "label": {"type": "string", "minLength": 1},
          "emphasised_in_spec": {"type": "boolean"},
          "by_level": {"$ref": "#/$defs/row"}
        }
      }
    },
    "consequence": {
      "type": "object",
      "additionalProperties": false,
      "required": ["read_only_reviewer_can", "read_only_reviewer_cannot", "result", "failure_mode"],
      "properties": {
        "read_only_reviewer_can": {"type": "array", "minItems": 4, "items": {"type": "string"}},
        "read_only_reviewer_cannot": {"type": "array", "minItems": 1, "items": {"type": "string"}},
        "result": {"const": "the_merge_stays_blocked"},
        "failure_mode": {"type": "string"}
      }
    },
    "therefore": {
      "type": "object",
      "additionalProperties": false,
      "required": ["cross_reviewer_minimum_permission", "least_privilege_preserved_by",
                   "least_privilege_not_preserved_by", "write_does_not_permit",
                   "security_boundary_lives_in", "workflow_identity_gate_spec_section",
                   "environment_protection_rules"],
      "properties": {
        "cross_reviewer_minimum_permission": {"const": "write"},
        "least_privilege_preserved_by": {"const": "branch_protection"},
        "least_privilege_not_preserved_by": {"const": "withholding_write"},
        "write_does_not_permit": {"type": "array", "minItems": 2, "items": {"type": "string"}},
        "security_boundary_lives_in": {
          "type": "array",
          "minItems": 2,
          "items": {"enum": ["branch_protection", "workflow_identity_gate"]}
        },
        "workflow_identity_gate_spec_section": {"const": "27.2"},
        "environment_protection_rules": {"const": "an_added_layer_where_the_plan_tier_provides_them"}
      }
    }
  }
}
JSONEOF
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/tools/check_permission_semantics.py <<'PYEOF'
#!/usr/bin/env python
"""Assert the seven load-bearing facts of spec Section 11.1.

The table in access/model/permission-semantics.yaml is transcribed from
the specification. These assertions exist so that an edit which "simplifies" it
fails a check rather than failing silently in production, where the symptom is a
gate that appears to be working and is not.

Usage: check_permission_semantics.py [--config PATH]
Exit 0 on success, 1 on any failed assertion.
"""
import argparse
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DEFAULT = os.path.join(ROOT, "access", "model", "permission-semantics.yaml")


def cap(doc, cap_id):
    for entry in doc.get("capabilities", []):
        if entry.get("id") == cap_id:
            return entry.get("by_level", {})
    return {}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=DEFAULT)
    args = parser.parse_args()
    with open(args.config, "r", encoding="utf-8") as handle:
        doc = yaml.safe_load(handle)

    review = cap(doc, "submit_a_review")
    counts = cap(doc, "approval_counts_toward_required_approving_reviews")
    push = cap(doc, "push_branches_to_the_repository")
    therefore = doc.get("therefore", {})

    assertions = [
        ("PS-1", "a Read holder can submit a review",
         review.get("read") is True),
        ("PS-2", "a Read holder's approval does NOT count toward required approving reviews",
         counts.get("read") is False),
        ("PS-3", "a Triage holder's approval does NOT count either",
         counts.get("triage") is False),
        ("PS-4", "a Write holder's approval DOES count",
         counts.get("write") is True),
        ("PS-5", "Read cannot push branches and Write can",
         push.get("read") is False and push.get("write") is True),
        ("PS-6", "the Cross-Reviewer minimum permission is Write",
         therefore.get("cross_reviewer_minimum_permission") == "write"),
        ("PS-7", "least privilege is preserved by branch protection, not by withholding Write",
         therefore.get("least_privilege_preserved_by") == "branch_protection"
         and therefore.get("least_privilege_not_preserved_by") == "withholding_write"),
    ]

    failed = 0
    for ident, statement, ok in assertions:
        if not ok:
            print("FAIL %s: %s" % (ident, statement))
            failed += 1
    if failed:
        print("PERMISSION-SEMANTICS: FAIL (%d of %d assertions)" % (failed, len(assertions)))
        return 1
    print("PERMISSION-SEMANTICS: PASS (%d assertions)" % len(assertions))
    return 0


if __name__ == "__main__":
    sys.exit(main())
PYEOF
chmod +x access/tools/check_permission_semantics.py
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
python access/tools/validate_access_config.py
python access/tools/check_permission_semantics.py
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
git add access
git commit -m "$(printf 'L5-01-04: permission-semantics.yaml - the Section 11.1 verified table, machine-checked\n\nLane: L5\n')"
git push -u origin lane/5/p1-permission-semantics
```

### Acceptance criteria

| # | Criterion | Proving command | Expected output |
|---|---|---|---|
| D1 | Both documents validate | `python access/tools/validate_access_config.py \| tail -1` | `ACCESS CONFIG VALIDATION PASSED (2 documents)` |
| D2 | All seven §11.1 assertions hold | `python access/tools/check_permission_semantics.py` | `PERMISSION-SEMANTICS: PASS (7 assertions)` |
| D3 | All nine §11.1 capability rows are present | `python -c "import yaml;print(len(yaml.safe_load(open('access/model/permission-semantics.yaml'))['capabilities']))"` | `9` |
| D4 | A Read approval does not count | `python -c "import yaml;d=yaml.safe_load(open('access/model/permission-semantics.yaml'));print([c for c in d['capabilities'] if c['id']=='approval_counts_toward_required_approving_reviews'][0]['by_level']['read'])"` | `False` |
| D5 | A Read holder can still submit a review — the silent-failure half | `python -c "import yaml;d=yaml.safe_load(open('access/model/permission-semantics.yaml'));print([c for c in d['capabilities'] if c['id']=='submit_a_review'][0]['by_level']['read'])"` | `True` |
| D6 | Cross-Reviewers require Write | `python -c "import yaml;print(yaml.safe_load(open('access/model/permission-semantics.yaml'))['therefore']['cross_reviewer_minimum_permission'])"` | `write` |
| D7 | Flipping the load-bearing cell fails the checker (negative test) | see SELF-VERIFY | `1` |
| D8 | No path outside `access/` touched | `git diff --name-only origin/integration...HEAD \| grep -cv '^access/' \| tr -d ' '` | `0` |

### SELF-VERIFY

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
echo "D1 $(python access/tools/validate_access_config.py | tail -1)"
echo "D2 $(python access/tools/check_permission_semantics.py)"
echo "D3 $(python -c "import yaml;print(len(yaml.safe_load(open('access/model/permission-semantics.yaml'))['capabilities']))")"
echo "D4 $(python -c "import yaml;d=yaml.safe_load(open('access/model/permission-semantics.yaml'));print([c for c in d['capabilities'] if c['id']=='approval_counts_toward_required_approving_reviews'][0]['by_level']['read'])")"
echo "D5 $(python -c "import yaml;d=yaml.safe_load(open('access/model/permission-semantics.yaml'));print([c for c in d['capabilities'] if c['id']=='submit_a_review'][0]['by_level']['read'])")"
echo "D6 $(python -c "import yaml;print(yaml.safe_load(open('access/model/permission-semantics.yaml'))['therefore']['cross_reviewer_minimum_permission'])")"
trap 'git checkout -- access/model/permission-semantics.yaml' EXIT
sed -i 's/^    by_level: {read: false, triage: false, write: true, maintain: true, admin: true}$/    by_level: {read: true, triage: false, write: true, maintain: true, admin: true}/' access/model/permission-semantics.yaml
ec=0; python access/tools/check_permission_semantics.py >/dev/null 2>&1 || ec=$?; echo "D7 $ec"
git checkout -- access/model/permission-semantics.yaml
trap - EXIT
echo "D8 $(git diff --name-only origin/integration...HEAD | grep -cv '^access/' | tr -d ' ')"
```

Expected output, exactly:

```
D1 ACCESS CONFIG VALIDATION PASSED (2 documents)
D2 PERMISSION-SEMANTICS: PASS (7 assertions)
D3 9
D4 False
D5 True
D6 write
D7 1
D8 0
```

### STOP

Stop and file a blocker if any of the following is true.

- `D4` prints `True`. The transcription is wrong in the one cell the whole access model rests on. Do not "fix" it by changing the checker.
- `D5` prints `False`. Then the table no longer records that a Read-only review *looks* like an approval, and the silent-failure mode §11.1 warns about is no longer documented.
- `D7` prints `0` — the checker does not detect a flipped cell, so it is decoration.
- Anything in this file tempts you to write "Read is sufficient for cross-review". That sentence is the failure §11.1 exists to prevent.

```bash
set -euo pipefail
bash access/tools/blocker.sh L5-01-04 "permission semantics table does not match Section 11.1" "<the failing criterion line>" "python access/tools/check_permission_semantics.py" "<its exact output>" "PERMISSION-SEMANTICS: PASS (7 assertions)" "<one sentence of fact>"
```

---

## L5-01-05 — `teams.yaml` — Teams derived from registries, the §11.2 person-class table

| Field | Value |
|---|---|
| Size | M |
| Depends on | L5-01-04 |
| Writes | `access/model/teams.yaml`, `access/schemas/teams.schema.json`, `access/tools/check_team_derivation.py` |
| Spec | §11.2 ("Write is granted through Teams, derived from the registries"; the six-row person-class table; "Team structure"); §53 drift; SIG-03; §98.2 Phase 1; D101 |

Two things this document is **not**. It is not a list of Teams — Team membership is derived from the registries and reconciled continuously, so a list here would be a second source of truth and a guaranteed drift finding. And it is not a list of repositories — §11 forbids that outright. It declares the **derivation rules** and the **person-class table**, and the apply runbook of **L5-01-12** consumes a registry-derived JSON input document at apply time.

The Phase 1 subtlety is D101 and is written into the document: Week 1 grants Write from an **interim** assignment set, which Phase 3 replaces with the registry-derived one. Waiting for Phase 3 would mean arming a Code-Owner-and-approval gate while no Team grants Write.

**Commands**

```bash
set -e
cd "$(git rev-parse --show-toplevel)"
export CONTROL_PLANE_ROOT="$PWD"
git fetch origin
git checkout integration
git pull --ff-only origin integration
test -f access/model/permission-semantics.yaml || { echo "MISSING DEPENDENCY L5-01-04"; exit 1; }
git checkout -b lane/5/p1-teams
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/model/teams.yaml <<'YAMLEOF'
# access/model/teams.yaml
# Spec Section 11.2. The Teams model and the person-class permission table.
# This document declares DERIVATION RULES. It contains no Team list, no
# repository name and no person login: Team membership is derived from the
# registries and reconciled continuously (Section 11.2), and a second list here
# would be a second source of truth.
document: teams
spec_sections: ["11.2", "53", "98.2"]
decisions: ["D101"]

derivation:
  source: the_registries
  input_at_apply_time: a_registry_derived_json_input_document
  input_rule: >-
    No lane reads registries/** from this source tree. The derived membership
    arrives as a JSON input document supplied on the command line
    (PARTITION rule 4).
  reconciled: continuously
  mismatch_behaviour: fails_ci_and_raises_a_drift_finding
  mismatch_between: ["people.yaml", "product.yaml", "actual_github_team_membership"]
  drift_signal: SIG-03
  drift_spec_section: "53"

team_shapes:
  - id: per_product
    naming: named_for_the_product
    membership: everyone_holding_a_current_assignment_on_it
    cardinality: one_per_product_in_the_product_registry
    grants: write
    grants_on: the_repositories_of_that_product

  - id: organisation_wide_team_lead
    naming: derived_from_the_team_lead_role_identifier
    membership: holders_of_the_team_lead_or_acting_team_lead_role
    cardinality: exactly_one
    grants: write
    grants_on: all_product_repositories

  - id: organisation_wide_qa
    naming: derived_from_the_qa_role_identifier
    membership: holders_of_the_qa_role
    cardinality: exactly_one
    grants: write
    grants_on: all_product_repositories

person_classes:
  - id: founder
    organisation_role: owner
    write_on: all_implicit
    read_on: all

  - id: team_lead_or_acting_team_lead
    organisation_role: member
    write_on: all_product_repositories
    read_on: all

  - id: qa
    organisation_role: member
    write_on: all_product_repositories
    read_on: all

  - id: developer
    organisation_role: member
    write_on: repositories_of_products_where_they_hold_a_qualifying_assignment
    qualifying_assignments: [primary_owner, cross_reviewer, backup_owner, temporary_contributor]
    read_on: all_others

  - id: contractor_or_temporary_specialist
    organisation_role: outside_collaborator_or_scoped_member
    write_on: only_repositories_named_in_their_scope
    read_on: only_repositories_named_in_their_scope

  - id: background_machine_layer
    organisation_role: machine_account
    write_on: branch_push_only_on_whitelisted_repositories
    may_merge: false
    environment_access: none
    read_on: repositories_in_its_queue
    never_appears_in_codeowners: true

cross_reviewer:
  minimum_permission: write
  source_document: access/model/permission-semantics.yaml
  spec_section: "11.1"
  rationale: >-
    A Cross-Reviewer holding only Read submits a review that visually reads as
    an approval and the merge stays blocked. Least privilege is preserved by
    branch protection, not by withholding Write.

phase_1_interim:
  assignment_set: interim
  replaced_by: the_phase_3_registry_derived_assignment_set
  decision: D101
  binding_rule: >-
    Teams grant Write within Week 1 and BEFORE branch protection is armed.
    Arming a Code-Owner-and-approval gate while no Team grants Write leaves
    nobody whose approval counts, and Section 95.4 names the result exactly: a
    team that experiences its merges mysteriously breaking (Section 98.2).
  arming_order_document: access/arming/arming-order.yaml

owner_continuity_reference: access/model/owner-continuity.yaml
YAMLEOF
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/schemas/teams.schema.json <<'JSONEOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  # NEEDS_URN (FD-050): replace with urn:multiproduct:schemas:<type>:<version>
  "$id": "https://control-plane.invalid/access/teams.schema.json",
  "x-target": "access/model/teams.yaml",
  "title": "Team derivation rules and the person-class permission table (spec Section 11.2)",
  "type": "object",
  "additionalProperties": false,
  "required": ["document", "spec_sections", "decisions", "derivation", "team_shapes",
               "person_classes", "cross_reviewer", "phase_1_interim",
               "owner_continuity_reference"],
  "properties": {
    "document": {"const": "teams"},
    "spec_sections": {"type": "array", "items": {"type": "string"}, "minItems": 1},
    "decisions": {"type": "array", "items": {"type": "string"}, "minItems": 1},
    "derivation": {
      "type": "object",
      "additionalProperties": false,
      "required": ["source", "input_at_apply_time", "input_rule", "reconciled",
                   "mismatch_behaviour", "mismatch_between", "drift_signal",
                   "drift_spec_section"],
      "properties": {
        "source": {"const": "the_registries"},
        "input_at_apply_time": {"const": "a_registry_derived_json_input_document"},
        "input_rule": {"type": "string"},
        "reconciled": {"const": "continuously"},
        "mismatch_behaviour": {"const": "fails_ci_and_raises_a_drift_finding"},
        "mismatch_between": {"type": "array", "minItems": 3, "items": {"type": "string"}},
        "drift_signal": {"const": "SIG-03"},
        "drift_spec_section": {"const": "53"}
      }
    },
    "team_shapes": {
      "type": "array",
      "minItems": 3,
      "maxItems": 3,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["id", "naming", "membership", "cardinality", "grants", "grants_on"],
        "properties": {
          "id": {"enum": ["per_product", "organisation_wide_team_lead", "organisation_wide_qa"]},
          "naming": {"type": "string"},
          "membership": {"type": "string"},
          "cardinality": {"type": "string"},
          "grants": {"const": "write"},
          "grants_on": {"type": "string"}
        }
      }
    },
    "person_classes": {
      "type": "array",
      "minItems": 6,
      "maxItems": 6,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["id", "organisation_role", "write_on", "read_on"],
        "properties": {
          "id": {"enum": ["founder", "team_lead_or_acting_team_lead", "qa", "developer",
                          "contractor_or_temporary_specialist", "background_machine_layer"]},
          "organisation_role": {"enum": ["owner", "member", "outside_collaborator_or_scoped_member",
                                         "machine_account"]},
          "write_on": {"type": "string"},
          "read_on": {"type": "string"},
          "qualifying_assignments": {"type": "array", "items": {"type": "string"}},
          "may_merge": {"type": "boolean"},
          "environment_access": {"type": "string"},
          "never_appears_in_codeowners": {"type": "boolean"}
        }
      }
    },
    "cross_reviewer": {
      "type": "object",
      "additionalProperties": false,
      "required": ["minimum_permission", "source_document", "spec_section", "rationale"],
      "properties": {
        "minimum_permission": {"const": "write"},
        "source_document": {"const": "access/model/permission-semantics.yaml"},
        "spec_section": {"const": "11.1"},
        "rationale": {"type": "string"}
      }
    },
    "phase_1_interim": {
      "type": "object",
      "additionalProperties": false,
      "required": ["assignment_set", "replaced_by", "decision", "binding_rule",
                   "arming_order_document"],
      "properties": {
        "assignment_set": {"const": "interim"},
        "replaced_by": {"const": "the_phase_3_registry_derived_assignment_set"},
        "decision": {"const": "D101"},
        "binding_rule": {"type": "string"},
        "arming_order_document": {"const": "access/arming/arming-order.yaml"}
      }
    },
    "owner_continuity_reference": {"const": "access/model/owner-continuity.yaml"}
  }
}
JSONEOF
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/tools/check_team_derivation.py <<'PYEOF'
#!/usr/bin/env python
"""Assert the Section 11.2 Teams model and its two anti-drift properties.

Six assertions:
  TD-1  all six Section 11.2 person classes are present, exactly once each
  TD-2  the background machine layer may not merge, holds no environment access,
        and never appears in CODEOWNERS
  TD-3  the Cross-Reviewer minimum permission is Write, and it agrees with
        access/model/permission-semantics.yaml rather than restating it
  TD-4  no repository name appears anywhere in the document (Section 11)
  TD-5  the Phase 1 grant is the interim assignment set replaced at Phase 3 (D101)
  TD-6  every Team shape grants Write, since a Team that grants nothing arms nothing

Usage: check_team_derivation.py [--config PATH] [--semantics PATH]
Exit 0 on success, 1 on any failed assertion.
"""
import argparse
import os
import re
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DEFAULT = os.path.join(ROOT, "access", "model", "teams.yaml")
SEMANTICS = os.path.join(ROOT, "access", "model", "permission-semantics.yaml")

EXPECTED_CLASSES = [
    "founder",
    "team_lead_or_acting_team_lead",
    "qa",
    "developer",
    "contractor_or_temporary_specialist",
    "background_machine_layer",
]

# owner/repo, exactly two path segments -- the shape a repository name takes.
REPO_SHAPE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


def walk_strings(node):
    if isinstance(node, dict):
        for key, value in node.items():
            yield str(key)
            for item in walk_strings(value):
                yield item
    elif isinstance(node, list):
        for value in node:
            for item in walk_strings(value):
                yield item
    elif isinstance(node, str):
        yield node


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=DEFAULT)
    parser.add_argument("--semantics", default=SEMANTICS)
    args = parser.parse_args()

    with open(args.config, "r", encoding="utf-8") as handle:
        doc = yaml.safe_load(handle)
    with open(args.semantics, "r", encoding="utf-8") as handle:
        semantics = yaml.safe_load(handle)

    classes = [entry.get("id") for entry in doc.get("person_classes", [])]
    machine = {}
    for entry in doc.get("person_classes", []):
        if entry.get("id") == "background_machine_layer":
            machine = entry

    repo_shaped = sorted(set(
        text for text in walk_strings(doc)
        if REPO_SHAPE.match(text) and not text.endswith((".yaml", ".json", ".py", ".sh", ".md"))
    ))

    assertions = [
        ("TD-1", "all six Section 11.2 person classes present exactly once",
         classes == EXPECTED_CLASSES),
        ("TD-2", "the background machine layer may not merge, has no environment access "
                 "and never appears in CODEOWNERS",
         machine.get("may_merge") is False
         and machine.get("environment_access") == "none"
         and machine.get("never_appears_in_codeowners") is True),
        ("TD-3", "the Cross-Reviewer minimum permission is Write and agrees with Section 11.1",
         doc.get("cross_reviewer", {}).get("minimum_permission") == "write"
         and semantics.get("therefore", {}).get("cross_reviewer_minimum_permission") == "write"),
        ("TD-4", "no repository name appears in the document (Section 11)",
         repo_shaped == []),
        ("TD-5", "the Phase 1 grant is the interim assignment set, replaced at Phase 3 (D101)",
         doc.get("phase_1_interim", {}).get("assignment_set") == "interim"
         and doc.get("phase_1_interim", {}).get("decision") == "D101"),
        ("TD-6", "every Team shape grants Write",
         bool(doc.get("team_shapes"))
         and all(shape.get("grants") == "write" for shape in doc["team_shapes"])),
    ]

    failed = 0
    for ident, statement, ok in assertions:
        if not ok:
            print("FAIL %s: %s" % (ident, statement))
            failed += 1
    if repo_shaped and failed:
        print("       repository-shaped strings found: %s" % ", ".join(repo_shaped))
    if failed:
        print("TEAM-DERIVATION: FAIL (%d of %d assertions)" % (failed, len(assertions)))
        return 1
    print("TEAM-DERIVATION: PASS (%d assertions)" % len(assertions))
    return 0


if __name__ == "__main__":
    sys.exit(main())
PYEOF
chmod +x access/tools/check_team_derivation.py
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
python access/tools/validate_access_config.py
python access/tools/check_permission_semantics.py
python access/tools/check_team_derivation.py
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
git add access
git commit -m "$(printf 'L5-01-05: teams.yaml - Teams derived from registries, the Section 11.2 person-class table\n\nLane: L5\n')"
git push -u origin lane/5/p1-teams
```

### Acceptance criteria

| # | Criterion | Proving command | Expected output |
|---|---|---|---|
| E1 | All three documents validate | `python access/tools/validate_access_config.py \| tail -1` | `ACCESS CONFIG VALIDATION PASSED (3 documents)` |
| E2 | All six derivation assertions hold | `python access/tools/check_team_derivation.py` | `TEAM-DERIVATION: PASS (6 assertions)` |
| E3 | Six person classes, no more and no fewer | `python -c "import yaml;print(len(yaml.safe_load(open('access/model/teams.yaml'))['person_classes']))"` | `6` |
| E4 | The machine layer may not merge | `python -c "import yaml;d=yaml.safe_load(open('access/model/teams.yaml'));print([c for c in d['person_classes'] if c['id']=='background_machine_layer'][0]['may_merge'])"` | `False` |
| E5 | Teams grant Write before arming, from the interim set (D101) | `python -c "import yaml;print(yaml.safe_load(open('access/model/teams.yaml'))['phase_1_interim']['decision'])"` | `D101` |
| E6 | No Team list and no repository list is committed | `grep -cE '^[[:space:]]*(teams|repositories):[[:space:]]*\[' access/model/teams.yaml \| tr -d ' '` | `0` |
| E7 | Dropping a person class fails the checker (negative test) | see SELF-VERIFY | `1` |
| E8 | No path outside `access/` touched | `git diff --name-only origin/integration...HEAD \| grep -cv '^access/' \| tr -d ' '` | `0` |

### SELF-VERIFY

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
echo "E1 $(python access/tools/validate_access_config.py | tail -1)"
echo "E2 $(python access/tools/check_team_derivation.py)"
echo "E3 $(python -c "import yaml;print(len(yaml.safe_load(open('access/model/teams.yaml'))['person_classes']))")"
echo "E4 $(python -c "import yaml;d=yaml.safe_load(open('access/model/teams.yaml'));print([c for c in d['person_classes'] if c['id']=='background_machine_layer'][0]['may_merge'])")"
echo "E5 $(python -c "import yaml;print(yaml.safe_load(open('access/model/teams.yaml'))['phase_1_interim']['decision'])")"
echo "E6 $(grep -cE '^[[:space:]]*(teams|repositories):[[:space:]]*\[' access/model/teams.yaml | tr -d ' ')"
python - <<'PYEOF'
import yaml
p = "access/model/teams.yaml"
d = yaml.safe_load(open(p, encoding="utf-8"))
d["person_classes"] = [c for c in d["person_classes"] if c["id"] != "qa"]
open("access/testdata/arming/teams-missing-class.yaml", "w", encoding="utf-8").write(
    yaml.safe_dump(d, sort_keys=False))
PYEOF
ec=0; python access/tools/check_team_derivation.py --config access/testdata/arming/teams-missing-class.yaml >/dev/null 2>&1 || ec=$?; echo "E7 $ec"
rm -f access/testdata/arming/teams-missing-class.yaml
echo "E8 $(git diff --name-only origin/integration...HEAD | grep -cv '^access/' | tr -d ' ')"
```

Expected output, exactly:

```
E1 ACCESS CONFIG VALIDATION PASSED (3 documents)
E2 TEAM-DERIVATION: PASS (6 assertions)
E3 6
E4 False
E5 D101
E6 0
E7 1
E8 0
```

### STOP

Stop and file a blocker if any of the following is true.

- `E2` prints `FAIL TD-4` — a repository-shaped string reached the document. §11 forbids a hard-coded repository list anywhere; the fix is to delete it, never to relax the regular expression.
- `E2` prints `FAIL TD-3` — this document and `permission-semantics.yaml` disagree about the Cross-Reviewer minimum permission. Two documents disagreeing about the one fact §11.1 exists to fix is a STOP, not a merge conflict to resolve by preference.
- `E7` prints `0` — the checker does not notice a missing person class.
- You are about to write an actual Team name, a person's login, or an assignment into this file. Membership is derived; a copy here is a second source of truth and a guaranteed SIG-03 finding.

```bash
set -euo pipefail
bash access/tools/blocker.sh L5-01-05 "teams.yaml derivation rules do not check out" "<the failing criterion line>" "python access/tools/check_team_derivation.py" "<its exact output>" "TEAM-DERIVATION: PASS (6 assertions)" "<one sentence of fact>"
```

---

## L5-01-06 — Human-only CODEOWNERS generator with executed negative tests

> **Partition status verified (Session 13, 2026-09-08):** This task writes a CODEOWNERS generator
> script to `access/codeowners/` (L5's own partition). It does NOT write the root `/CODEOWNERS`.
> SELF-VERIFY confirms `^CODEOWNERS$` count = 0. **Safe to dispatch.**

| Field | Value |
|---|---|
| Size | L |
| Depends on | L5-01-05 |
| Writes | `access/codeowners/generate_codeowners.py`, `access/codeowners/machine-identity-denylist.yaml`, `access/codeowners/test_generate_codeowners.sh`, `access/schemas/machine-identity-denylist.schema.json`, `access/schemas/codeowners-input.schema.json`, `access/testdata/codeowners/*.json` |
| Spec | §11.3 ("CODEOWNERS is generated to contain human identities only — no machine account ever appears in it… The Phase 1 completion check verifies this negatively"); §40.1 fifth-tier credential names; D53; D89; §98.2 |

Read §0.2 again before starting. **This task never writes the control-plane repository's root `CODEOWNERS`** — that path belongs to L0. It builds the generator and proves it refuses machine identities. Output goes to standard output; the caller redirects it.

The organisation login is a command-line argument (`--org`), never a value in the tree (§0.6). The input document is a JSON file supplied on the command line — the generator never reads `registries/**` (PARTITION rule 4), and the shape is fixed by `access/schemas/codeowners-input.schema.json`, which is the interface §0.3 publishes to L3 provisioning.

The schema's `x-target` is the reference input fixture. That is deliberate: a schema governing a command-line input document still needs a committed conformance witness, and the fixture is it. A schema whose target does not exist fails `validate_access_config.py`, which is the behaviour that keeps this interface honest.

**Commands**

```bash
set -e
cd "$(git rev-parse --show-toplevel)"
export CONTROL_PLANE_ROOT="$PWD"
git fetch origin
git checkout integration
git pull --ff-only origin integration
test -f access/model/teams.yaml || { echo "MISSING DEPENDENCY L5-01-05"; exit 1; }
git checkout -b lane/5/p1-codeowners
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/codeowners/machine-identity-denylist.yaml <<'YAMLEOF'
# access/codeowners/machine-identity-denylist.yaml
# Spec Section 11.3 and Section 98.2. D53, D89.
# CODEOWNERS is generated to contain human identities only - no machine account
# ever appears in it - so a machine-account approval can never satisfy branch
# protection: the required Code Owner review must come from a human.
#
# Pattern syntax: only "*" is a wildcard. Square brackets are LITERAL, so
# "*[bot]" means "ends with the literal text [bot]". The generator does not use
# fnmatch, under which "[bot]" would be a character class matching b, o or t and
# would refuse every ordinary team slug ending in one of those letters.
document: machine-identity-denylist
spec_sections: ["11.3", "40.1", "98.2"]
decisions: ["D53", "D89"]

rule: >-
  The generator emits an entry only for an identity declared kind human. Any
  other kind, any login matching a refused pattern, and any named fifth-tier
  machine credential cause the generator to refuse to emit at all. It never
  emits a partial file with the machine entry dropped: a silently pruned
  CODEOWNERS is a routing table nobody knows is wrong.

identity_kinds_admitted: [human]
identity_kinds_refused: [machine, app, bot, service_account]

login_patterns_refused:
  - "*[bot]"
  - "*-bot"
  - "bot-*"
  - "github-actions*"
  - "renovate*"
  - "dependabot*"

named_machine_credentials_refused:
  - reconciler
  - provisioning-cli
  - organisation-export
  - records-writer
  - layer-b-backup

named_machine_credentials_source: >-
  The fifth secrets tier of Section 40.1 - the reconciler credential, the
  provisioning CLI credential, the organisation-export token, the records-writer
  credential and the Layer B backup credential.

on_refusal:
  action: refuse_to_emit
  exit_code: 2
  message_prefix: "CODEOWNERS-REFUSED"
YAMLEOF
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/schemas/machine-identity-denylist.schema.json <<'JSONEOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  # NEEDS_URN (FD-050): replace with urn:multiproduct:schemas:<type>:<version>
  "$id": "https://control-plane.invalid/access/machine-identity-denylist.schema.json",
  "x-target": "access/codeowners/machine-identity-denylist.yaml",
  "title": "Machine identities refused by the CODEOWNERS generator (spec Section 11.3, D53)",
  "type": "object",
  "additionalProperties": false,
  "required": ["document", "spec_sections", "decisions", "rule", "identity_kinds_admitted",
               "identity_kinds_refused", "login_patterns_refused",
               "named_machine_credentials_refused", "named_machine_credentials_source",
               "on_refusal"],
  "properties": {
    "document": {"const": "machine-identity-denylist"},
    "spec_sections": {"type": "array", "items": {"type": "string"}, "minItems": 1},
    "decisions": {"type": "array", "items": {"type": "string"}, "minItems": 1},
    "rule": {"type": "string"},
    "identity_kinds_admitted": {
      "type": "array", "minItems": 1, "maxItems": 1, "items": {"const": "human"}
    },
    "identity_kinds_refused": {"type": "array", "minItems": 1, "items": {"type": "string"}},
    "login_patterns_refused": {"type": "array", "minItems": 3, "items": {"type": "string"}},
    "named_machine_credentials_refused": {
      "type": "array", "minItems": 5, "maxItems": 5, "items": {"type": "string"}
    },
    "named_machine_credentials_source": {"type": "string"},
    "on_refusal": {
      "type": "object",
      "additionalProperties": false,
      "required": ["action", "exit_code", "message_prefix"],
      "properties": {
        "action": {"const": "refuse_to_emit"},
        "exit_code": {"const": 2},
        "message_prefix": {"const": "CODEOWNERS-REFUSED"}
      }
    }
  }
}
JSONEOF
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/schemas/codeowners-input.schema.json <<'JSONEOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  # NEEDS_URN (FD-050): replace with urn:multiproduct:schemas:<type>:<version>
  "$id": "https://control-plane.invalid/access/codeowners-input.schema.json",
  "x-target": "access/testdata/codeowners/reference-input.json",
  "title": "CODEOWNERS generator input document (published interface, plan file section 0.3)",
  "description": "Constructed by L3 provisioning from the registries and supplied to access/codeowners/generate_codeowners.py on the command line. The x-target is the reference fixture, which is this interface's committed conformance witness.",
  "type": "object",
  "additionalProperties": false,
  "required": ["product_id", "product_team_slug", "team_lead_team_slug",
               "verification_responsibility", "migration_paths", "source_paths"],
  "$defs": {
    "identity": {
      "type": "object",
      "additionalProperties": false,
      "required": ["kind", "login"],
      "properties": {
        "kind": {"type": "string"},
        "login": {"type": "string", "minLength": 1}
      }
    }
  },
  "properties": {
    "product_id": {"type": "string", "minLength": 1},
    "product_team_slug": {"type": "string", "minLength": 1},
    "team_lead_team_slug": {"type": "string", "minLength": 1},
    "verification_responsibility": {"$ref": "#/$defs/identity"},
    "migration_paths": {"type": "array", "items": {"type": "string"}},
    "source_paths": {"type": "array", "items": {"type": "string"}}
  }
}
JSONEOF
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/testdata/codeowners/reference-input.json <<'JSONEOF'
{
  "product_id": "example-product",
  "product_team_slug": "product-example-product",
  "team_lead_team_slug": "role-team-lead",
  "verification_responsibility": {"kind": "human", "login": "verification-holder"},
  "migration_paths": ["migrations/"],
  "source_paths": ["src/", "app/"]
}
JSONEOF

cat > access/testdata/codeowners/machine-login-input.json <<'JSONEOF'
{
  "product_id": "example-product",
  "product_team_slug": "product-example-product",
  "team_lead_team_slug": "role-team-lead",
  "verification_responsibility": {"kind": "human", "login": "renovate[bot]"},
  "migration_paths": ["migrations/"],
  "source_paths": ["src/"]
}
JSONEOF

cat > access/testdata/codeowners/machine-kind-input.json <<'JSONEOF'
{
  "product_id": "example-product",
  "product_team_slug": "product-example-product",
  "team_lead_team_slug": "role-team-lead",
  "verification_responsibility": {"kind": "machine", "login": "verification-holder"},
  "migration_paths": ["migrations/"],
  "source_paths": ["src/"]
}
JSONEOF

cat > access/testdata/codeowners/named-credential-input.json <<'JSONEOF'
{
  "product_id": "example-product",
  "product_team_slug": "product-example-product",
  "team_lead_team_slug": "role-team-lead",
  "verification_responsibility": {"kind": "human", "login": "records-writer"},
  "migration_paths": ["migrations/"],
  "source_paths": ["src/"]
}
JSONEOF

cat > access/testdata/codeowners/machine-team-input.json <<'JSONEOF'
{
  "product_id": "example-product",
  "product_team_slug": "github-actions-runners",
  "team_lead_team_slug": "role-team-lead",
  "verification_responsibility": {"kind": "human", "login": "verification-holder"},
  "migration_paths": ["migrations/"],
  "source_paths": ["src/"]
}
JSONEOF
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/codeowners/generate_codeowners.py <<'PYEOF'
#!/usr/bin/env python
"""Generate a product repository's CODEOWNERS from a registry-derived input.

Spec Section 11.3:
  "CODEOWNERS routes review requests automatically and is generated from the
   registries rather than hand-maintained; the generator emits human identities
   only. verification/ is owned by whoever holds verification_responsibility.
   product.yaml, migration directories and CI workflow files are owned by the
   Team Lead role. Product source paths are owned by the product Team."

Human identities only (D53). If any identity in the input is not a human, the
generator REFUSES TO EMIT ANYTHING and exits 2. It never drops the offending
entry and emits the rest: a silently pruned routing table is worse than no file.

Pattern syntax in the denylist is deliberately NOT fnmatch. Only "*" is a
wildcard; every other character, square brackets included, is literal. Under
fnmatch the pattern "*[bot]" is a character class matching any login ending in
b, o or t -- which refuses "product-example-product" and every other ordinary
slug. Here it means "ends with the literal text [bot]", which is what the
denylist says.

Usage:
  generate_codeowners.py --org ORG_LOGIN --input INPUT.json
Exit codes:
  0  CODEOWNERS written to stdout
  2  a machine identity was present -- refused (message on stderr)
  3  the input document is missing, unreadable or the wrong shape
"""
import argparse
import json
import os
import re
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DENYLIST = os.path.join(ROOT, "access", "codeowners", "machine-identity-denylist.yaml")

REQUIRED_KEYS = ("product_id", "product_team_slug", "team_lead_team_slug",
                 "verification_responsibility", "migration_paths", "source_paths")


def refuse(reason):
    sys.stderr.write("CODEOWNERS-REFUSED %s\n" % reason)
    sys.exit(2)


def bad_input(reason):
    sys.stderr.write("CODEOWNERS-INPUT-ERROR %s\n" % reason)
    sys.exit(3)


def load_denylist(path):
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def pattern_to_regex(pattern):
    """Only '*' is a wildcard. Every other character is literal.

    Square brackets are literal here. fnmatch would read "[bot]" as a character
    class matching b, o or t, so "*[bot]" would refuse every login ending in one
    of those letters -- "product-example-product" among them.
    """
    parts = [re.escape(part) for part in pattern.split("*")]
    return re.compile("^" + ".*".join(parts) + "$")


def check_login(login, deny):
    lowered = login.lower()
    for pattern in deny["login_patterns_refused"]:
        if pattern_to_regex(pattern.lower()).match(lowered):
            return "login %r matches refused machine pattern %r" % (login, pattern)
    for named in deny["named_machine_credentials_refused"]:
        if lowered == named.lower():
            return "login %r is the named fifth-tier machine credential %r" % (login, named)
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--org", required=False)
    parser.add_argument("--input", required=False)
    args = parser.parse_args()

    if not args.org:
        bad_input("--org is required; the organisation login is never committed")
    if not args.input:
        bad_input("--input is required")
    if not os.path.exists(args.input):
        bad_input("input document not found: %s" % args.input)

    deny = load_denylist(DENYLIST)

    try:
        with open(args.input, "r", encoding="utf-8") as handle:
            doc = json.load(handle)
    except ValueError as exc:
        bad_input("input document is not valid JSON: %s" % exc)

    for key in REQUIRED_KEYS:
        if key not in doc:
            bad_input("input document is missing required key %r" % key)

    verification = doc["verification_responsibility"]
    if verification.get("kind") not in deny["identity_kinds_admitted"]:
        refuse("verification_responsibility kind %r is not human"
               % verification.get("kind"))
    problem = check_login(str(verification.get("login", "")), deny)
    if problem:
        refuse(problem)

    for slug_key in ("product_team_slug", "team_lead_team_slug"):
        problem = check_login(str(doc[slug_key]), deny)
        if problem:
            refuse("%s: %s" % (slug_key, problem))

    org = args.org
    product_team = "@%s/%s" % (org, doc["product_team_slug"])
    lead_team = "@%s/%s" % (org, doc["team_lead_team_slug"])
    verifier = "@%s" % verification["login"]

    lines = [
        "# GENERATED FILE - DO NOT EDIT BY HAND.",
        "# Generated by access/codeowners/generate_codeowners.py from a",
        "# registry-derived input document. Spec Section 11.3.",
        "# Human identities only: no machine account ever appears here, so a",
        "# machine-account approval can never satisfy branch protection (D53).",
        "# Product: %s" % doc["product_id"],
        "",
        "%-40s %s" % ("*", product_team),
    ]
    for path in doc["source_paths"]:
        lines.append("%-40s %s" % ("/" + path.lstrip("/"), product_team))
    lines.append("%-40s %s" % ("/verification/", verifier))
    lines.append("%-40s %s" % ("/product.yaml", lead_team))
    for path in doc["migration_paths"]:
        lines.append("%-40s %s" % ("/" + path.lstrip("/"), lead_team))
    lines.append("%-40s %s" % ("/.github/workflows/", lead_team))

    sys.stdout.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
PYEOF
chmod +x access/codeowners/generate_codeowners.py
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/codeowners/test_generate_codeowners.sh <<'SHEOF'
#!/usr/bin/env bash
# Executed negative tests for the human-only CODEOWNERS rule (Section 11.3).
# Section 98.2: "an approval from a machine account does NOT satisfy branch
# protection - CODEOWNERS is generated to contain human identities only, and the
# check is executed negatively." This script is that execution.
set -u
cd "$(git rev-parse --show-toplevel)"
GEN="access/codeowners/generate_codeowners.py"
FIX="access/testdata/codeowners"
PASS=0
FAIL=0

expect_exit () {  # expect_exit <label> <expected-code> <input-file>
  local label="$1" expected="$2" input="$3" rc
  python "$GEN" --org example-org --input "$input" >/dev/null 2>&1
  rc=$?
  if [ "$rc" -eq "$expected" ]; then
    PASS=$((PASS + 1))
  else
    echo "FAIL ${label}: expected exit ${expected}, got ${rc}"
    FAIL=$((FAIL + 1))
  fi
}

expect_exit "CO-1 valid human input emits"           0 "${FIX}/reference-input.json"
expect_exit "CO-2 bot login refused"                 2 "${FIX}/machine-login-input.json"
expect_exit "CO-3 non-human kind refused"            2 "${FIX}/machine-kind-input.json"
expect_exit "CO-4 named machine credential refused"  2 "${FIX}/named-credential-input.json"
expect_exit "CO-5 machine-shaped team slug refused"  2 "${FIX}/machine-team-input.json"

# CO-6: a refusal emits nothing at all on stdout.
OUT=$(python "$GEN" --org example-org --input "${FIX}/machine-login-input.json" 2>/dev/null || true)
if [ -z "$OUT" ]; then
  PASS=$((PASS + 1))
else
  echo "FAIL CO-6: a refusal wrote to stdout"; FAIL=$((FAIL + 1))
fi

# CO-7: a missing --org is an input error, never a guessed organisation.
python "$GEN" --input "${FIX}/reference-input.json" >/dev/null 2>&1
RC7=$?
if [ "$RC7" -eq 3 ]; then
  PASS=$((PASS + 1))
else
  echo "FAIL CO-7: missing --org exited ${RC7}, expected 3"; FAIL=$((FAIL + 1))
fi

# CO-8: the emitted file carries no machine identity of any refused shape.
HITS=$(python "$GEN" --org example-org --input "${FIX}/reference-input.json" \
       | grep -Eic 'bot\]|renovate|dependabot|github-actions|records-writer|reconciler' || true)
if [ "$HITS" = "0" ]; then
  PASS=$((PASS + 1))
else
  echo "FAIL CO-8: a machine identity appears in the emitted file"; FAIL=$((FAIL + 1))
fi

if [ "$FAIL" -ne 0 ]; then
  echo "CODEOWNERS-NEGATIVE-TESTS: FAIL (${FAIL} of $((PASS + FAIL)) cases)"
  exit 1
fi
echo "CODEOWNERS-NEGATIVE-TESTS: PASS (${PASS} cases)"
SHEOF
chmod +x access/codeowners/test_generate_codeowners.sh
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
python access/tools/validate_access_config.py
bash access/codeowners/test_generate_codeowners.sh
python access/codeowners/generate_codeowners.py --org example-org \
  --input access/testdata/codeowners/reference-input.json
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
git add access
git commit -m "$(printf 'L5-01-06: human-only CODEOWNERS generator with executed negative tests\n\nLane: L5\n')"
git push -u origin lane/5/p1-codeowners
```

### Acceptance criteria

| # | Criterion | Proving command | Expected output |
|---|---|---|---|
| F1 | All five documents validate | `python access/tools/validate_access_config.py \| tail -1` | `ACCESS CONFIG VALIDATION PASSED (5 documents)` |
| F2 | All eight negative tests execute and pass | `bash access/codeowners/test_generate_codeowners.sh \| tail -1` | `CODEOWNERS-NEGATIVE-TESTS: PASS (8 cases)` |
| F3 | A bot login is refused with exit 2 | `python access/codeowners/generate_codeowners.py --org example-org --input access/testdata/codeowners/machine-login-input.json >/dev/null 2>&1; echo $?` | `2` |
| F4 | The refusal names itself unambiguously | `python access/codeowners/generate_codeowners.py --org example-org --input access/testdata/codeowners/machine-login-input.json 2>&1 >/dev/null \| cut -d' ' -f1` | `CODEOWNERS-REFUSED` |
| F5 | A valid input emits exactly seven routing lines | `python access/codeowners/generate_codeowners.py --org example-org --input access/testdata/codeowners/reference-input.json \| grep -c '^[*/]'` | `7` |
| F6 | No machine identity appears in the emitted file | `python access/codeowners/generate_codeowners.py --org example-org --input access/testdata/codeowners/reference-input.json \| grep -Eic 'bot\]|renovate|records-writer'` | `0` |
| F7 | The repository's own root `CODEOWNERS` was not written | `git diff --name-only origin/integration...HEAD \| grep -c '^CODEOWNERS$' \| tr -d ' '` | `0` |
| F8 | No path outside `access/` touched | `git diff --name-only origin/integration...HEAD \| grep -cv '^access/' \| tr -d ' '` | `0` |

### SELF-VERIFY

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
echo "F1 $(python access/tools/validate_access_config.py | tail -1)"
echo "F2 $(bash access/codeowners/test_generate_codeowners.sh | tail -1)"
ec=0; python access/codeowners/generate_codeowners.py --org example-org --input access/testdata/codeowners/machine-login-input.json >/dev/null 2>&1 || ec=$?; echo "F3 $ec"
echo "F4 $(python access/codeowners/generate_codeowners.py --org example-org --input access/testdata/codeowners/machine-login-input.json 2>&1 >/dev/null | cut -d' ' -f1)"
echo "F5 $(python access/codeowners/generate_codeowners.py --org example-org --input access/testdata/codeowners/reference-input.json | grep -c '^[*/]')"
echo "F6 $(python access/codeowners/generate_codeowners.py --org example-org --input access/testdata/codeowners/reference-input.json | grep -Eic 'bot\]|renovate|records-writer' || true)"
echo "F7 $(git diff --name-only origin/integration...HEAD | grep -c '^CODEOWNERS$' | tr -d ' ')"
echo "F8 $(git diff --name-only origin/integration...HEAD | grep -cv '^access/' | tr -d ' ')"
```

Expected output, exactly:

```
F1 ACCESS CONFIG VALIDATION PASSED (5 documents)
F2 CODEOWNERS-NEGATIVE-TESTS: PASS (8 cases)
F3 2
F4 CODEOWNERS-REFUSED
F5 7
F6 0
F7 0
F8 0
```

### STOP

Stop and file a blocker if any of the following is true.

- `F3` prints `0`. The generator emitted a CODEOWNERS containing a bot. That is the exact condition §11.3 forbids and §98.2 tests negatively; it means a machine approval could satisfy branch protection.
- `F2` reports any failing case. Do not delete the case. Do not relax the denylist. The negative tests are the deliverable; the generator is only the thing they test.
- The generator looks like it should drop the machine entry and emit the rest. It must refuse the whole file. A CODEOWNERS silently missing a route is a routing table nobody knows is wrong.
- `F7` prints anything other than `0` — the root `CODEOWNERS` is L0's path (§0.2).

```bash
set -euo pipefail
bash access/tools/blocker.sh L5-01-06 "CODEOWNERS generator admits a machine identity" "<the failing criterion line>" "bash access/codeowners/test_generate_codeowners.sh" "<its exact output>" "CODEOWNERS-NEGATIVE-TESTS: PASS (8 cases)" "<one sentence of fact>"
```

---

## L5-01-07 — `branch-protection.yaml` — the full §11.3 checklist, unarmed/armed profiles, payload renderer

| Field | Value |
|---|---|
| Size | L |
| Depends on | L5-01-04 |
| Writes | `access/branch-protection/branch-protection.yaml`, `access/branch-protection/required-checks.md`, `access/schemas/branch-protection.schema.json`, `access/tools/render_protection_payload.py` |
| Spec | §11.3 in full (all eleven bullets); §95.2 unarmed/armed pattern; §98.2 ("The required-status-check list starts empty per repository"); §53.2 `control-plane/blocking-drift`; invariant 9; invariant 87; D89; D101 |

> **Note (§4.9):** `access/branch-protection/branch-protection.yaml` is the **estate template for product repositories**. `control-plane`'s own configuration is `docs/build/rulesets/*.json` under L0. F-07 forbids any lane adding a required context. `digest-invariant-selftest` goes on `control-plane` only, at Phase 6.

Every bullet of §11.3 becomes a row `BP-01` … `BP-11`, in the spec's own order, with an `unarmed` value and an `armed` value. §95.2 defines the unarmed configuration exactly — *require-PR and direct-push blocking stay on; required approving reviews is set to 0* — and requires the armed configuration to be recorded beside it, so arming is a configuration flip, not a build project.

Two things are never relaxed in either profile: force pushes and deletions stay blocked (BP-08), and rules apply to administrators (BP-09). The unarmed profile relaxes *independence*, not *history* (§95.3).

The required-status-check list **starts empty per repository**. §98.2 is blunt about why: a required check no workflow emits blocks every pull request indefinitely, and a list that silently stays empty is a gate that reads armed and is not. The catalogue below names the eight contexts and the phase that adds each; the renderer emits `[]` unless contexts are passed explicitly.

**Commands**

```bash
set -e
cd "$(git rev-parse --show-toplevel)"
export CONTROL_PLANE_ROOT="$PWD"
git fetch origin
git checkout integration
git pull --ff-only origin integration
test -f access/model/permission-semantics.yaml || { echo "MISSING DEPENDENCY L5-01-04"; exit 1; }
git checkout -b lane/5/p1-branch-protection
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/branch-protection/branch-protection.yaml <<'YAMLEOF'
# access/branch-protection/branch-protection.yaml
# Spec Section 11.3, the branch-protection configuration per repository, in the
# specification's own bullet order. Section 95.2 supplies the unarmed profile;
# Section 95.4 arms it. No repository name appears here (Section 11).
document: branch-protection
spec_sections: ["11.3", "95.2", "95.4", "98.2", "53.2"]
decisions: ["D89", "D101"]
invariants: [9, 87]

applies_to:
  branch: the_repository_default_branch
  repository_enumeration: dynamic_from_product_registry
  hard_coded_repository_lists: forbidden

checklist:
  - id: BP-01
    requirement: Require a pull request before merging
    unarmed: true
    armed: true

  - id: BP-02
    requirement: Require at least 1 approving review
    unarmed: 0
    armed: 1
    note: >-
      Section 95.2 defines the unarmed configuration exactly - required approving
      reviews is set to 0 while require-PR and direct-push blocking stay on.

  - id: BP-03
    requirement: Require review from Code Owners
    unarmed: false
    armed: true
    note: >-
      CODEOWNERS is generated to contain human identities only, so a
      machine-account approval can never satisfy branch protection. The Phase 1
      completion check verifies this negatively.

  - id: BP-04
    requirement: Require approval of the most recent reviewable push
    unarmed: false
    armed: true
    note: >-
      This mechanically prevents an author's own approval from satisfying the
      requirement, and is the enforcement behind the no-self-approval invariant
      (invariant 9).

  - id: BP-05
    requirement: Dismiss stale approvals when new commits are pushed
    unarmed: true
    armed: true

  - id: BP-06
    requirement: Require status checks to pass
    unarmed: contexts_start_empty
    armed: contexts_populated_as_each_check_comes_into_existence
    note: >-
      A required check no workflow emits blocks every pull request indefinitely;
      a list that silently stays empty is a gate that reads armed and is not
      (Section 98.2). See required_status_checks below.

  - id: BP-07
    requirement: Require branches to be up to date before merging
    unarmed: true
    armed: true

  - id: BP-08
    requirement: Block force pushes and deletions on the default branch
    unarmed: true
    armed: true
    never_relaxed: true
    note: >-
      Bootstrap relaxes independence requirements only. Append-only history
      holds from day one (Section 95.3).

  - id: BP-09
    requirement: Apply rules to administrators
    unarmed: true
    armed: true
    never_relaxed: true
    exception: a_documented_break_glass_procedure_with_an_audit_record
    exception_spec_section: "54"

  - id: BP-10
    requirement: Every environment carries a deployment branch and tag policy
    unarmed: true
    armed: true
    declared_in: access/environments/deployment-policies.yaml
    spec_section: "33.4"
    note: >-
      Branch protection governs what merges; the deployment branch policy governs
      what may reach an environment's secrets. Neither substitutes for the other,
      and a repository with the first and not the second holds production
      credentials behind nothing.

  - id: BP-11
    requirement: CODEOWNERS routes review requests automatically and is generated
    unarmed: true
    armed: true
    declared_in: access/codeowners/generate_codeowners.py
    note: >-
      verification/ is owned by whoever holds verification_responsibility.
      product.yaml, migration directories and CI workflow files are owned by the
      Team Lead role. Product source paths are owned by the product Team. The
      generator emits human identities only.

# BP-12 NOT ADDED: gate G2 asserts len(checklist) == 11 against §11.3's bullets,
# and signing lives in the rulesets (not branch protection).

required_status_checks:
  starts_empty_per_repository: true
  strict: true
  rationale: >-
    The required-status-check list starts empty per repository and is populated
    as each check comes into existence. Each phase's completion check names the
    contexts it adds (Section 98.2).
  emitting_lane: L2
  emitting_lane_note: >-
    This lane declares the policy. The workflows that emit these contexts are
    owned by L2 (.github/workflows/**) and are never written from here.
  catalogue:
    - context: tests
      added_at_phase: 4
    - context: build
      added_at_phase: 4
    - context: security-scan
      added_at_phase: 4
    - context: contract-validation
      added_at_phase: 4
    - context: reviewer-matrix-validation
      added_at_phase: 4
    - context: parity-check
      added_at_phase: 4
    - context: verification-contract
      added_at_phase: 5
    - context: control-plane/blocking-drift
      added_at_phase: 6
      note: >-
        The check the reconciler holds at failure while Blocking-class drift is
        open against the product (Section 53.2).
  # NOTE (§4.9): This hard-coded list is superseded. The required contexts are
  # generated from the contract (contracts/workflow-io/required-contexts.tsv).

profiles:
  unarmed:
    binding: false
    spec_section: "95.2"
    description: >-
      Configured but not yet binding on repositories covered by a bootstrap
      exception. Require-PR and direct-push blocking stay on; required approving
      reviews is 0; the workflow-identity gate is not yet enforcing.
  armed:
    binding: true
    spec_section: "95.4"
    description: >-
      Required approving reviews at the specified count and the workflow-identity
      gate active on production deploys. Arming a gate is a configuration flip,
      not a build project.
    preconditions:
      - a Team grants Write on the repository
      - CODEOWNERS exists and contains human identities only
      - the unarmed profile is already applied
    precondition_decision: D101
    precondition_rationale: >-
      Arming a Code-Owner-and-approval gate while no Team grants Write leaves
      nobody whose approval counts (Section 98.2, Section 95.4).

bypass_actors:
  control_plane_repository: none
  rationale: >-
    A ruleset bypass actor bypasses the rule wherever the rule applies; GitHub
    does not scope bypass by path. The control-plane repository admits no machine
    bypass actor, and the reconciler credential's declared repair scope is the
    only machine write path admitted (D89, Section 98.2).
YAMLEOF
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/schemas/branch-protection.schema.json <<'JSONEOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  # NEEDS_URN (FD-050): replace with urn:multiproduct:schemas:<type>:<version>
  "$id": "https://control-plane.invalid/access/branch-protection.schema.json",
  "x-target": "access/branch-protection/branch-protection.yaml",
  "title": "The Section 11.3 branch-protection checklist as declared state",
  "type": "object",
  "additionalProperties": false,
  "required": ["document", "spec_sections", "decisions", "invariants", "applies_to",
               "checklist", "required_status_checks", "profiles", "bypass_actors"],
  "properties": {
    "document": {"const": "branch-protection"},
    "spec_sections": {"type": "array", "items": {"type": "string"}, "minItems": 1},
    "decisions": {"type": "array", "items": {"type": "string"}, "minItems": 1},
    "invariants": {"type": "array", "items": {"type": "integer"}, "minItems": 1},
    "applies_to": {
      "type": "object",
      "additionalProperties": false,
      "required": ["branch", "repository_enumeration", "hard_coded_repository_lists"],
      "properties": {
        "branch": {"const": "the_repository_default_branch"},
        "repository_enumeration": {"const": "dynamic_from_product_registry"},
        "hard_coded_repository_lists": {"const": "forbidden"}
      }
    },
    "checklist": {
      "type": "array",
      "minItems": 11,
      "maxItems": 11,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["id", "requirement", "unarmed", "armed"],
        "properties": {
          "id": {"type": "string", "pattern": "^BP-(0[1-9]|1[01])$"},
          "requirement": {"type": "string", "minLength": 1},
          "unarmed": {"oneOf": [{"type": "boolean"}, {"type": "integer"}, {"type": "string"}]},
          "armed": {"oneOf": [{"type": "boolean"}, {"type": "integer"}, {"type": "string"}]},
          "note": {"type": "string"},
          "never_relaxed": {"const": true},
          "exception": {"type": "string"},
          "exception_spec_section": {"type": "string"},
          "declared_in": {"type": "string"},
          "spec_section": {"type": "string"}
        }
      }
    },
    "required_status_checks": {
      "type": "object",
      "additionalProperties": false,
      "required": ["starts_empty_per_repository", "strict", "rationale",
                   "emitting_lane", "emitting_lane_note", "catalogue"],
      "properties": {
        "starts_empty_per_repository": {"const": true},
        "strict": {"const": true},
        "rationale": {"type": "string"},
        "emitting_lane": {"const": "L2"},
        "emitting_lane_note": {"type": "string"},
        "catalogue": {
          "type": "array",
          "minItems": 8,
          "maxItems": 8,
          "items": {
            "type": "object",
            "additionalProperties": false,
            "required": ["context", "added_at_phase"],
            "properties": {
              "context": {"type": "string", "minLength": 1},
              "added_at_phase": {"type": "integer", "minimum": 4, "maximum": 6},
              "note": {"type": "string"}
            }
          }
        }
      }
    },
    "profiles": {
      "type": "object",
      "additionalProperties": false,
      "required": ["unarmed", "armed"],
      "properties": {
        "unarmed": {
          "type": "object",
          "additionalProperties": false,
          "required": ["binding", "spec_section", "description"],
          "properties": {
            "binding": {"const": false},
            "spec_section": {"const": "95.2"},
            "description": {"type": "string"}
          }
        },
        "armed": {
          "type": "object",
          "additionalProperties": false,
          "required": ["binding", "spec_section", "description", "preconditions",
                       "precondition_decision", "precondition_rationale"],
          "properties": {
            "binding": {"const": true},
            "spec_section": {"const": "95.4"},
            "description": {"type": "string"},
            "preconditions": {"type": "array", "minItems": 3, "items": {"type": "string"}},
            "precondition_decision": {"const": "D101"},
            "precondition_rationale": {"type": "string"}
          }
        }
      }
    },
    "bypass_actors": {
      "type": "object",
      "additionalProperties": false,
      "required": ["control_plane_repository", "rationale"],
      "properties": {
        "control_plane_repository": {"const": "none"},
        "rationale": {"type": "string"}
      }
    }
  }
}
JSONEOF
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/tools/render_protection_payload.py <<'PYEOF'
#!/usr/bin/env python
"""Render the literal GitHub branch-protection API payload for one profile.

Published interface (plan file section 0.3). Consumed by L3 provisioning and by
access/runbooks/apply-branch-protection.sh. It never talks to GitHub: it turns
access/branch-protection/branch-protection.yaml plus a profile name into the JSON
body of PUT /repos/{owner}/{repo}/branches/{branch}/protection.

The required-status-check context list starts EMPTY (Section 98.2). Contexts are
supplied explicitly with --contexts and must be drawn from the declared
catalogue: a context no workflow emits blocks every pull request indefinitely.

Usage:
  render_protection_payload.py --profile {unarmed,armed} [--contexts a,b]
                               [--config PATH]
Exit codes:
  0  payload written to stdout as JSON
  3  bad arguments or unreadable configuration
  4  a requested context is not in the declared catalogue
"""
import argparse
import json
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DEFAULT = os.path.join(ROOT, "access", "branch-protection", "branch-protection.yaml")


def row(doc, ident):
    for entry in doc["checklist"]:
        if entry["id"] == ident:
            return entry
    sys.stderr.write("RENDER-ERROR checklist row %s missing\n" % ident)
    sys.exit(3)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=["unarmed", "armed"], required=True)
    parser.add_argument("--contexts", default="")
    parser.add_argument("--config", default=DEFAULT)
    args = parser.parse_args()

    with open(args.config, "r", encoding="utf-8") as handle:
        doc = yaml.safe_load(handle)

    catalogue = [entry["context"] for entry in doc["required_status_checks"]["catalogue"]]
    requested = [item.strip() for item in args.contexts.split(",") if item.strip()]
    unknown = [item for item in requested if item not in catalogue]
    if unknown:
        sys.stderr.write("RENDER-ERROR context not in the declared catalogue: %s\n"
                         % ", ".join(unknown))
        return 4

    profile = args.profile
    payload = {
        "required_status_checks": {
            "strict": bool(doc["required_status_checks"]["strict"]),
            "contexts": requested,
        },
        "enforce_admins": bool(row(doc, "BP-09")[profile]),
        "required_pull_request_reviews": {
            "dismiss_stale_reviews": bool(row(doc, "BP-05")[profile]),
            "require_code_owner_reviews": bool(row(doc, "BP-03")[profile]),
            "required_approving_review_count": int(row(doc, "BP-02")[profile]),
            "require_last_push_approval": bool(row(doc, "BP-04")[profile]),
        },
        "restrictions": None,
        "allow_force_pushes": not bool(row(doc, "BP-08")[profile]),
        "allow_deletions": not bool(row(doc, "BP-08")[profile]),
    }
    sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
PYEOF
chmod +x access/tools/render_protection_payload.py
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/branch-protection/required-checks.md <<'EOF'
# Required status checks — the list starts empty, per repository

Spec §98.2, Phase 1: *"The required-status-check list starts empty per repository
and is populated as each check comes into existence — CI checks at that product's
Phase 4, the verification contract at Phase 5, the pipeline checks at Phase 6. A
required check no workflow emits blocks every pull request indefinitely; a list
that silently stays empty is a gate that reads armed and is not. Each phase's
completion check names the contexts it adds."*

Both halves of that sentence are load-bearing, and they pull in opposite
directions. Adding a context early blocks every pull request on the repository
until the emitting workflow exists. Never adding one leaves a gate that reads
armed and is not. The resolution is the catalogue: the contexts are declared
here from Phase 1, and each is **added to a repository only at the phase that
brings its workflow into existence**.

| Context | Added at | Emitted by |
|---|---|---|
| `tests` | that product's Phase 4 | L2 reusable workflow |
| `build` | that product's Phase 4 | L2 reusable workflow |
| `security-scan` | that product's Phase 4 | L2 reusable workflow |
| `contract-validation` | that product's Phase 4 | L2 reusable workflow |
| `reviewer-matrix-validation` | that product's Phase 4 | L2 reusable workflow |
| `parity-check` | that product's Phase 4 | L2 reusable workflow |
| `verification-contract` | that product's Phase 5 | L2 reusable workflow |
| `control-plane/blocking-drift` | that product's Phase 6 | the reconciler (L3), surfaced as a check |

**This lane emits none of them.** `.github/workflows/**` is L2's path and
`reconciler/**` is L3's (§0.2). L5 declares the policy and renders the payload;
adding a context to a live repository is an apply-time step in
`access/runbooks/apply-branch-protection.sh`, and it is legitimate only once
`gh api /repos/$ORG_LOGIN/<repo>/commits/<sha>/check-runs` shows the context
actually reported by a run — which is exactly what the phase completion checks of
§98.2 Phases 4, 5 and 6 verify.
EOF
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
python access/tools/validate_access_config.py
python access/tools/render_protection_payload.py --profile unarmed
python access/tools/render_protection_payload.py --profile armed
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
git add access
git commit -m "$(printf 'L5-01-07: branch-protection.yaml - the Section 11.3 checklist, unarmed and armed profiles, payload renderer\n\nLane: L5\n')"
git push -u origin lane/5/p1-branch-protection
```

### Acceptance criteria

| # | Criterion | Proving command | Expected output |
|---|---|---|---|
| G1 | All six documents validate | `python access/tools/validate_access_config.py \| tail -1` | `ACCESS CONFIG VALIDATION PASSED (6 documents)` |
| G2 | All eleven §11.3 bullets are present | `python -c "import yaml;print(len(yaml.safe_load(open('access/branch-protection/branch-protection.yaml'))['checklist']))"` | `11` |
| G3 | Unarmed requires 0 approving reviews | `python access/tools/render_protection_payload.py --profile unarmed \| python -c "import json,sys;print(json.load(sys.stdin)['required_pull_request_reviews']['required_approving_review_count'])"` | `0` |
| G4 | Armed requires 1 | `python access/tools/render_protection_payload.py --profile armed \| python -c "import json,sys;print(json.load(sys.stdin)['required_pull_request_reviews']['required_approving_review_count'])"` | `1` |
| G5 | Armed requires Code Owner review and most-recent-push approval | `python access/tools/render_protection_payload.py --profile armed \| python -c "import json,sys;d=json.load(sys.stdin)['required_pull_request_reviews'];print(d['require_code_owner_reviews'],d['require_last_push_approval'])"` | `True True` |
| G6 | Force pushes and deletions are blocked, and rules apply to administrators, in BOTH profiles | see SELF-VERIFY | `False False True` on both lines |
| G7 | The context list starts empty | `python access/tools/render_protection_payload.py --profile armed \| python -c "import json,sys;print(len(json.load(sys.stdin)['required_status_checks']['contexts']))"` | `0` |
| G8 | A context outside the catalogue is refused | `python access/tools/render_protection_payload.py --profile armed --contexts not-a-real-check >/dev/null 2>&1; echo $?` | `4` |
| G9 | The eight catalogue contexts are declared | `python -c "import yaml;print(len(yaml.safe_load(open('access/branch-protection/branch-protection.yaml'))['required_status_checks']['catalogue']))"` | `8` |
| G10 | The control-plane repository admits no bypass actor (D89) | `python -c "import yaml;print(yaml.safe_load(open('access/branch-protection/branch-protection.yaml'))['bypass_actors']['control_plane_repository'])"` | `none` |
| G11 | No path outside `access/` touched | `git diff --name-only origin/integration...HEAD \| grep -cv '^access/' \| tr -d ' '` | `0` |

### SELF-VERIFY

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
echo "G1 $(python access/tools/validate_access_config.py | tail -1)"
echo "G2 $(python -c "import yaml;print(len(yaml.safe_load(open('access/branch-protection/branch-protection.yaml'))['checklist']))")"
echo "G3 $(python access/tools/render_protection_payload.py --profile unarmed | python -c "import json,sys;print(json.load(sys.stdin)['required_pull_request_reviews']['required_approving_review_count'])")"
echo "G4 $(python access/tools/render_protection_payload.py --profile armed | python -c "import json,sys;print(json.load(sys.stdin)['required_pull_request_reviews']['required_approving_review_count'])")"
echo "G5 $(python access/tools/render_protection_payload.py --profile armed | python -c "import json,sys;d=json.load(sys.stdin)['required_pull_request_reviews'];print(d['require_code_owner_reviews'],d['require_last_push_approval'])")"
for p in unarmed armed; do
  echo "G6 $(python access/tools/render_protection_payload.py --profile $p | python -c "import json,sys;d=json.load(sys.stdin);print(d['allow_force_pushes'],d['allow_deletions'],d['enforce_admins'])")"
done
echo "G7 $(python access/tools/render_protection_payload.py --profile armed | python -c "import json,sys;print(len(json.load(sys.stdin)['required_status_checks']['contexts']))")"
ec=0; python access/tools/render_protection_payload.py --profile armed --contexts not-a-real-check >/dev/null 2>&1 || ec=$?; echo "G8 $ec"
echo "G9 $(python -c "import yaml;print(len(yaml.safe_load(open('access/branch-protection/branch-protection.yaml'))['required_status_checks']['catalogue']))")"
echo "G10 $(python -c "import yaml;print(yaml.safe_load(open('access/branch-protection/branch-protection.yaml'))['bypass_actors']['control_plane_repository'])")"
echo "G11 $(git diff --name-only origin/integration...HEAD | grep -cv '^access/' | tr -d ' ')"
```

Expected output, exactly:

```
G1 ACCESS CONFIG VALIDATION PASSED (6 documents)
G2 11
G3 0
G4 1
G5 True True
G6 False False True
G6 False False True
G7 0
G8 4
G9 8
G10 none
G11 0
```

### STOP

Stop and file a blocker if any of the following is true.

- `G6` prints `True` in the first or second column on either line. Bootstrap relaxes independence requirements only; append-only history holds from day one (§95.3). Force pushes and deletions are not a profile difference.
- `G6` prints `False` in the third column on either line. "Apply rules to administrators" has exactly one exception and it is a documented break-glass procedure with an audit record (§54) — never a profile.
- `G7` prints anything other than `0`. A required context that no workflow emits blocks every pull request on the repository indefinitely (§98.2).
- `G8` prints `0`. The renderer accepted an undeclared context, which is the same failure by a different route.
- A required status check looks like it should be added now because "the workflow will exist soon". It does not exist. Do not add it.

```bash
set -euo pipefail
bash access/tools/blocker.sh L5-01-07 "branch-protection profiles do not render correctly" "<the failing criterion line>" "python access/tools/render_protection_payload.py --profile armed" "<its exact output>" "<the expected line from the SELF-VERIFY block>" "<one sentence of fact>"
```

---

## L5-01-08 — `deployment-policies.yaml` — the §33.4 deployment branch and tag policy

| Field | Value |
|---|---|
| Size | M |
| Depends on | L5-01-07 |
| Writes | `access/environments/deployment-policies.yaml`, `access/schemas/deployment-policies.schema.json`, `access/tools/render_environment_payload.py` |
| Spec | §33.4 ("Every environment carries a deployment branch and tag policy, applied from the template at product creation"); §11.3 bullet BP-10; §11.4; §27.2; §40.3; §98.2 Phase 1; D73 |

§11.3 states the consequence plainly and this task exists to make it false: *"a repository with the first and not the second holds production credentials behind nothing."* Branch protection governs what merges. The deployment branch policy governs what may reach an environment's secrets. Without the second, any Write holder pushes a branch carrying a workflow that declares `environment: production` and GitHub hands that job the environment's secrets from an unreviewed ref — and the same absence lets a Write holder delete the workflow-identity gate on their own branch and dispatch the deploy from it.

Deployment branch policies are available on the Team plan and are **not** the Enterprise feature §11.4 excludes. Environment *required reviewers* are the Enterprise feature, and this document declares that they are not used (D73). The renderer never emits a `reviewers` key, and criterion **`H6` proves it by execution**.

**Commands**

```bash
set -e
cd "$(git rev-parse --show-toplevel)"
export CONTROL_PLANE_ROOT="$PWD"
git fetch origin
git checkout integration
git pull --ff-only origin integration
test -f access/branch-protection/branch-protection.yaml || { echo "MISSING DEPENDENCY L5-01-07"; exit 1; }
git checkout -b lane/5/p1-deployment-policies
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/environments/deployment-policies.yaml <<'YAMLEOF'
# access/environments/deployment-policies.yaml
# Spec Section 33.4 and Section 11.3 bullet BP-10. The deployment branch and tag
# policy for every environment, applied from the template at product creation.
# No repository name and no organisation login appear here (Section 11).
document: deployment-policies
spec_sections: ["33.4", "11.3", "11.4", "27.2", "40.3", "98.2"]
decisions: ["D73"]

applies_to:
  environments_created_from: the_product_template_at_product_creation
  repository_enumeration: dynamic_from_product_registry
  hard_coded_repository_lists: forbidden

environments:
  - name: development
    restricted: false
    accepted_refs: []
    secrets_scope: environment_scoped
    note: >-
      Section 33.4 restricts staging and production. Development carries
      environment-scoped secrets like the others and no ref restriction.

  - name: staging
    restricted: true
    accepted_refs:
      - kind: branch
        value: the_repository_default_branch
      - kind: tag
        value: protected_release_tags
    accepts_no_other_ref: true
    secrets_scope: environment_scoped

  - name: production
    restricted: true
    accepted_refs:
      - kind: branch
        value: the_repository_default_branch
      - kind: tag
        value: protected_release_tags
    accepts_no_other_ref: true
    secrets_scope: environment_scoped
    approval_mechanism: workflow_identity_gate
    approval_spec_section: "27.2"

required_reviewers:
  used: false
  reason: >-
    Environment deployment protection rules - required reviewers, wait timers -
    are a GitHub Enterprise feature and are not available on the Team plan for
    private repositories. They are an optional strengthening behind a recorded
    Founder budget decision, never the mechanism the estate depends on (D73).

wait_timers:
  used: false
  reason: >-
    Same plan-tier fact as required reviewers (Section 11.4, D73).

why_this_is_not_optional: >-
  Without a deployment branch policy, any Write holder - or anyone who
  compromises a Write holder's workstation - pushes a branch carrying a workflow
  that declares environment production, and GitHub hands that job the
  environment's secrets from an unreviewed ref. The same absence lets a Write
  holder delete the workflow-identity gate on their own branch and dispatch the
  deploy from it: the gate is code, and the ref restriction is what stops the
  gated actor choosing which code runs (Section 33.4).

tag_policy:
  protected_release_tags_required: true
  pattern_source: supplied_at_apply_time_from_the_product_registry
  note: >-
    "Protected release tags" is only true where a tag ruleset protects the
    release-tag pattern. The pattern is product data and arrives at apply time;
    it is never a literal in this tree.

negative_test:
  id: NEG-04
  statement: >-
    A workflow pushed to a non-default branch declaring environment production
    obtains no environment secret.
  spec_section: "98.2"
  declared_here: the_environment_configuration_that_makes_it_true
  executed_by: L2
  executed_by_reason: >-
    Executing it requires pushing a workflow file. .github/workflows/** is L2's
    path; this lane declares the configuration and never writes the workflow.
YAMLEOF
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/schemas/deployment-policies.schema.json <<'JSONEOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  # NEEDS_URN (FD-050): replace with urn:multiproduct:schemas:<type>:<version>
  "$id": "https://control-plane.invalid/access/deployment-policies.schema.json",
  "x-target": "access/environments/deployment-policies.yaml",
  "title": "Deployment branch and tag policy per environment (spec Section 33.4)",
  "type": "object",
  "additionalProperties": false,
  "required": ["document", "spec_sections", "decisions", "applies_to", "environments",
               "required_reviewers", "wait_timers", "why_this_is_not_optional",
               "tag_policy", "negative_test"],
  "properties": {
    "document": {"const": "deployment-policies"},
    "spec_sections": {"type": "array", "items": {"type": "string"}, "minItems": 1},
    "decisions": {"type": "array", "items": {"type": "string"}, "minItems": 1},
    "applies_to": {
      "type": "object",
      "additionalProperties": false,
      "required": ["environments_created_from", "repository_enumeration",
                   "hard_coded_repository_lists"],
      "properties": {
        "environments_created_from": {"const": "the_product_template_at_product_creation"},
        "repository_enumeration": {"const": "dynamic_from_product_registry"},
        "hard_coded_repository_lists": {"const": "forbidden"}
      }
    },
    "environments": {
      "type": "array",
      "minItems": 3,
      "maxItems": 3,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["name", "restricted", "accepted_refs", "secrets_scope"],
        "properties": {
          "name": {"enum": ["development", "staging", "production"]},
          "restricted": {"type": "boolean"},
          "accepted_refs": {
            "type": "array",
            "items": {
              "type": "object",
              "additionalProperties": false,
              "required": ["kind", "value"],
              "properties": {
                "kind": {"enum": ["branch", "tag"]},
                "value": {"enum": ["the_repository_default_branch", "protected_release_tags"]}
              }
            }
          },
          "accepts_no_other_ref": {"const": true},
          "secrets_scope": {"const": "environment_scoped"},
          "approval_mechanism": {"const": "workflow_identity_gate"},
          "approval_spec_section": {"const": "27.2"},
          "note": {"type": "string"}
        }
      }
    },
    "required_reviewers": {
      "type": "object",
      "additionalProperties": false,
      "required": ["used", "reason"],
      "properties": {"used": {"const": false}, "reason": {"type": "string"}}
    },
    "wait_timers": {
      "type": "object",
      "additionalProperties": false,
      "required": ["used", "reason"],
      "properties": {"used": {"const": false}, "reason": {"type": "string"}}
    },
    "why_this_is_not_optional": {"type": "string"},
    "tag_policy": {
      "type": "object",
      "additionalProperties": false,
      "required": ["protected_release_tags_required", "pattern_source", "note"],
      "properties": {
        "protected_release_tags_required": {"const": true},
        "pattern_source": {"const": "supplied_at_apply_time_from_the_product_registry"},
        "note": {"type": "string"}
      }
    },
    "negative_test": {
      "type": "object",
      "additionalProperties": false,
      "required": ["id", "statement", "spec_section", "declared_here",
                   "executed_by", "executed_by_reason"],
      "properties": {
        "id": {"const": "NEG-04"},
        "statement": {"type": "string"},
        "spec_section": {"const": "98.2"},
        "declared_here": {"const": "the_environment_configuration_that_makes_it_true"},
        "executed_by": {"const": "L2"},
        "executed_by_reason": {"type": "string"}
      }
    }
  }
}
JSONEOF
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/tools/render_environment_payload.py <<'PYEOF'
#!/usr/bin/env python
"""Render the GitHub environment payload and its deployment branch policies.

Turns access/environments/deployment-policies.yaml plus one environment name into
the literal bodies of:
  PUT  /repos/{owner}/{repo}/environments/{name}
  POST /repos/{owner}/{repo}/environments/{name}/deployment-branch-policies

It never emits a "reviewers" key and never emits a wait timer. Environment
required reviewers are Enterprise-only on private repositories and are not
depended on; production approval is the Section 27.2 workflow-identity gate (D73).

Usage:
  render_environment_payload.py --environment {development,staging,production}
                                --default-branch NAME
                                --release-tag-pattern PATTERN
                                [--config PATH]
Exit codes:
  0  JSON written to stdout
  3  bad arguments, unreadable configuration, or an unknown environment
"""
import argparse
import json
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DEFAULT = os.path.join(ROOT, "access", "environments", "deployment-policies.yaml")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--environment", required=True)
    parser.add_argument("--default-branch", default="main")
    parser.add_argument("--release-tag-pattern", default="v*")
    parser.add_argument("--config", default=DEFAULT)
    args = parser.parse_args()

    with open(args.config, "r", encoding="utf-8") as handle:
        doc = yaml.safe_load(handle)

    match = None
    for entry in doc["environments"]:
        if entry["name"] == args.environment:
            match = entry
    if match is None:
        sys.stderr.write("RENDER-ERROR unknown environment %r\n" % args.environment)
        return 3

    if match["restricted"]:
        environment_payload = {
            "deployment_branch_policy": {
                "protected_branches": False,
                "custom_branch_policies": True,
            }
        }
        policies = []
        for ref in match["accepted_refs"]:
            if ref["value"] == "the_repository_default_branch":
                policies.append({"name": args.default_branch, "type": "branch"})
            elif ref["value"] == "protected_release_tags":
                policies.append({"name": args.release_tag_pattern, "type": "tag"})
    else:
        environment_payload = {"deployment_branch_policy": None}
        policies = []

    out = {
        "environment": match["name"],
        "environment_payload": environment_payload,
        "deployment_branch_policies": policies,
        "required_reviewers_used": bool(doc["required_reviewers"]["used"]),
        "approval_mechanism": match.get("approval_mechanism", "not_applicable"),
    }
    sys.stdout.write(json.dumps(out, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
PYEOF
chmod +x access/tools/render_environment_payload.py
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
python access/tools/validate_access_config.py
python access/tools/render_environment_payload.py --environment production \
  --default-branch main --release-tag-pattern 'v*'
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
git add access
git commit -m "$(printf 'L5-01-08: deployment-policies.yaml - the Section 33.4 deployment branch and tag policy\n\nLane: L5\n')"
git push -u origin lane/5/p1-deployment-policies
```

### Acceptance criteria

| # | Criterion | Proving command | Expected output |
|---|---|---|---|
| H1 | All seven documents validate | `python access/tools/validate_access_config.py \| tail -1` | `ACCESS CONFIG VALIDATION PASSED (7 documents)` |
| H2 | Three environments are declared | `python -c "import yaml;print(len(yaml.safe_load(open('access/environments/deployment-policies.yaml'))['environments']))"` | `3` |
| H3 | Production is restricted | `python -c "import yaml;d=yaml.safe_load(open('access/environments/deployment-policies.yaml'));print([e for e in d['environments'] if e['name']=='production'][0]['restricted'])"` | `True` |
| H4 | Production accepts exactly the default branch and protected release tags | `python access/tools/render_environment_payload.py --environment production --default-branch main --release-tag-pattern 'v*' \| python -c "import json,sys;print(json.dumps(json.load(sys.stdin)['deployment_branch_policies']))"` | `[{"name": "main", "type": "branch"}, {"name": "v*", "type": "tag"}]` |
| H5 | Staging is restricted on the same terms | `python access/tools/render_environment_payload.py --environment staging --default-branch main --release-tag-pattern 'v*' \| python -c "import json,sys;print(len(json.load(sys.stdin)['deployment_branch_policies']))"` | `2` |
| H6 | No environment-reviewer key is ever emitted (D73) | see SELF-VERIFY | `0` |
| H7 | Required reviewers are declared unused | `python -c "import yaml;print(yaml.safe_load(open('access/environments/deployment-policies.yaml'))['required_reviewers']['used'])"` | `False` |
| H8 | Production approval is the workflow-identity gate | `python -c "import yaml;d=yaml.safe_load(open('access/environments/deployment-policies.yaml'));print([e for e in d['environments'] if e['name']=='production'][0]['approval_mechanism'])"` | `workflow_identity_gate` |
| H9 | No path outside `access/` touched | `git diff --name-only origin/integration...HEAD \| grep -cv '^access/' \| tr -d ' '` | `0` |

### SELF-VERIFY

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
echo "H1 $(python access/tools/validate_access_config.py | tail -1)"
echo "H2 $(python -c "import yaml;print(len(yaml.safe_load(open('access/environments/deployment-policies.yaml'))['environments']))")"
echo "H3 $(python -c "import yaml;d=yaml.safe_load(open('access/environments/deployment-policies.yaml'));print([e for e in d['environments'] if e['name']=='production'][0]['restricted'])")"
echo "H4 $(python access/tools/render_environment_payload.py --environment production --default-branch main --release-tag-pattern 'v*' | python -c "import json,sys;print(json.dumps(json.load(sys.stdin)['deployment_branch_policies']))")"
echo "H5 $(python access/tools/render_environment_payload.py --environment staging --default-branch main --release-tag-pattern 'v*' | python -c "import json,sys;print(len(json.load(sys.stdin)['deployment_branch_policies']))")"
echo "H6 $(for e in development staging production; do python access/tools/render_environment_payload.py --environment $e --default-branch main --release-tag-pattern 'v*'; done | grep -c '"reviewers"' || true)"
echo "H7 $(python -c "import yaml;print(yaml.safe_load(open('access/environments/deployment-policies.yaml'))['required_reviewers']['used'])")"
echo "H8 $(python -c "import yaml;d=yaml.safe_load(open('access/environments/deployment-policies.yaml'));print([e for e in d['environments'] if e['name']=='production'][0]['approval_mechanism'])")"
echo "H9 $(git diff --name-only origin/integration...HEAD | grep -cv '^access/' | tr -d ' ')"
```

Expected output, exactly:

```
H1 ACCESS CONFIG VALIDATION PASSED (7 documents)
H2 3
H3 True
H4 [{"name": "main", "type": "branch"}, {"name": "v*", "type": "tag"}]
H5 2
H6 0
H7 False
H8 workflow_identity_gate
H9 0
```

### STOP

Stop and file a blocker if any of the following is true.

- `H3` prints `False`. A production environment with no deployment branch policy holds production credentials behind nothing (§11.3, §33.4).
- `H6` prints anything other than `0`. The renderer emitted an environment required-reviewer key. That feature is Enterprise-only on private repositories and the estate does not depend on it (§11.4, D73); production approval is the §27.2 workflow-identity gate.
- The deployment branch policy looks like "the same feature" as environment required reviewers and therefore skippable on the Team plan. §33.4 states the opposite in as many words: deployment branch policies are available on the Team plan and are **not** the Enterprise feature §11.4 excludes.

```bash
set -euo pipefail
bash access/tools/blocker.sh L5-01-08 "deployment branch and tag policy is wrong or absent" "<the failing criterion line>" "python access/tools/render_environment_payload.py --environment production --default-branch main --release-tag-pattern 'v*'" "<its exact output>" "<the expected line from the SELF-VERIFY block>" "<one sentence of fact>"
```

---

## L5-01-09 — `plan-tier.yaml` — the §11.4 table with a depended-on checker

| Field | Value |
|---|---|
| Size | M |
| Depends on | L5-01-07, and L5-01-08 for the executed cross-document assertion |
| Writes | `access/plan-tier/plan-tier.yaml`, `access/schemas/plan-tier.schema.json`, `access/tools/check_no_enterprise_dependency.py` |
| Spec | §11.4 (all five rows); §33.4 (deployment branch policies are on the Team plan); §27.2; §99.6 "Plan-tier posture is settled (D73)"; D73 |

The §11.4 table is transcribed as five rows, `PT-01` … `PT-05`, plus one row `PT-06` sourced from §33.4 and labelled as such — its `source_section` says `33.4`, so nobody can mistake it for an invented §11.4 row.

Each row records two separate facts, and conflating them is the mistake this checker exists to catch:

* `enterprise_only` — is the *named GitHub feature* an Enterprise feature?
* `enterprise_mechanism_depended_on` — does the estate *depend on that Enterprise mechanism*?

`check_no_enterprise_dependency.py` fails when both are true for any row. That is the whole check, and §99.6 is what it enforces: *plan-tier posture is settled*.

The §0.8 index names `T07` as this task's dependency, which is the schema-level one. The checker additionally reads `access/environments/deployment-policies.yaml` for assertions `PT-A2`, `PT-A3` and `PT-A4`, so `T08` must also have merged. Executing the tasks in the order §0.5 mandates satisfies both without a decision.

**Commands**

```bash
set -e
cd "$(git rev-parse --show-toplevel)"
export CONTROL_PLANE_ROOT="$PWD"
git fetch origin
git checkout integration
git pull --ff-only origin integration
test -f access/environments/deployment-policies.yaml || { echo "MISSING DEPENDENCY L5-01-08"; exit 1; }
git checkout -b lane/5/p1-plan-tier
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/plan-tier/plan-tier.yaml <<'YAMLEOF'
# access/plan-tier/plan-tier.yaml
# Spec Section 11.4, "Implementation dependencies - plan-tier facts", transcribed
# as PT-01..PT-05. PT-06 is sourced from Section 33.4 and says so in its
# source_section: it is not an invented Section 11.4 row.
document: plan-tier
spec_sections: ["11.4", "33.4", "27.2", "99.6"]
decisions: ["D73"]

posture: settled

rows:
  - id: PT-01
    source_section: "11.4"
    capability: Branch protection or rulesets on private repositories
    plan_tier_fact: available_on_the_team_plan
    enterprise_only: false
    enterprise_mechanism_depended_on: false
    mechanism_of_record: Configured as specified in Section 11.3
    note: >-
      Non-negotiable; the one item that forces a paid plan.

  - id: PT-02
    source_section: "11.4"
    capability: Environment deployment protection rules (required reviewers, wait timers) on private repositories
    plan_tier_fact: a_github_enterprise_feature_not_available_on_the_team_plan
    enterprise_only: true
    enterprise_mechanism_depended_on: false
    mechanism_of_record: The Section 27.2 workflow-identity gate
    note: >-
      The deploy workflow verifies that the recorded approving identity differs
      from the deploying identity and fails closed. This is the
      production-approval mechanism of record - the design, not a fallback.
      Buying Enterprise is a recorded Founder budget decision that would add
      environment required reviewers as a strengthening (D73).

  - id: PT-03
    source_section: "11.4"
    capability: Custom repository roles (approval authority without branch push)
    plan_tier_fact: github_enterprise_cloud_only
    enterprise_only: true
    enterprise_mechanism_depended_on: false
    mechanism_of_record: Write via Teams as specified
    note: >-
      If custom repository roles were available, a role inheriting Read plus
      approval permission would be strictly better for Cross-Reviewers than
      Write. The specification assumes the Write configuration because it works
      on the Team plan.

  - id: PT-04
    source_section: "11.4"
    capability: Self-review prevention on production deployment
    plan_tier_fact: environment_required_reviewers_are_enterprise_only_on_private_repositories
    enterprise_only: true
    enterprise_mechanism_depended_on: false
    mechanism_of_record: >-
      The same Section 27.2 workflow-identity gate; branch protection's
      most-recent-push approval rule covers the review side (Section 11.3)

  - id: PT-05
    source_section: "11.4"
    capability: Outside collaborator scoping for contractors
    plan_tier_fact: available_on_all_tiers
    enterprise_only: false
    enterprise_mechanism_depended_on: false
    mechanism_of_record: Scoped access per Section 11.2

  - id: PT-06
    source_section: "33.4"
    capability: Environment deployment branch and tag policies
    plan_tier_fact: available_on_the_team_plan
    enterprise_only: false
    enterprise_mechanism_depended_on: false
    mechanism_of_record: Configured as specified in access/environments/deployment-policies.yaml
    note: >-
      Deployment branch policies are available on the Team plan and are NOT the
      Enterprise feature Section 11.4 excludes (Section 33.4). Confusing the two
      is how a production environment ends up with no ref restriction.

cross_document_assertions:
  - id: PT-X1
    statement: access/environments/deployment-policies.yaml declares required reviewers unused
    document: access/environments/deployment-policies.yaml
  - id: PT-X2
    statement: the environment payload renderer emits no environment-reviewer key
    tool: access/tools/render_environment_payload.py
YAMLEOF
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/schemas/plan-tier.schema.json <<'JSONEOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  # NEEDS_URN (FD-050): replace with urn:multiproduct:schemas:<type>:<version>
  "$id": "https://control-plane.invalid/access/plan-tier.schema.json",
  "x-target": "access/plan-tier/plan-tier.yaml",
  "title": "Plan-tier facts and what the estate does not depend on (spec Section 11.4, D73)",
  "type": "object",
  "additionalProperties": false,
  "required": ["document", "spec_sections", "decisions", "posture", "rows",
               "cross_document_assertions"],
  "properties": {
    "document": {"const": "plan-tier"},
    "spec_sections": {"type": "array", "items": {"type": "string"}, "minItems": 1},
    "decisions": {"type": "array", "items": {"type": "string"}, "minItems": 1},
    "posture": {"const": "settled"},
    "rows": {
      "type": "array",
      "minItems": 6,
      "maxItems": 6,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["id", "source_section", "capability", "plan_tier_fact",
                     "enterprise_only", "enterprise_mechanism_depended_on",
                     "mechanism_of_record"],
        "properties": {
          "id": {"type": "string", "pattern": "^PT-0[1-6]$"},
          "source_section": {"enum": ["11.4", "33.4"]},
          "capability": {"type": "string", "minLength": 1},
          "plan_tier_fact": {"type": "string", "minLength": 1},
          "enterprise_only": {"type": "boolean"},
          "enterprise_mechanism_depended_on": {"const": false},
          "mechanism_of_record": {"type": "string", "minLength": 1},
          "note": {"type": "string"}
        }
      }
    },
    "cross_document_assertions": {
      "type": "array",
      "minItems": 2,
      "maxItems": 2,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["id", "statement"],
        "properties": {
          "id": {"type": "string", "pattern": "^PT-X[12]$"},
          "statement": {"type": "string"},
          "document": {"type": "string"},
          "tool": {"type": "string"}
        }
      }
    }
  }
}
JSONEOF
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/tools/check_no_enterprise_dependency.py <<'PYEOF'
#!/usr/bin/env python
"""Prove that nothing in access/** depends on a GitHub Enterprise-only feature.

Spec Section 99.6: "Plan-tier posture is settled (D73): branch protection on
private repositories requires the Team plan - non-negotiable, verified.
Environment required reviewers are Enterprise-only and are not depended on."

Four assertions:
  PT-A1  no row is both enterprise_only and enterprise_mechanism_depended_on
  PT-A2  the deployment-policies document declares required reviewers unused
  PT-A3  the deployment-policies document declares wait timers unused
  PT-A4  the environment payload renderer reports required_reviewers_used false
         for every environment -- executed, not asserted

Usage: check_no_enterprise_dependency.py [--config PATH]
Exit 0 on success, 1 on any failed assertion.
"""
import argparse
import json
import os
import subprocess
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DEFAULT = os.path.join(ROOT, "access", "plan-tier", "plan-tier.yaml")
DEPLOY = os.path.join(ROOT, "access", "environments", "deployment-policies.yaml")
RENDER = os.path.join(ROOT, "access", "tools", "render_environment_payload.py")


def renders_without_reviewers():
    for environment in ("development", "staging", "production"):
        result = subprocess.run(
            [sys.executable, RENDER, "--environment", environment,
             "--default-branch", "main", "--release-tag-pattern", "v*"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            return False
        payload = json.loads(result.stdout.decode("utf-8"))
        if payload.get("required_reviewers_used") is not False:
            return False
        if "reviewers" in json.dumps(payload["environment_payload"]):
            return False
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=DEFAULT)
    args = parser.parse_args()

    with open(args.config, "r", encoding="utf-8") as handle:
        doc = yaml.safe_load(handle)
    with open(DEPLOY, "r", encoding="utf-8") as handle:
        deploy = yaml.safe_load(handle)

    offenders = [row["id"] for row in doc["rows"]
                 if row["enterprise_only"] and row["enterprise_mechanism_depended_on"]]

    assertions = [
        ("PT-A1", "no row depends on an Enterprise-only mechanism", offenders == []),
        ("PT-A2", "environment required reviewers are declared unused",
         deploy["required_reviewers"]["used"] is False),
        ("PT-A3", "environment wait timers are declared unused",
         deploy["wait_timers"]["used"] is False),
        ("PT-A4", "the environment payload renderer depends on no reviewer feature",
         renders_without_reviewers()),
    ]

    failed = 0
    for ident, statement, ok in assertions:
        if not ok:
            print("FAIL %s: %s" % (ident, statement))
            failed += 1
    if offenders:
        print("       offending rows: %s" % ", ".join(offenders))
    if failed:
        print("PLAN-TIER: FAIL (%d of %d assertions)" % (failed, len(assertions)))
        return 1
    print("PLAN-TIER: PASS (%d assertions)" % len(assertions))
    return 0


if __name__ == "__main__":
    sys.exit(main())
PYEOF
chmod +x access/tools/check_no_enterprise_dependency.py
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
python access/tools/validate_access_config.py
python access/tools/check_no_enterprise_dependency.py
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
git add access
git commit -m "$(printf 'L5-01-09: plan-tier.yaml - the Section 11.4 table with a depended-on checker\n\nLane: L5\n')"
git push -u origin lane/5/p1-plan-tier
```

### Acceptance criteria

| # | Criterion | Proving command | Expected output |
|---|---|---|---|
| I1 | All eight documents validate | `python access/tools/validate_access_config.py \| tail -1` | `ACCESS CONFIG VALIDATION PASSED (8 documents)` |
| I2 | All four plan-tier assertions hold | `python access/tools/check_no_enterprise_dependency.py` | `PLAN-TIER: PASS (4 assertions)` |
| I3 | Six rows: the five of §11.4 plus the §33.4 row | `python -c "import yaml;print(len(yaml.safe_load(open('access/plan-tier/plan-tier.yaml'))['rows']))"` | `6` |
| I4 | Exactly five rows are sourced from §11.4 | `python -c "import yaml;d=yaml.safe_load(open('access/plan-tier/plan-tier.yaml'));print(sum(1 for r in d['rows'] if r['source_section']=='11.4'))"` | `5` |
| I5 | Nothing depends on an Enterprise-only mechanism | `python -c "import yaml;d=yaml.safe_load(open('access/plan-tier/plan-tier.yaml'));print(sum(1 for r in d['rows'] if r['enterprise_only'] and r['enterprise_mechanism_depended_on']))"` | `0` |
| I6 | Branch protection on private repositories is on the Team plan | `python -c "import yaml;d=yaml.safe_load(open('access/plan-tier/plan-tier.yaml'));print([r for r in d['rows'] if r['id']=='PT-01'][0]['plan_tier_fact'])"` | `available_on_the_team_plan` |
| I7 | Declaring a dependency on an Enterprise mechanism fails the checker (negative test) | see SELF-VERIFY | `1` |
| I8 | No path outside `access/` touched | `git diff --name-only origin/integration...HEAD \| grep -cv '^access/' \| tr -d ' '` | `0` |

### SELF-VERIFY

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
echo "I1 $(python access/tools/validate_access_config.py | tail -1)"
echo "I2 $(python access/tools/check_no_enterprise_dependency.py)"
echo "I3 $(python -c "import yaml;print(len(yaml.safe_load(open('access/plan-tier/plan-tier.yaml'))['rows']))")"
echo "I4 $(python -c "import yaml;d=yaml.safe_load(open('access/plan-tier/plan-tier.yaml'));print(sum(1 for r in d['rows'] if r['source_section']=='11.4'))")"
echo "I5 $(python -c "import yaml;d=yaml.safe_load(open('access/plan-tier/plan-tier.yaml'));print(sum(1 for r in d['rows'] if r['enterprise_only'] and r['enterprise_mechanism_depended_on']))")"
echo "I6 $(python -c "import yaml;d=yaml.safe_load(open('access/plan-tier/plan-tier.yaml'));print([r for r in d['rows'] if r['id']=='PT-01'][0]['plan_tier_fact'])")"
python - <<'PYEOF'
import yaml
d = yaml.safe_load(open("access/plan-tier/plan-tier.yaml", encoding="utf-8"))
for row in d["rows"]:
    if row["id"] == "PT-02":
        row["enterprise_mechanism_depended_on"] = True
open("access/testdata/arming/plan-tier-depends-on-enterprise.yaml", "w",
     encoding="utf-8").write(yaml.safe_dump(d, sort_keys=False))
PYEOF
ec=0; python access/tools/check_no_enterprise_dependency.py --config access/testdata/arming/plan-tier-depends-on-enterprise.yaml >/dev/null 2>&1 || ec=$?; echo "I7 $ec"
rm -f access/testdata/arming/plan-tier-depends-on-enterprise.yaml
echo "I8 $(git diff --name-only origin/integration...HEAD | grep -cv '^access/' | tr -d ' ')"
```

Expected output, exactly:

```
I1 ACCESS CONFIG VALIDATION PASSED (8 documents)
I2 PLAN-TIER: PASS (4 assertions)
I3 6
I4 5
I5 0
I6 available_on_the_team_plan
I7 1
I8 0
```

### STOP

Stop and file a blocker if any of the following is true.

- `I5` prints anything other than `0`. Something in `access/**` depends on a feature the estate does not have. Buying Enterprise is not the remedy available here: it is a recorded Founder budget decision (D73), not an implementer's choice, and it is a STOP.
- `I7` prints `0` — the checker does not detect a declared Enterprise dependency.
- A row is needed that is neither in §11.4 nor in §33.4. Every row cites its `source_section`; there is no third source.

```bash
set -euo pipefail
bash access/tools/blocker.sh L5-01-09 "an access/** declaration depends on an Enterprise-only feature" "<the failing criterion line>" "python access/tools/check_no_enterprise_dependency.py" "<its exact output>" "PLAN-TIER: PASS (4 assertions)" "<one sentence of fact>"
```

---

## L5-01-10 — D101 arming order and the arming-order gate

| Field | Value |
|---|---|
| Size | L |
| Depends on | L5-01-05, L5-01-06, L5-01-07 |
| Writes | `access/arming/arming-order.yaml`, `access/schemas/arming-order.schema.json`, `access/tools/check_arming_order.py`, `access/testdata/arming/write-after-arming.yaml` |
| Spec | D101; §98.2 Phase 1 ("Teams grant Write per the permission model — **within Week 1 and before branch protection is armed**"); §95.2; §95.4; §11.1; §11.3 |

> **Note (§4.9):** `access/branch-protection/branch-protection.yaml` is the **estate template for product repositories**. `control-plane`'s own configuration is `docs/build/rulesets/*.json` under L0. F-07 forbids any lane adding a required context. `digest-invariant-selftest` goes on `control-plane` only, at Phase 6.

This is the task the whole file exists to make mechanical. D101 in full: *"Week one arms gates in an order that can be satisfied. Branch protection requiring a Write-holding Code Owner approval was scheduled before any Team granted Write, and required status checks before any workflow emitted them. Teams are derived and granted first, from an interim assignment set that Phase 3 replaces, and the bootstrap arming pattern of §95.2 — configured but not yet binding, with the armed configuration recorded beside it — is reused rather than a second approach invented."*

The order is declared as nine numbered steps. The gate is five assertions over that declaration, and one of them is executed against a deliberately mis-ordered fixture, so the gate is proved to fire rather than assumed to.

**Commands**

```bash
set -e
cd "$(git rev-parse --show-toplevel)"
export CONTROL_PLANE_ROOT="$PWD"
git fetch origin
git checkout integration
git pull --ff-only origin integration
test -f access/model/teams.yaml || { echo "MISSING DEPENDENCY L5-01-05"; exit 1; }
test -f access/codeowners/generate_codeowners.py || { echo "MISSING DEPENDENCY L5-01-06"; exit 1; }
test -f access/branch-protection/branch-protection.yaml || { echo "MISSING DEPENDENCY L5-01-07"; exit 1; }
git checkout -b lane/5/p1-arming-order
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/arming/arming-order.yaml <<'YAMLEOF'
# access/arming/arming-order.yaml
# D101. The Week 1 arming order, declared so that it can be checked rather than
# remembered. Section 98.2: Teams grant Write "within Week 1 and before branch
# protection is armed". Section 95.4 names the failure if that order is inverted:
# a team that experiences its merges mysteriously breaking.
document: arming-order
spec_sections: ["98.2", "95.2", "95.4", "11.1", "11.3"]
decisions: ["D101"]

principle: >-
  Week one arms gates in an order that can be satisfied. Teams are derived and
  granted first, from an interim assignment set that Phase 3 replaces, and the
  bootstrap arming pattern of Section 95.2 - configured but not yet binding, with
  the armed configuration recorded beside it - is reused rather than a second
  approach invented (D101).

steps:
  - index: 1
    id: AO-01
    action: Apply the organisation baseline - single organisation, base permission Read, organisation-enforced 2FA
    declared_in: access/model/organisation.yaml
    requires: []
    grants_write: false
    arms_a_gate: false

  - index: 2
    id: AO-02
    action: Verify a second organisation Owner or an escrowed break-glass Owner credential with a named escrow custodian
    declared_in: access/model/owner-continuity.yaml
    requires: [AO-01]
    grants_write: false
    arms_a_gate: false
    note: >-
      The consolidation week is when total-loss exposure peaks (Section 98.2).

  - index: 3
    id: AO-03
    action: Create the Teams and grant Write, from the Phase 1 interim assignment set
    declared_in: access/model/teams.yaml
    requires: [AO-01]
    grants_write: true
    arms_a_gate: false

  - index: 4
    id: AO-04
    action: Generate CODEOWNERS for every repository, human identities only
    declared_in: access/codeowners/generate_codeowners.py
    requires: [AO-03]
    grants_write: false
    arms_a_gate: false
    note: >-
      Generated after the Teams exist, because the routing names Teams.

  - index: 5
    id: AO-05
    action: Apply branch protection in the unarmed profile
    declared_in: access/branch-protection/branch-protection.yaml
    requires: [AO-04]
    grants_write: false
    arms_a_gate: false
    note: >-
      Require-PR and direct-push blocking are on from this step. Required
      approving reviews is 0 (Section 95.2).

  - index: 6
    id: AO-06
    action: Apply the deployment branch and tag policy on every environment
    declared_in: access/environments/deployment-policies.yaml
    requires: [AO-05]
    grants_write: false
    arms_a_gate: false

  - index: 7
    id: AO-07
    action: Record a bootstrap exception for every gate current headcount cannot satisfy
    declared_in: not_an_access_artifact
    owned_by_lane: L0
    requires: [AO-05]
    grants_write: false
    arms_a_gate: false
    note: >-
      exceptions.yaml is not an access/** artifact. This lane records the
      dependency and routes it to L0; it configures nothing there.

  - index: 8
    id: AO-08
    action: Arm branch protection - 1 approving review, Code Owner review required, approval of the most recent reviewable push required
    declared_in: access/branch-protection/branch-protection.yaml
    requires: [AO-03, AO-04, AO-05, AO-07]
    grants_write: false
    arms_a_gate: true

  - index: 9
    id: AO-09
    action: Add each required status-check context, only once a workflow emits it
    declared_in: access/branch-protection/required-checks.md
    owned_by_lane: L2
    requires: [AO-08]
    grants_write: false
    arms_a_gate: true
    note: >-
      The list starts empty per repository. A required check no workflow emits
      blocks every pull request indefinitely (Section 98.2). The emitting
      workflows are L2's.

gate_assertions:
  - id: AOG-1
    statement: Every step that arms a gate requires, transitively, a step that grants Write.
  - id: AOG-2
    statement: Every step that grants Write has a strictly lower index than every step that arms a gate.
  - id: AOG-3
    statement: No step requires a step with a higher index.
  - id: AOG-4
    statement: Indexes run 1..N with no gap and no duplicate, and ids match their index.
  - id: AOG-5
    statement: The step arming the Code-Owner-and-approval gate requires the CODEOWNERS generation step.
YAMLEOF
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/schemas/arming-order.schema.json <<'JSONEOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  # NEEDS_URN (FD-050): replace with urn:multiproduct:schemas:<type>:<version>
  "$id": "https://control-plane.invalid/access/arming-order.schema.json",
  "x-target": "access/arming/arming-order.yaml",
  "title": "The D101 Week 1 arming order",
  "type": "object",
  "additionalProperties": false,
  "required": ["document", "spec_sections", "decisions", "principle", "steps",
               "gate_assertions"],
  "properties": {
    "document": {"const": "arming-order"},
    "spec_sections": {"type": "array", "items": {"type": "string"}, "minItems": 1},
    "decisions": {"type": "array", "minItems": 1, "items": {"const": "D101"}},
    "principle": {"type": "string"},
    "steps": {
      "type": "array",
      "minItems": 9,
      "maxItems": 9,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["index", "id", "action", "declared_in", "requires",
                     "grants_write", "arms_a_gate"],
        "properties": {
          "index": {"type": "integer", "minimum": 1, "maximum": 9},
          "id": {"type": "string", "pattern": "^AO-0[1-9]$"},
          "action": {"type": "string", "minLength": 1},
          "declared_in": {"type": "string", "minLength": 1},
          "owned_by_lane": {"enum": ["L0", "L1", "L2", "L3", "L4", "L5"]},
          "requires": {"type": "array", "items": {"type": "string", "pattern": "^AO-0[1-9]$"}},
          "grants_write": {"type": "boolean"},
          "arms_a_gate": {"type": "boolean"},
          "note": {"type": "string"}
        }
      }
    },
    "gate_assertions": {
      "type": "array",
      "minItems": 5,
      "maxItems": 5,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["id", "statement"],
        "properties": {
          "id": {"type": "string", "pattern": "^AOG-[1-5]$"},
          "statement": {"type": "string", "minLength": 1}
        }
      }
    }
  }
}
JSONEOF
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/tools/check_arming_order.py <<'PYEOF'
#!/usr/bin/env python
"""The D101 arming-order gate.

Refuses an arming order that cannot be satisfied. The failure it exists to
prevent is named in Section 98.2 and Section 95.4: arming a
Code-Owner-and-approval gate while no Team grants Write leaves nobody whose
approval counts, and the team experiences its merges mysteriously breaking.

Assertions:
  AOG-1  every step that arms a gate transitively requires a step that grants Write
  AOG-2  every Write-granting step has a strictly lower index than every arming step
  AOG-3  no step requires a step with a higher index
  AOG-4  indexes run 1..N with no gap or duplicate, and each id matches its index
  AOG-5  the arming step requires the CODEOWNERS generation step

Usage: check_arming_order.py [--config PATH]
Exit 0 on success, 1 on any failed assertion.
"""
import argparse
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DEFAULT = os.path.join(ROOT, "access", "arming", "arming-order.yaml")
CODEOWNERS_STEP_MARKER = "generate_codeowners.py"


def transitive_requires(steps_by_id, start_id, seen=None):
    if seen is None:
        seen = set()
    for required in steps_by_id.get(start_id, {}).get("requires", []):
        if required in seen:
            continue
        seen.add(required)
        transitive_requires(steps_by_id, required, seen)
    return seen


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=DEFAULT)
    args = parser.parse_args()

    with open(args.config, "r", encoding="utf-8") as handle:
        doc = yaml.safe_load(handle)

    steps = doc.get("steps", [])
    by_id = dict((step["id"], step) for step in steps)
    arming = [step for step in steps if step.get("arms_a_gate")]
    granting = [step for step in steps if step.get("grants_write")]

    aog1 = bool(arming) and bool(granting)
    for step in arming:
        reached = transitive_requires(by_id, step["id"])
        if not any(by_id.get(ident, {}).get("grants_write") for ident in reached):
            aog1 = False

    aog2 = bool(arming) and bool(granting)
    for grant in granting:
        for arm in arming:
            if not grant["index"] < arm["index"]:
                aog2 = False

    aog3 = True
    for step in steps:
        for required in step.get("requires", []):
            if required not in by_id or by_id[required]["index"] >= step["index"]:
                aog3 = False

    indexes = sorted(step["index"] for step in steps)
    aog4 = indexes == list(range(1, len(steps) + 1))
    for step in steps:
        if step["id"] != "AO-%02d" % step["index"]:
            aog4 = False

    codeowners_ids = [step["id"] for step in steps
                      if CODEOWNERS_STEP_MARKER in str(step.get("declared_in", ""))]
    aog5 = bool(codeowners_ids) and bool(arming)
    for step in arming:
        reached = transitive_requires(by_id, step["id"])
        if not any(ident in reached for ident in codeowners_ids):
            aog5 = False

    assertions = [
        ("AOG-1", "every arming step transitively requires a Write-granting step", aog1),
        ("AOG-2", "every Write-granting step precedes every arming step", aog2),
        ("AOG-3", "no step requires a step with a higher index", aog3),
        ("AOG-4", "indexes run 1..N with no gap or duplicate and ids match", aog4),
        ("AOG-5", "the arming step requires CODEOWNERS generation", aog5),
    ]

    failed = 0
    for ident, statement, ok in assertions:
        if not ok:
            print("FAIL %s: %s" % (ident, statement))
            failed += 1
    if failed:
        print("ARMING-ORDER: FAIL (%d of %d assertions)" % (failed, len(assertions)))
        return 1
    print("ARMING-ORDER: PASS (%d assertions)" % len(assertions))
    return 0


if __name__ == "__main__":
    sys.exit(main())
PYEOF
chmod +x access/tools/check_arming_order.py
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
python - <<'PYEOF'
"""Build the deliberately mis-ordered fixture: Write granted AFTER arming.

This is the exact order D101 was written to forbid. The gate must reject it.
"""
import yaml

doc = yaml.safe_load(open("access/arming/arming-order.yaml", encoding="utf-8"))
steps = dict((s["id"], s) for s in doc["steps"])
steps["AO-03"]["index"] = 9
steps["AO-03"]["requires"] = ["AO-08"]
steps["AO-04"]["requires"] = ["AO-01"]
steps["AO-08"]["requires"] = ["AO-04", "AO-05", "AO-07"]
steps["AO-09"]["index"] = 3
steps["AO-09"]["requires"] = ["AO-01"]
doc["steps"] = sorted(steps.values(), key=lambda s: s["index"])
open("access/testdata/arming/write-after-arming.yaml", "w", encoding="utf-8").write(
    "# FIXTURE. The arming order D101 forbids: Write granted after the gate is\n"
    "# armed. access/tools/check_arming_order.py must reject this document.\n"
    "# Never applied to a real organisation.\n"
    + yaml.safe_dump(doc, sort_keys=False))
PYEOF
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
python access/tools/validate_access_config.py
python access/tools/check_arming_order.py
python access/tools/check_arming_order.py --config access/testdata/arming/write-after-arming.yaml || echo "fixture rejected as required"
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
git add access
git commit -m "$(printf 'L5-01-10: D101 arming order and the arming-order gate\n\nLane: L5\n')"
git push -u origin lane/5/p1-arming-order
```

### Acceptance criteria

| # | Criterion | Proving command | Expected output |
|---|---|---|---|
| J1 | All nine documents validate | `python access/tools/validate_access_config.py \| tail -1` | `ACCESS CONFIG VALIDATION PASSED (9 documents)` |
| J2 | All five gate assertions hold on the real order | `python access/tools/check_arming_order.py` | `ARMING-ORDER: PASS (5 assertions)` |
| J3 | Nine steps are declared | `python -c "import yaml;print(len(yaml.safe_load(open('access/arming/arming-order.yaml'))['steps']))"` | `9` |
| J4 | Exactly one step grants Write, and it is step 3 | `python -c "import yaml;d=yaml.safe_load(open('access/arming/arming-order.yaml'));print([s['index'] for s in d['steps'] if s['grants_write']])"` | `[3]` |
| J5 | The arming steps come after it | `python -c "import yaml;d=yaml.safe_load(open('access/arming/arming-order.yaml'));print([s['index'] for s in d['steps'] if s['arms_a_gate']])"` | `[8, 9]` |
| J6 | The mis-ordered fixture is rejected (executed negative test) | `python access/tools/check_arming_order.py --config access/testdata/arming/write-after-arming.yaml >/dev/null 2>&1; echo $?` | `1` |
| J7 | And it is rejected for the right reason | `python access/tools/check_arming_order.py --config access/testdata/arming/write-after-arming.yaml \| grep -c '^FAIL AOG-2'` | `1` |
| J8 | The fixture is fixture-only and never applied | `grep -c 'Never applied to a real organisation' access/testdata/arming/write-after-arming.yaml` | `1` |
| J9 | No path outside `access/` touched | `git diff --name-only origin/integration...HEAD \| grep -cv '^access/' \| tr -d ' '` | `0` |

### SELF-VERIFY

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
echo "J1 $(python access/tools/validate_access_config.py | tail -1)"
echo "J2 $(python access/tools/check_arming_order.py)"
echo "J3 $(python -c "import yaml;print(len(yaml.safe_load(open('access/arming/arming-order.yaml'))['steps']))")"
echo "J4 $(python -c "import yaml;d=yaml.safe_load(open('access/arming/arming-order.yaml'));print([s['index'] for s in d['steps'] if s['grants_write']])")"
echo "J5 $(python -c "import yaml;d=yaml.safe_load(open('access/arming/arming-order.yaml'));print([s['index'] for s in d['steps'] if s['arms_a_gate']])")"
ec=0; python access/tools/check_arming_order.py --config access/testdata/arming/write-after-arming.yaml >/dev/null 2>&1 || ec=$?; echo "J6 $ec"
echo "J7 $(python access/tools/check_arming_order.py --config access/testdata/arming/write-after-arming.yaml | grep -c '^FAIL AOG-2')"
echo "J8 $(grep -c 'Never applied to a real organisation' access/testdata/arming/write-after-arming.yaml)"
echo "J9 $(git diff --name-only origin/integration...HEAD | grep -cv '^access/' | tr -d ' ')"
```

Expected output, exactly:

```
J1 ACCESS CONFIG VALIDATION PASSED (9 documents)
J2 ARMING-ORDER: PASS (5 assertions)
J3 9
J4 [3]
J5 [8, 9]
J6 1
J7 1
J8 1
J9 0
```

### STOP

Stop and file a blocker if any of the following is true.

- `J6` prints `0`. The gate accepts the exact order D101 forbids. It is decoration, and the arming week has no mechanical protection.
- `J4` prints anything other than `[3]`, or `J5` prints an index lower than any index in `J4`. Do not reorder the steps to make the checker pass; the order is the deliverable.
- Step `AO-09` looks like it belongs earlier so that required status checks are set at arming time. §98.2 forbids it: a required check no workflow emits blocks every pull request indefinitely.
- Step `AO-07` looks like something this lane should build. It is not. `exceptions.yaml` is not an `access/**` artifact; the dependency is declared and routed to L0 (§0.2).

```bash
set -euo pipefail
bash access/tools/blocker.sh L5-01-10 "the arming-order gate does not reject an unsatisfiable order" "<the failing criterion line>" "python access/tools/check_arming_order.py --config access/testdata/arming/write-after-arming.yaml" "<its exact output>" "<the expected line from the SELF-VERIFY block>" "<one sentence of fact>"
```

---

## L5-01-11 — Owner continuity and break-glass escrow declaration

| Field | Value |
|---|---|
| Size | S |
| Depends on | L5-01-03 |
| Writes | `access/model/owner-continuity.yaml`, `access/schemas/owner-continuity.schema.json` |
| Spec | §11.2 ("A second organisation Owner — or an escrowed break-glass owner credential — exists as part of founder continuity"); §14.4 escrow mechanics; §98.2 Phase 1 completion check; §45.3; D21; invariant 39; AT-022 |

§98.2 requires, as a Phase 1 completion condition, that *"a second organisation Owner or an escrowed break-glass Owner credential exists with a named escrow custodian — the consolidation week is when total-loss exposure peaks."*

This document declares the requirement, the escrow mechanics that make it real, and the two alerting rules. It **names no person**. A custodian is a person; person identities are registry data owned by L1, and a name copied here would be a second source of truth. The document records that the custodian is named in the operational asset inventory (§49) and that `custodian_named_here` is `false`, so a later reader cannot mistake the absence for an omission.

**Commands**

```bash
set -e
cd "$(git rev-parse --show-toplevel)"
export CONTROL_PLANE_ROOT="$PWD"
git fetch origin
git checkout integration
git pull --ff-only origin integration
test -f access/model/organisation.yaml || { echo "MISSING DEPENDENCY L5-01-03"; exit 1; }
git checkout -b lane/5/p1-owner-continuity
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/model/owner-continuity.yaml <<'YAMLEOF'
# access/model/owner-continuity.yaml
# Spec Section 11.2, Section 14.4, Section 98.2. D21, invariant 39, AT-022.
# Organisation ownership is never a population of one with no recovery path.
# NO PERSON IS NAMED HERE. The escrow custodian is named in the operational
# asset inventory (Section 49); a copy here would be a second source of truth.
document: owner-continuity
spec_sections: ["11.2", "14.4", "45.3", "49", "98.2"]
decisions: ["D21"]
invariants: [39]
acceptance_tests: ["AT-022"]

requirement:
  satisfied_by_either:
    - a second organisation Owner exists
    - an escrowed break-glass Owner credential is held under sealed, audited escrow
  never: organisation_ownership_recoverable_only_through_one_persons_login
  phase_1_reason: >-
    The consolidation week is when total-loss exposure peaks (Section 98.2).

escrow:
  custodian_named_here: false
  custodian_recorded_in: the operational asset inventory (Section 49)
  custodian_named_here_reason: >-
    A custodian is a person. Person identities are registry data; this document
    declares the requirement and its checks, never a person's name.
  seal_audit_cadence: quarterly
  seal_audit_month_of_quarter: 2
  seal_audit_confirms:
    - the escrow is intact
    - its contents match the declared inventory of escrowed credentials
    - no access has occurred outside a recorded break-glass event
    - each escrowed item still works
  functional_verification:
    statement: >-
      An inventory match is not a functional test. The escrowed Owner credential
      must authenticate; the dormant-account authentication alert logs exactly
      that (Section 14.4).
    recorded_as: a drill record, distinct from a break-glass record
  re_escrow_on_rotation:
    blocking: true
    rule: >-
      Any credential rotation on the covered account triggers mandatory
      re-escrow of the replacement before the rotation is considered complete. A
      rotation is not recordable as done until the replacement is escrowed
      (Section 14.4, Section 40.1).

alerting:
  on_authentication_of_the_dormant_owner_account: true
  on_any_use_of_an_escrowed_credential: true
  routes_to: [founder]
  routes_to_under_incapacity_trigger: [successor_arrangement]
  dispatch_owned_by: "L5 notify/** - a different L5 phase file, out of scope here"

break_glass:
  use_is: a_break_glass_event
  registered_in: the exception registry (Section 54)
  appears_in: the disaster-recovery failure-scenario table (Section 45)
  owned_by_lane: L0
  owned_by_lane_reason: >-
    exceptions.yaml is not an access/** artifact. This document cites the
    requirement and configures nothing there.

phase_1_check:
  statement: >-
    A second organisation Owner or an escrowed break-glass Owner credential
    exists with a named escrow custodian.
  spec_section: "98.2"
  verified_at: apply_time
  verified_by: access/runbooks/apply-organisation.sh
YAMLEOF
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/schemas/owner-continuity.schema.json <<'JSONEOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  # NEEDS_URN (FD-050): replace with urn:multiproduct:schemas:<type>:<version>
  "$id": "https://control-plane.invalid/access/owner-continuity.schema.json",
  "x-target": "access/model/owner-continuity.yaml",
  "title": "Organisation Owner continuity and break-glass escrow (spec Section 11.2, Section 14.4)",
  "type": "object",
  "additionalProperties": false,
  "required": ["document", "spec_sections", "decisions", "invariants", "acceptance_tests",
               "requirement", "escrow", "alerting", "break_glass", "phase_1_check"],
  "properties": {
    "document": {"const": "owner-continuity"},
    "spec_sections": {"type": "array", "items": {"type": "string"}, "minItems": 1},
    "decisions": {"type": "array", "items": {"type": "string"}, "minItems": 1},
    "invariants": {"type": "array", "items": {"type": "integer"}, "minItems": 1},
    "acceptance_tests": {"type": "array", "items": {"type": "string"}, "minItems": 1},
    "requirement": {
      "type": "object",
      "additionalProperties": false,
      "required": ["satisfied_by_either", "never", "phase_1_reason"],
      "properties": {
        "satisfied_by_either": {"type": "array", "minItems": 2, "maxItems": 2,
                                "items": {"type": "string"}},
        "never": {"const": "organisation_ownership_recoverable_only_through_one_persons_login"},
        "phase_1_reason": {"type": "string"}
      }
    },
    "escrow": {
      "type": "object",
      "additionalProperties": false,
      "required": ["custodian_named_here", "custodian_recorded_in",
                   "custodian_named_here_reason", "seal_audit_cadence",
                   "seal_audit_month_of_quarter", "seal_audit_confirms",
                   "functional_verification", "re_escrow_on_rotation"],
      "properties": {
        "custodian_named_here": {"const": false},
        "custodian_recorded_in": {"type": "string"},
        "custodian_named_here_reason": {"type": "string"},
        "seal_audit_cadence": {"const": "quarterly"},
        "seal_audit_month_of_quarter": {"const": 2},
        "seal_audit_confirms": {"type": "array", "minItems": 4, "items": {"type": "string"}},
        "functional_verification": {
          "type": "object",
          "additionalProperties": false,
          "required": ["statement", "recorded_as"],
          "properties": {"statement": {"type": "string"}, "recorded_as": {"type": "string"}}
        },
        "re_escrow_on_rotation": {
          "type": "object",
          "additionalProperties": false,
          "required": ["blocking", "rule"],
          "properties": {"blocking": {"const": true}, "rule": {"type": "string"}}
        }
      }
    },
    "alerting": {
      "type": "object",
      "additionalProperties": false,
      "required": ["on_authentication_of_the_dormant_owner_account",
                   "on_any_use_of_an_escrowed_credential", "routes_to",
                   "routes_to_under_incapacity_trigger", "dispatch_owned_by"],
      "properties": {
        "on_authentication_of_the_dormant_owner_account": {"const": true},
        "on_any_use_of_an_escrowed_credential": {"const": true},
        "routes_to": {"type": "array", "minItems": 1, "items": {"type": "string"}},
        "routes_to_under_incapacity_trigger": {"type": "array", "minItems": 1,
                                               "items": {"type": "string"}},
        "dispatch_owned_by": {"type": "string"}
      }
    },
    "break_glass": {
      "type": "object",
      "additionalProperties": false,
      "required": ["use_is", "registered_in", "appears_in", "owned_by_lane",
                   "owned_by_lane_reason"],
      "properties": {
        "use_is": {"const": "a_break_glass_event"},
        "registered_in": {"type": "string"},
        "appears_in": {"type": "string"},
        "owned_by_lane": {"const": "L0"},
        "owned_by_lane_reason": {"type": "string"}
      }
    },
    "phase_1_check": {
      "type": "object",
      "additionalProperties": false,
      "required": ["statement", "spec_section", "verified_at", "verified_by"],
      "properties": {
        "statement": {"type": "string"},
        "spec_section": {"const": "98.2"},
        "verified_at": {"const": "apply_time"},
        "verified_by": {"const": "access/runbooks/apply-organisation.sh"}
      }
    }
  }
}
JSONEOF
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
python access/tools/validate_access_config.py
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
git add access
git commit -m "$(printf 'L5-01-11: owner continuity and break-glass escrow declaration\n\nLane: L5\n')"
git push -u origin lane/5/p1-owner-continuity
```

### Acceptance criteria

| # | Criterion | Proving command | Expected output |
|---|---|---|---|
| K1 | All ten documents validate | `python access/tools/validate_access_config.py \| tail -1` | `ACCESS CONFIG VALIDATION PASSED (10 documents)` |
| K2 | Ownership is never a population of one | `python -c "import yaml;print(yaml.safe_load(open('access/model/owner-continuity.yaml'))['requirement']['never'])"` | `organisation_ownership_recoverable_only_through_one_persons_login` |
| K3 | Two ways to satisfy it, and only two | `python -c "import yaml;print(len(yaml.safe_load(open('access/model/owner-continuity.yaml'))['requirement']['satisfied_by_either']))"` | `2` |
| K4 | No person is named | `python -c "import yaml;print(yaml.safe_load(open('access/model/owner-continuity.yaml'))['escrow']['custodian_named_here'])"` | `False` |
| K5 | Re-escrow blocks rotation completion | `python -c "import yaml;print(yaml.safe_load(open('access/model/owner-continuity.yaml'))['escrow']['re_escrow_on_rotation']['blocking'])"` | `True` |
| K6 | Both alerting rules are on | `python -c "import yaml;a=yaml.safe_load(open('access/model/owner-continuity.yaml'))['alerting'];print(a['on_authentication_of_the_dormant_owner_account'],a['on_any_use_of_an_escrowed_credential'])"` | `True True` |
| K7 | `organisation.yaml` points here and nowhere else | `python -c "import yaml;print(yaml.safe_load(open('access/model/organisation.yaml'))['owner_continuity']['declared_in'])"` | `access/model/owner-continuity.yaml` |
| K8 | No path outside `access/` touched | `git diff --name-only origin/integration...HEAD \| grep -cv '^access/' \| tr -d ' '` | `0` |

### SELF-VERIFY

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
echo "K1 $(python access/tools/validate_access_config.py | tail -1)"
echo "K2 $(python -c "import yaml;print(yaml.safe_load(open('access/model/owner-continuity.yaml'))['requirement']['never'])")"
echo "K3 $(python -c "import yaml;print(len(yaml.safe_load(open('access/model/owner-continuity.yaml'))['requirement']['satisfied_by_either']))")"
echo "K4 $(python -c "import yaml;print(yaml.safe_load(open('access/model/owner-continuity.yaml'))['escrow']['custodian_named_here'])")"
echo "K5 $(python -c "import yaml;print(yaml.safe_load(open('access/model/owner-continuity.yaml'))['escrow']['re_escrow_on_rotation']['blocking'])")"
echo "K6 $(python -c "import yaml;a=yaml.safe_load(open('access/model/owner-continuity.yaml'))['alerting'];print(a['on_authentication_of_the_dormant_owner_account'],a['on_any_use_of_an_escrowed_credential'])")"
echo "K7 $(python -c "import yaml;print(yaml.safe_load(open('access/model/organisation.yaml'))['owner_continuity']['declared_in'])")"
echo "K8 $(git diff --name-only origin/integration...HEAD | grep -cv '^access/' | tr -d ' ')"
```

Expected output, exactly:

```
K1 ACCESS CONFIG VALIDATION PASSED (10 documents)
K2 organisation_ownership_recoverable_only_through_one_persons_login
K3 2
K4 False
K5 True
K6 True True
K7 access/model/owner-continuity.yaml
K8 0
```

### STOP

Stop and file a blocker if any of the following is true.

- A person's name, login, or email would have to be written into this document. That is a STOP. The custodian is named in the operational asset inventory (§49), which is not an `access/**` artifact in this file's scope.
- An escrowed credential, a recovery code, or a key would have to be written into this or any other file. §101 invariant 84 and §0.6 both forbid it; there is no version of this task that stores a secret.
- `K4` prints `True`.
- The organisation has exactly one Owner and no escrow. The requirement is then not satisfied, and §98.2 makes it a Phase 1 completion condition. Record nothing; file the blocker.

```bash
set -euo pipefail
bash access/tools/blocker.sh L5-01-11 "owner continuity is not declared correctly" "<the failing criterion line>" "python access/tools/validate_access_config.py" "<its exact output>" "ACCESS CONFIG VALIDATION PASSED (10 documents)" "<one sentence of fact>"
```

---

## L5-01-12 — Apply runbooks — dry-run by default, `gh` commands in arming order

| Field | Value |
|---|---|
| Size | L |
| Depends on | L5-01-03, L5-01-05, L5-01-07, L5-01-08, L5-01-10 |
| Writes | `access/runbooks/README.md`, `access/runbooks/apply-organisation.sh`, `access/runbooks/apply-teams.sh`, `access/runbooks/apply-branch-protection.sh`, `access/runbooks/apply-environments.sh`, `access/testdata/teams/interim-teams.json` |
| Spec | §98.2 Phase 1; §11 (dynamic enumeration); §95.2; D101 |

Four scripts, run in the order `arming-order.yaml` declares. Every one of them is **dry-run by default**: `--apply` is an explicit flag, and in apply mode each requires `$ORG_LOGIN` and a `gh auth status` that succeeds. A build agent holds neither, which is the point — these runbooks are executed by a human with organisation-admin credentials, and every acceptance criterion below is satisfied in dry-run mode with no credentials at all.

Two properties are enforced in code rather than in prose:

1. **No repository name is ever written down.** `apply-branch-protection.sh` and `apply-environments.sh` enumerate with `gh api --paginate /orgs/$ORG_LOGIN/repos` (§11).
2. **D101 is enforced at the moment of arming.** `apply-branch-protection.sh --profile armed` runs `check_arming_order.py` first and refuses on failure, and then, per repository, refuses to arm any repository on which no Team holds Write. That is the mechanical form of §98.2's *"Teams granting Write exist before branch protection is armed, so that no window opens in which no approval can satisfy the gate."*

**Commands**

```bash
set -e
cd "$(git rev-parse --show-toplevel)"
export CONTROL_PLANE_ROOT="$PWD"
git fetch origin
git checkout integration
git pull --ff-only origin integration
test -f access/arming/arming-order.yaml || { echo "MISSING DEPENDENCY L5-01-10"; exit 1; }
test -f access/environments/deployment-policies.yaml || { echo "MISSING DEPENDENCY L5-01-08"; exit 1; }
git checkout -b lane/5/p1-apply-runbooks
mkdir -p access/testdata/teams
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/testdata/teams/interim-teams.json <<'JSONEOF'
{
  "assignment_set": "interim",
  "teams": [
    {"slug": "role-team-lead", "permission": "push", "repositories": ["example-product"]},
    {"slug": "role-qa", "permission": "push", "repositories": ["example-product"]},
    {"slug": "product-example-product", "permission": "push", "repositories": ["example-product"]}
  ]
}
JSONEOF
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/runbooks/apply-organisation.sh <<'SHEOF'
#!/usr/bin/env bash
# Arming steps AO-01 and AO-02. Spec Section 11, Section 11.2, Section 98.2.
# Dry-run by default. --apply requires $ORG_LOGIN and an authenticated gh.
#
# Usage: apply-organisation.sh [--apply]
# Exit codes: 0 ok | 2 missing credentials in apply mode | 5 owner continuity unsatisfied
set -u
cd "$(git rev-parse --show-toplevel)"
APPLY=0
[ "${1:-}" = "--apply" ] && APPLY=1
ORG="${ORG_LOGIN:-ORG-LOGIN-NOT-SET}"

if [ "$APPLY" -eq 1 ]; then
  if [ "$ORG" = "ORG-LOGIN-NOT-SET" ]; then
    echo "APPLY-ORGANISATION: REFUSED - ORG_LOGIN is not set" >&2; exit 2
  fi
  gh auth status >/dev/null 2>&1 || {
    echo "APPLY-ORGANISATION: REFUSED - gh is not authenticated" >&2; exit 2; }
fi

CALLS=0
run () {  # run <gh args...>
  CALLS=$((CALLS + 1))
  if [ "$APPLY" -eq 1 ]; then
    echo "APPLY $*"
    "$@"
  else
    echo "DRY-RUN $*"
  fi
}

# Base permission Read (Section 11.2).
run gh api -X PATCH "/orgs/${ORG}" -f default_repository_permission=read
# Organisation-enforced two-factor authentication (Section 11.2, D53).
run gh api -X PATCH "/orgs/${ORG}" -F two_factor_requirement_enabled=true
# No machine approval satisfies a gate (D53): Actions may not approve pull requests.
run gh api -X PUT "/orgs/${ORG}/actions/permissions/workflow" -F can_approve_pull_request_reviews=false

# AO-02 - owner continuity. Section 98.2 makes this a Phase 1 completion condition.
CALLS=$((CALLS + 1))
if [ "$APPLY" -eq 1 ]; then
  OWNERS=$(gh api --paginate "/orgs/${ORG}/members?role=admin" --jq 'length' | awk '{s+=$1} END {print s+0}')
  echo "APPLY owner count = ${OWNERS}"
  if [ "${OWNERS}" -lt 2 ] && [ "${ESCROW_ATTESTED:-no}" != "yes" ]; then
    echo "APPLY-ORGANISATION: REFUSED - one organisation Owner and no attested" >&2
    echo "  escrowed break-glass Owner credential. Section 98.2 makes a second" >&2
    echo "  Owner or an escrowed credential with a named escrow custodian a" >&2
    echo "  Phase 1 completion condition; the consolidation week is when" >&2
    echo "  total-loss exposure peaks." >&2
    exit 5
  fi
else
  echo "DRY-RUN gh api --paginate /orgs/${ORG}/members?role=admin  # owner continuity, AO-02"
fi

if [ "$APPLY" -eq 1 ]; then
  echo "APPLY-ORGANISATION: APPLIED (${CALLS} calls)"
else
  echo "APPLY-ORGANISATION: DRY-RUN COMPLETE (${CALLS} calls)"
fi
SHEOF
chmod +x access/runbooks/apply-organisation.sh
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/runbooks/apply-teams.sh <<'SHEOF'
#!/usr/bin/env bash
# Arming step AO-03. Spec Section 11.2, D101.
# Teams grant Write BEFORE branch protection is armed, from the Phase 1 interim
# assignment set. Membership is derived from the registries and arrives as a
# JSON input document; this script reads no registry (PARTITION rule 4).
#
# Usage: apply-teams.sh --input INPUT.json [--apply]
# Exit codes: 0 ok | 2 missing credentials in apply mode | 3 bad input
set -u
cd "$(git rev-parse --show-toplevel)"
APPLY=0
INPUT=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --apply) APPLY=1 ;;
    --input) shift; INPUT="${1:-}" ;;
    *) echo "usage: apply-teams.sh --input INPUT.json [--apply]" >&2; exit 3 ;;
  esac
  shift
done
[ -n "$INPUT" ] || { echo "APPLY-TEAMS: REFUSED - --input is required" >&2; exit 3; }
[ -f "$INPUT" ] || { echo "APPLY-TEAMS: REFUSED - input not found: $INPUT" >&2; exit 3; }
ORG="${ORG_LOGIN:-ORG-LOGIN-NOT-SET}"

if [ "$APPLY" -eq 1 ]; then
  [ "$ORG" != "ORG-LOGIN-NOT-SET" ] || {
    echo "APPLY-TEAMS: REFUSED - ORG_LOGIN is not set" >&2; exit 2; }
  gh auth status >/dev/null 2>&1 || {
    echo "APPLY-TEAMS: REFUSED - gh is not authenticated" >&2; exit 2; }
fi

SET=$(python -c "import json,sys;print(json.load(open(sys.argv[1]))['assignment_set'])" "$INPUT")
echo "assignment_set = ${SET}  (Phase 3 replaces the interim set - D101)"

GRANTS=$(python -c "
import json, sys
doc = json.load(open(sys.argv[1]))
for team in doc['teams']:
    for repo in team['repositories']:
        print('%s|%s|%s' % (team['slug'], team['permission'], repo))
" "$INPUT")

COUNT=0
while IFS='|' read -r SLUG PERM REPO; do
  [ -n "$SLUG" ] || continue
  COUNT=$((COUNT + 1))
  if [ "$APPLY" -eq 1 ]; then
    gh api -X PUT "/orgs/${ORG}/teams/${SLUG}/repos/${ORG}/${REPO}" -f permission="${PERM}"
    echo "APPLY team ${SLUG} -> ${REPO} (${PERM})"
  else
    echo "DRY-RUN gh api -X PUT /orgs/${ORG}/teams/${SLUG}/repos/${ORG}/${REPO} -f permission=${PERM}"
  fi
done <<EOT
${GRANTS}
EOT

if [ "$APPLY" -eq 1 ]; then
  echo "APPLY-TEAMS: APPLIED (${COUNT} grants)"
else
  echo "APPLY-TEAMS: DRY-RUN COMPLETE (${COUNT} grants)"
fi
SHEOF
chmod +x access/runbooks/apply-teams.sh
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/runbooks/apply-branch-protection.sh <<'SHEOF'
#!/usr/bin/env bash
# Arming steps AO-05 (unarmed) and AO-08 (armed). Spec Section 11.3,
# Section 95.2, Section 98.2, D101.
#
# The D101 gate is enforced here, twice:
#   1. check_arming_order.py must pass before anything is applied.
#   2. In apply mode with --profile armed, every repository must already have at
#      least one Team holding push, maintain or admin. Arming a
#      Code-Owner-and-approval gate on a repository where no Team holds Write
#      leaves nobody whose approval counts.
#
# Usage: apply-branch-protection.sh --profile {unarmed,armed}
#          [--contexts a,b] [--arming-config PATH] [--apply]
# Exit codes: 0 ok | 2 missing credentials | 3 no Team grants Write | 4 arming order rejected
set -u
cd "$(git rev-parse --show-toplevel)"
APPLY=0
PROFILE=""
CONTEXTS=""
ARMING_CONFIG="access/arming/arming-order.yaml"
while [ "$#" -gt 0 ]; do
  case "$1" in
    --apply) APPLY=1 ;;
    --profile) shift; PROFILE="${1:-}" ;;
    --contexts) shift; CONTEXTS="${1:-}" ;;
    --arming-config) shift; ARMING_CONFIG="${1:-}" ;;
    *) echo "usage: apply-branch-protection.sh --profile {unarmed,armed} [--contexts a,b] [--arming-config PATH] [--apply]" >&2; exit 4 ;;
  esac
  shift
done
case "$PROFILE" in
  unarmed|armed) : ;;
  *) echo "APPLY-BRANCH-PROTECTION: REFUSED - --profile must be unarmed or armed" >&2; exit 4 ;;
esac

if ! python access/tools/check_arming_order.py --config "$ARMING_CONFIG" >/dev/null 2>&1; then
  echo "APPLY-BRANCH-PROTECTION: REFUSED - the declared arming order is unsatisfiable" >&2
  python access/tools/check_arming_order.py --config "$ARMING_CONFIG" >&2 || true
  exit 4
fi

PAYLOAD=$(python access/tools/render_protection_payload.py --profile "$PROFILE" --contexts "$CONTEXTS")
ORG="${ORG_LOGIN:-ORG-LOGIN-NOT-SET}"

if [ "$APPLY" -eq 0 ]; then
  echo "$PAYLOAD"
  echo "DRY-RUN gh api --paginate /orgs/${ORG}/repos --jq .[].name   # Section 11: never a hard-coded list"
  echo "DRY-RUN gh api -X PUT /repos/${ORG}/REPO/branches/DEFAULT/protection --input -"
  echo "APPLY-BRANCH-PROTECTION: DRY-RUN COMPLETE (profile=${PROFILE})"
  exit 0
fi

[ "$ORG" != "ORG-LOGIN-NOT-SET" ] || {
  echo "APPLY-BRANCH-PROTECTION: REFUSED - ORG_LOGIN is not set" >&2; exit 2; }
gh auth status >/dev/null 2>&1 || {
  echo "APPLY-BRANCH-PROTECTION: REFUSED - gh is not authenticated" >&2; exit 2; }

COUNT=0
for REPO in $(gh api --paginate "/orgs/${ORG}/repos" --jq '.[].name'); do
  if [ "$PROFILE" = "armed" ]; then
    WRITERS=$(gh api "/repos/${ORG}/${REPO}/teams" \
      --jq '[.[] | select(.permission=="push" or .permission=="maintain" or .permission=="admin")] | length')
    if [ "${WRITERS}" -eq 0 ]; then
      echo "APPLY-BRANCH-PROTECTION: REFUSED on ${REPO} - no Team holds Write." >&2
      echo "  Arming a Code-Owner-and-approval gate here leaves nobody whose" >&2
      echo "  approval counts (D101, Section 98.2). Run apply-teams.sh first." >&2
      exit 3
    fi
  fi
  BRANCH=$(gh api "/repos/${ORG}/${REPO}" --jq '.default_branch')
  printf '%s' "$PAYLOAD" | gh api -X PUT "/repos/${ORG}/${REPO}/branches/${BRANCH}/protection" --input -
  COUNT=$((COUNT + 1))
  echo "APPLY ${REPO}:${BRANCH} profile=${PROFILE}"
done
echo "APPLY-BRANCH-PROTECTION: APPLIED (${COUNT} repositories, profile=${PROFILE})"
SHEOF
chmod +x access/runbooks/apply-branch-protection.sh
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/runbooks/apply-environments.sh <<'SHEOF'
#!/usr/bin/env bash
# Arming step AO-06. Spec Section 33.4, Section 11.3 bullet BP-10.
# Every environment carries a deployment branch and tag policy. A repository
# with branch protection and no deployment branch policy holds production
# credentials behind nothing.
#
# Usage: apply-environments.sh [--release-tag-pattern PATTERN] [--apply]
# Exit codes: 0 ok | 2 missing credentials in apply mode
set -u
cd "$(git rev-parse --show-toplevel)"
APPLY=0
TAGS="v*"
while [ "$#" -gt 0 ]; do
  case "$1" in
    --apply) APPLY=1 ;;
    --release-tag-pattern) shift; TAGS="${1:-v*}" ;;
    *) echo "usage: apply-environments.sh [--release-tag-pattern PATTERN] [--apply]" >&2; exit 2 ;;
  esac
  shift
done
ORG="${ORG_LOGIN:-ORG-LOGIN-NOT-SET}"
ENVIRONMENTS="development staging production"

if [ "$APPLY" -eq 0 ]; then
  for ENV in $ENVIRONMENTS; do
    python access/tools/render_environment_payload.py --environment "$ENV" \
      --default-branch DEFAULT --release-tag-pattern "$TAGS"
  done
  echo "DRY-RUN gh api --paginate /orgs/${ORG}/repos --jq .[].name   # Section 11"
  echo "APPLY-ENVIRONMENTS: DRY-RUN COMPLETE (3 environments)"
  exit 0
fi

[ "$ORG" != "ORG-LOGIN-NOT-SET" ] || {
  echo "APPLY-ENVIRONMENTS: REFUSED - ORG_LOGIN is not set" >&2; exit 2; }
gh auth status >/dev/null 2>&1 || {
  echo "APPLY-ENVIRONMENTS: REFUSED - gh is not authenticated" >&2; exit 2; }

COUNT=0
for REPO in $(gh api --paginate "/orgs/${ORG}/repos" --jq '.[].name'); do
  BRANCH=$(gh api "/repos/${ORG}/${REPO}" --jq '.default_branch')
  for ENV in $ENVIRONMENTS; do
    RENDERED=$(python access/tools/render_environment_payload.py --environment "$ENV" \
      --default-branch "$BRANCH" --release-tag-pattern "$TAGS")
    printf '%s' "$RENDERED" \
      | python -c "import json,sys;print(json.dumps(json.load(sys.stdin)['environment_payload']))" \
      | gh api -X PUT "/repos/${ORG}/${REPO}/environments/${ENV}" --input -
    printf '%s' "$RENDERED" \
      | python -c "import json,sys
for policy in json.load(sys.stdin)['deployment_branch_policies']:
    print(json.dumps(policy))" \
      | while read -r POLICY; do
          printf '%s' "$POLICY" | gh api -X POST \
            "/repos/${ORG}/${REPO}/environments/${ENV}/deployment-branch-policies" --input -
        done
    COUNT=$((COUNT + 1))
    echo "APPLY ${REPO}:${ENV}"
  done
done
echo "APPLY-ENVIRONMENTS: APPLIED (${COUNT} environments)"
SHEOF
chmod +x access/runbooks/apply-environments.sh
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/runbooks/README.md <<'EOF'
# `access/runbooks/` — apply order

Executed by a human holding organisation-admin credentials. Every script is
**dry-run by default**; `--apply` is explicit, and in apply mode every script
requires `$ORG_LOGIN` and an authenticated `gh`. No build agent holds either.

The order below is the order declared in `access/arming/arming-order.yaml` and
checked by `access/tools/check_arming_order.py`. It is D101's order, and the
reason it is not negotiable is §98.2: *Teams granting Write exist before branch
protection is armed, so that no window opens in which no approval can satisfy the
gate.*

| Step | Command | Owner |
|---|---|---|
| AO-01 | `bash access/runbooks/apply-organisation.sh` | L5 |
| AO-02 | the owner-continuity check inside the same script | L5 |
| AO-03 | `bash access/runbooks/apply-teams.sh --input <registry-derived>.json` | L5 |
| AO-04 | `python access/codeowners/generate_codeowners.py --org "$ORG_LOGIN" --input <input>.json` | L5 |
| AO-05 | `bash access/runbooks/apply-branch-protection.sh --profile unarmed` | L5 |
| AO-06 | `bash access/runbooks/apply-environments.sh` | L5 |
| AO-07 | record the bootstrap exceptions — not an access path; routed to L0 | L0 |
| AO-08 | `bash access/runbooks/apply-branch-protection.sh --profile armed` | L5 |
| AO-09 | add each required status-check context, per phase, once a workflow emits it | L2 |

## Running order, verbatim

```bash
set -euo pipefail
export ORG_LOGIN=<the organisation login>
gh auth status

bash access/runbooks/apply-organisation.sh                       # dry run
bash access/runbooks/apply-organisation.sh --apply

bash access/runbooks/apply-teams.sh --input interim-teams.json          # dry run
bash access/runbooks/apply-teams.sh --input interim-teams.json --apply

bash access/runbooks/apply-branch-protection.sh --profile unarmed          # dry run
bash access/runbooks/apply-branch-protection.sh --profile unarmed --apply

bash access/runbooks/apply-environments.sh                       # dry run
bash access/runbooks/apply-environments.sh --apply

# The bootstrap exceptions are L0's. Do not arm until they are recorded.

bash access/runbooks/apply-branch-protection.sh --profile armed --apply
```

## The one refusal that must not be worked around

`apply-branch-protection.sh --profile armed --apply` refuses, per repository,
when no Team on that repository holds `push`, `maintain` or `admin`. That is not
a bug and it is not a permissions problem with the token. It means the Teams step
has not happened for that repository, and arming the gate would leave nobody
whose approval counts — the outcome §95.4 describes as a team that experiences
its merges mysteriously breaking. Run `apply-teams.sh` and try again.
EOF
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
for s in access/runbooks/apply-*.sh; do bash -n "$s" && echo "SYNTAX-OK $s"; done
bash access/runbooks/apply-organisation.sh | tail -1
bash access/runbooks/apply-teams.sh --input access/testdata/teams/interim-teams.json | tail -1
bash access/runbooks/apply-branch-protection.sh --profile unarmed | tail -1
bash access/runbooks/apply-environments.sh | tail -1
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
git add access
git commit -m "$(printf 'L5-01-12: apply runbooks - dry-run by default, gh commands in D101 arming order\n\nLane: L5\n')"
git push -u origin lane/5/p1-apply-runbooks
```

### Acceptance criteria

| # | Criterion | Proving command | Expected output |
|---|---|---|---|
| L1 | All four scripts parse | `for s in access/runbooks/apply-*.sh; do bash -n "$s" \|\| echo BAD; done; echo SYNTAX-OK` | `SYNTAX-OK` |
| L2 | Organisation dry run completes with four calls | `bash access/runbooks/apply-organisation.sh \| tail -1` | `APPLY-ORGANISATION: DRY-RUN COMPLETE (4 calls)` |
| L3 | Teams dry run completes with three grants | `bash access/runbooks/apply-teams.sh --input access/testdata/teams/interim-teams.json \| tail -1` | `APPLY-TEAMS: DRY-RUN COMPLETE (3 grants)` |
| L4 | Branch-protection dry run completes | `bash access/runbooks/apply-branch-protection.sh --profile unarmed \| tail -1` | `APPLY-BRANCH-PROTECTION: DRY-RUN COMPLETE (profile=unarmed)` |
| L5 | Environments dry run completes | `bash access/runbooks/apply-environments.sh \| tail -1` | `APPLY-ENVIRONMENTS: DRY-RUN COMPLETE (3 environments)` |
| L6 | An unsatisfiable arming order is refused (executed negative test) | `bash access/runbooks/apply-branch-protection.sh --profile armed --arming-config access/testdata/arming/write-after-arming.yaml >/dev/null 2>&1; echo $?` | `4` |
| L7 | The D101 per-repository refusal exists in code | `grep -c 'REFUSED on ' access/runbooks/apply-branch-protection.sh` | `1` |
| L8 | Repositories are enumerated dynamically, never listed | `grep -c 'gh api --paginate "/orgs/${ORG}/repos"' access/runbooks/apply-branch-protection.sh` | `1` |
| L9 | Apply mode is never the default | `grep -c '^APPLY=0$' access/runbooks/apply-organisation.sh access/runbooks/apply-teams.sh access/runbooks/apply-branch-protection.sh access/runbooks/apply-environments.sh \| grep -c ':1$'` | `4` |
| L10 | The README order is the arming order | `grep -oE 'AO-0[1-9]' access/runbooks/README.md \| head -9 \| tr '\n' ','` | `AO-01,AO-02,AO-03,AO-04,AO-05,AO-06,AO-07,AO-08,AO-09,` |
| L11 | No path outside `access/` touched | `git diff --name-only origin/integration...HEAD \| grep -cv '^access/' \| tr -d ' '` | `0` |

### SELF-VERIFY

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
for s in access/runbooks/apply-*.sh; do bash -n "$s" || echo BAD; done; echo "L1 SYNTAX-OK"
echo "L2 $(bash access/runbooks/apply-organisation.sh | tail -1)"
echo "L3 $(bash access/runbooks/apply-teams.sh --input access/testdata/teams/interim-teams.json | tail -1)"
echo "L4 $(bash access/runbooks/apply-branch-protection.sh --profile unarmed | tail -1)"
echo "L5 $(bash access/runbooks/apply-environments.sh | tail -1)"
ec=0; bash access/runbooks/apply-branch-protection.sh --profile armed --arming-config access/testdata/arming/write-after-arming.yaml >/dev/null 2>&1 || ec=$?; echo "L6 $ec"
echo "L7 $(grep -c 'REFUSED on ' access/runbooks/apply-branch-protection.sh)"
echo "L8 $(grep -c 'gh api --paginate "/orgs/${ORG}/repos"' access/runbooks/apply-branch-protection.sh)"
echo "L9 $(grep -c '^APPLY=0$' access/runbooks/apply-organisation.sh access/runbooks/apply-teams.sh access/runbooks/apply-branch-protection.sh access/runbooks/apply-environments.sh | grep -c ':1$')"
echo "L10 $(grep -oE 'AO-0[1-9]' access/runbooks/README.md | head -9 | tr '\n' ',')"
echo "L11 $(git diff --name-only origin/integration...HEAD | grep -cv '^access/' | tr -d ' ')"
```

Expected output, exactly:

```
L1 SYNTAX-OK
L2 APPLY-ORGANISATION: DRY-RUN COMPLETE (4 calls)
L3 APPLY-TEAMS: DRY-RUN COMPLETE (3 grants)
L4 APPLY-BRANCH-PROTECTION: DRY-RUN COMPLETE (profile=unarmed)
L5 APPLY-ENVIRONMENTS: DRY-RUN COMPLETE (3 environments)
L6 4
L7 1
L8 1
L9 4
L10 AO-01,AO-02,AO-03,AO-04,AO-05,AO-06,AO-07,AO-08,AO-09,
L11 0
```

### STOP

Stop and file a blocker if any of the following is true.

- `L6` prints `0`. `apply-branch-protection.sh` would arm a gate while the declared arming order is unsatisfiable.
- `L7` prints `0`. The per-repository D101 refusal is missing, and arming can open the window §98.2 exists to close.
- In apply mode, `apply-branch-protection.sh --profile armed` refuses on a repository. **Do not add a flag to skip the check and do not grant Admin and arm it by hand.** Run `apply-teams.sh` for that repository first. If that is not possible, the refusal is the blocker.
- `apply-organisation.sh --apply` exits `5`. The organisation has one Owner and no attested escrow. §98.2 makes this a Phase 1 completion condition; setting `ESCROW_ATTESTED=yes` without an actual sealed escrow falsifies a completion check.
- A repository name would have to be written into any of these scripts. §11 forbids it; enumerate with `gh api --paginate`.

```bash
set -euo pipefail
bash access/tools/blocker.sh L5-01-12 "an apply runbook does not enforce the D101 order" "<the failing criterion line>" "bash access/runbooks/apply-branch-protection.sh --profile armed --arming-config access/testdata/arming/write-after-arming.yaml" "<its exact output>" "<the expected line from the SELF-VERIFY block>" "<one sentence of fact>"
```

---

## L5-01-13 — Phase 1 access completion check — offline assertions plus the negative-test register

| Field | Value |
|---|---|
| Size | M |
| Depends on | L5-01-03, L5-01-04, L5-01-05, L5-01-06, L5-01-07, L5-01-08, L5-01-09, L5-01-10, L5-01-11 |
| Writes | `access/checks/phase1-access-check.sh`, `access/checks/phase1_assertions.py`, `access/checks/negative-tests.yaml`, `access/schemas/negative-tests.schema.json` |
| Spec | §98.2 Phase 1 completion check, clause by clause; §95.4 activation checklist; D53; D89; D101 |

The §98.2 Phase 1 completion check is one long sentence with twelve clauses. This task turns each into a row that is either **asserted offline here** or **routed, with its owner named**. Nothing is left implicit, because a completion check with an unowned clause is a completion check that passes for the wrong reason.

Eight clauses are asserted offline, with no credentials and no organisation. Four are routed: two to L0, one to L2, and one to the L5 phase file that owns subsystem K (`access/ai-runtime/**` — a different file, out of scope here per §0.2). The register records all twelve.

Two clauses of §95.4 — *a Read-only approval does not satisfy it; a Write-holding cross-reviewer approval does* — are executable only at two humans with Write. They are registered with `execution_mode: at_headcount`, and their offline half (the §11.1 semantics table) is asserted now.

**Commands**

```bash
set -e
cd "$(git rev-parse --show-toplevel)"
export CONTROL_PLANE_ROOT="$PWD"
git fetch origin
git checkout integration
git pull --ff-only origin integration
test -f access/model/owner-continuity.yaml || { echo "MISSING DEPENDENCY L5-01-11"; exit 1; }
test -f access/plan-tier/plan-tier.yaml || { echo "MISSING DEPENDENCY L5-01-09"; exit 1; }
git checkout -b lane/5/p1-phase1-check
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/checks/negative-tests.yaml <<'YAMLEOF'
# access/checks/negative-tests.yaml
# The Section 98.2 Phase 1 completion check, clause by clause, plus the two
# Section 95.4 activation-checklist rows that only two humans with Write can
# execute. Every row is either asserted offline here or routed with its owner
# named. A completion check with an unowned clause passes for the wrong reason.
document: negative-tests
spec_sections: ["98.2", "95.4", "11.1", "11.3"]
decisions: ["D53", "D89", "D101"]

tests:
  - id: NEG-01
    statement: An approval from a Read-only account does NOT satisfy branch protection.
    spec_section: "98.2"
    execution_mode: at_headcount
    executed_by: L5
    headcount_trigger: two humans with Write (Section 95.4)
    offline_half: the Section 11.1 semantics table asserts that a Read approval does not count
    evidence_command: python access/tools/check_permission_semantics.py

  - id: NEG-02
    statement: An approval from a Write-holding Cross-Reviewer DOES satisfy branch protection.
    spec_section: "98.2"
    execution_mode: at_headcount
    executed_by: L5
    headcount_trigger: two humans with Write (Section 95.4)
    offline_half: the Section 11.1 semantics table asserts that a Write approval counts
    evidence_command: python access/tools/check_permission_semantics.py

  - id: NEG-03
    statement: An approval from a machine account does NOT satisfy branch protection - CODEOWNERS is generated to contain human identities only.
    spec_section: "98.2"
    execution_mode: offline_now
    executed_by: L5
    evidence_command: bash access/codeowners/test_generate_codeowners.sh

  - id: NEG-04
    statement: A workflow pushed to a non-default branch declaring environment production obtains no environment secret.
    spec_section: "98.2"
    execution_mode: by_lane_L2
    executed_by: L2
    routing_reason: >-
      Executing it requires pushing a workflow file, and .github/workflows/** is
      L2's path. This lane declares the environment configuration that makes the
      test pass and writes no workflow.
    evidence_command: declared in access/environments/deployment-policies.yaml

  - id: NEG-05
    statement: The minimal exceptions.yaml schema validator - expiry, owner, deactivation trigger present - rejects a deliberately malformed exception.
    spec_section: "98.2"
    execution_mode: routed_to_L0
    executed_by: L0
    routing_reason: >-
      exceptions.yaml is not an access/** artifact. This lane records the
      dependency and configures nothing there.
    evidence_command: routed

  - id: NEG-06
    statement: No direct human push to any default branch succeeds on the control-plane repository, and the repository admits no machine bypass actor.
    spec_section: "98.2"
    execution_mode: at_apply_time
    executed_by: L5
    offline_half: the armed profile renders enforce_admins true and blocks force pushes and deletions
    evidence_command: bash access/runbooks/apply-branch-protection.sh --profile armed

  - id: NEG-07
    statement: Organisation-enforced 2FA is active, with hardware keys or passkeys for the Founder, organisation Owners and platform-admin holders.
    spec_section: "98.2"
    execution_mode: offline_now
    executed_by: L5
    evidence_command: python access/checks/phase1_assertions.py

  - id: NEG-08
    statement: Teams granting Write exist before branch protection is armed, so that no window opens in which no approval can satisfy the gate.
    spec_section: "98.2"
    execution_mode: offline_now
    executed_by: L5
    evidence_command: python access/tools/check_arming_order.py

  - id: NEG-09
    statement: A second organisation Owner or an escrowed break-glass Owner credential exists with a named escrow custodian.
    spec_section: "98.2"
    execution_mode: at_apply_time
    executed_by: L5
    offline_half: access/model/owner-continuity.yaml declares the requirement and the escrow mechanics
    evidence_command: bash access/runbooks/apply-organisation.sh --apply

  - id: NEG-10
    statement: No API key is present anywhere, including shell profiles and repository .env files.
    spec_section: "98.2"
    execution_mode: routed_to_l5_subsystem_k
    executed_by: L5
    routing_reason: >-
      The API-key-free check lives under access/ai-runtime/checks/, which is
      subsystem K and belongs to a different L5 phase file. This file writes only
      the paths listed in its own scope statement.
    evidence_command: routed

  - id: NEG-11
    statement: The organisation export's first run is scheduled in Phase 2, or its absence is recorded as a dated accepted risk.
    spec_section: "98.2"
    execution_mode: routed_to_L0
    executed_by: L0
    routing_reason: >-
      The export schedule and the accepted-risk record are not access/**
      artifacts.
    evidence_command: routed

  - id: NEG-12
    statement: The reconciler credential's declared repair scope is the only machine write path admitted on the control-plane repository; the records-writer holds no credential there.
    spec_section: "98.2"
    execution_mode: offline_now
    executed_by: L5
    evidence_command: python access/checks/phase1_assertions.py

summary:
  offline_now: 4
  at_headcount: 2
  at_apply_time: 2
  by_lane_L2: 1
  routed_to_L0: 2
  routed_to_l5_subsystem_k: 1
  total: 12
YAMLEOF
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/schemas/negative-tests.schema.json <<'JSONEOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  # NEEDS_URN (FD-050): replace with urn:multiproduct:schemas:<type>:<version>
  "$id": "https://control-plane.invalid/access/negative-tests.schema.json",
  "x-target": "access/checks/negative-tests.yaml",
  "title": "The Phase 1 access negative-test register (spec Section 98.2, Section 95.4)",
  "type": "object",
  "additionalProperties": false,
  "required": ["document", "spec_sections", "decisions", "tests", "summary"],
  "properties": {
    "document": {"const": "negative-tests"},
    "spec_sections": {"type": "array", "items": {"type": "string"}, "minItems": 1},
    "decisions": {"type": "array", "items": {"type": "string"}, "minItems": 1},
    "tests": {
      "type": "array",
      "minItems": 12,
      "maxItems": 12,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["id", "statement", "spec_section", "execution_mode",
                     "executed_by", "evidence_command"],
        "properties": {
          "id": {"type": "string", "pattern": "^NEG-(0[1-9]|1[0-2])$"},
          "statement": {"type": "string", "minLength": 1},
          "spec_section": {"type": "string"},
          "execution_mode": {"enum": ["offline_now", "at_headcount", "at_apply_time",
                                      "by_lane_L2", "routed_to_L0",
                                      "routed_to_l5_subsystem_k"]},
          "executed_by": {"enum": ["L0", "L2", "L5"]},
          "headcount_trigger": {"type": "string"},
          "offline_half": {"type": "string"},
          "routing_reason": {"type": "string"},
          "evidence_command": {"type": "string", "minLength": 1}
        }
      }
    },
    "summary": {
      "type": "object",
      "additionalProperties": false,
      "required": ["offline_now", "at_headcount", "at_apply_time", "by_lane_L2",
                   "routed_to_L0", "routed_to_l5_subsystem_k", "total"],
      "properties": {
        "offline_now": {"type": "integer"},
        "at_headcount": {"type": "integer"},
        "at_apply_time": {"type": "integer"},
        "by_lane_L2": {"type": "integer"},
        "routed_to_L0": {"type": "integer"},
        "routed_to_l5_subsystem_k": {"type": "integer"},
        "total": {"const": 12}
      }
    }
  }
}
JSONEOF
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/checks/phase1_assertions.py <<'PYEOF'
#!/usr/bin/env python
"""The eight offline assertions of the Section 98.2 Phase 1 access completion check.

Runs with no credentials, no organisation and no network. Each assertion maps to
a clause of the Section 98.2 completion-check sentence. The four clauses that
cannot be asserted offline are printed as ROUTED with their owner named, because
a completion check with an unowned clause passes for the wrong reason.

Exit 0 on success, 1 on any failed assertion.
"""
import json
import os
import subprocess
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))


def load(relative):
    with open(os.path.join(ROOT, relative), "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def render(profile):
    result = subprocess.run(
        [sys.executable,
         os.path.join(ROOT, "access", "tools", "render_protection_payload.py"),
         "--profile", profile],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        return {}
    return json.loads(result.stdout.decode("utf-8"))


def main():
    org = load("access/model/organisation.yaml")
    semantics = load("access/model/permission-semantics.yaml")
    teams = load("access/model/teams.yaml")
    protection = load("access/branch-protection/branch-protection.yaml")
    continuity = load("access/model/owner-continuity.yaml")
    register = load("access/checks/negative-tests.yaml")

    armed = render("armed")
    unarmed = render("unarmed")
    counts = {}
    for entry in semantics["capabilities"]:
        if entry["id"] == "approval_counts_toward_required_approving_reviews":
            counts = entry["by_level"]

    assertions = [
        ("P1-01", "the armed profile blocks force pushes and deletions and applies "
                  "to administrators, in both profiles",
         armed.get("allow_force_pushes") is False
         and armed.get("allow_deletions") is False
         and armed.get("enforce_admins") is True
         and unarmed.get("enforce_admins") is True),
        ("P1-02", "the control-plane repository admits no machine bypass actor (D89)",
         protection["bypass_actors"]["control_plane_repository"] == "none"),
        ("P1-03", "a Read-only approval does not satisfy branch protection (Section 11.1)",
         counts.get("read") is False),
        ("P1-04", "a Write-holding Cross-Reviewer approval does, and Cross-Reviewers hold Write",
         counts.get("write") is True
         and teams["cross_reviewer"]["minimum_permission"] == "write"),
        ("P1-05", "CODEOWNERS is generated human-only and the check is executed negatively",
         protection["checklist"][10]["id"] == "BP-11"
         and os.path.exists(os.path.join(ROOT, "access", "codeowners",
                                         "test_generate_codeowners.sh"))),
        ("P1-06", "organisation-enforced 2FA is declared active with hardware keys or "
                  "passkeys for the Founder, Owners and platform-admin holders",
         org["two_factor"]["organisation_enforced"] is True
         and len(org["two_factor"]["strong_factor_required_for"]) == 3
         and set(org["two_factor"]["accepted_strong_factors"])
         == set(["hardware_security_key", "passkey"])),
        ("P1-09", "Teams granting Write precede arming, and the required-check list starts empty",
         teams["phase_1_interim"]["decision"] == "D101"
         and protection["required_status_checks"]["starts_empty_per_repository"] is True
         and len(armed.get("required_status_checks", {}).get("contexts", [1])) == 0),
        ("P1-11", "owner continuity is declared with an escrow custodian recorded elsewhere",
         continuity["escrow"]["custodian_named_here"] is False
         and len(continuity["requirement"]["satisfied_by_either"]) == 2),
    ]

    failed = 0
    for ident, statement, ok in assertions:
        if ok:
            print("%s OK   %s" % (ident, statement))
        else:
            print("%s FAIL %s" % (ident, statement))
            failed += 1

    routed = [test for test in register["tests"]
              if test["execution_mode"] in ("by_lane_L2", "routed_to_L0",
                                            "routed_to_l5_subsystem_k")]
    for test in routed:
        print("%s ROUTED to %s  %s" % (test["id"], test["executed_by"], test["statement"]))

    if failed:
        print("PHASE1-ACCESS-CHECK: FAIL (%d of %d assertions)" % (failed, len(assertions)))
        return 1
    print("PHASE1-ACCESS-CHECK: PASS (%d assertions, %d routed)"
          % (len(assertions), len(routed)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
PYEOF
chmod +x access/checks/phase1_assertions.py
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/checks/phase1-access-check.sh <<'SHEOF'
#!/usr/bin/env bash
# The Phase 1 access completion check (spec Section 98.2), offline.
# Runs every access/** checker in dependency order, then the eight offline
# assertions. No credentials, no organisation, no network.
set -eu
cd "$(git rev-parse --show-toplevel)"

python access/tools/validate_access_config.py         > /dev/null
python access/tools/check_permission_semantics.py     > /dev/null
python access/tools/check_team_derivation.py          > /dev/null
python access/tools/check_no_enterprise_dependency.py > /dev/null
python access/tools/check_arming_order.py             > /dev/null
bash   access/codeowners/test_generate_codeowners.sh  > /dev/null

# The arming gate must REJECT the forbidden order. A gate that accepts it is
# decoration, and the whole check is worthless (D101).
if python access/tools/check_arming_order.py \
     --config access/testdata/arming/write-after-arming.yaml >/dev/null 2>&1; then
  echo "PHASE1-ACCESS-CHECK: FAIL - the arming gate accepted a forbidden order" >&2
  exit 1
fi

python access/checks/phase1_assertions.py
SHEOF
chmod +x access/checks/phase1-access-check.sh
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
python access/tools/validate_access_config.py
bash access/checks/phase1-access-check.sh
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
git add access
git commit -m "$(printf 'L5-01-13: Phase 1 access completion check and the negative-test register\n\nLane: L5\n')"
git push -u origin lane/5/p1-phase1-check
```

### Acceptance criteria

| # | Criterion | Proving command | Expected output |
|---|---|---|---|
| M1 | All eleven documents validate | `python access/tools/validate_access_config.py \| tail -1` | `ACCESS CONFIG VALIDATION PASSED (11 documents)` |
| M2 | The completion check passes offline | `bash access/checks/phase1-access-check.sh \| tail -1` | `PHASE1-ACCESS-CHECK: PASS (8 assertions, 4 routed)` |
| M3 | Twelve §98.2 clauses are registered | `python -c "import yaml;print(len(yaml.safe_load(open('access/checks/negative-tests.yaml'))['tests']))"` | `12` |
| M4 | No clause is unowned | `python -c "import yaml;d=yaml.safe_load(open('access/checks/negative-tests.yaml'));print(sum(1 for t in d['tests'] if not t.get('executed_by')))"` | `0` |
| M5 | Every routed clause names its reason | `python -c "import yaml;d=yaml.safe_load(open('access/checks/negative-tests.yaml'));r=[t for t in d['tests'] if t['execution_mode'] in ('by_lane_L2','routed_to_L0','routed_to_l5_subsystem_k')];print(sum(1 for t in r if t.get('routing_reason')),len(r))"` | `4 4` |
| M6 | The two §95.4 headcount rows are registered, not silently skipped | `python -c "import yaml;d=yaml.safe_load(open('access/checks/negative-tests.yaml'));print(sum(1 for t in d['tests'] if t['execution_mode']=='at_headcount'))"` | `2` |
| M7 | The machine-approval clause is executed, not asserted | `python -c "import yaml;d=yaml.safe_load(open('access/checks/negative-tests.yaml'));print([t for t in d['tests'] if t['id']=='NEG-03'][0]['execution_mode'])"` | `offline_now` |
| M8 | A machine bypass actor fails the check (negative test) | see SELF-VERIFY | `1` |
| M9 | No path outside `access/` touched | `git diff --name-only origin/integration...HEAD \| grep -cv '^access/' \| tr -d ' '` | `0` |

### SELF-VERIFY

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
echo "M1 $(python access/tools/validate_access_config.py | tail -1)"
echo "M2 $(bash access/checks/phase1-access-check.sh | tail -1)"
echo "M3 $(python -c "import yaml;print(len(yaml.safe_load(open('access/checks/negative-tests.yaml'))['tests']))")"
echo "M4 $(python -c "import yaml;d=yaml.safe_load(open('access/checks/negative-tests.yaml'));print(sum(1 for t in d['tests'] if not t.get('executed_by')))")"
echo "M5 $(python -c "import yaml;d=yaml.safe_load(open('access/checks/negative-tests.yaml'));r=[t for t in d['tests'] if t['execution_mode'] in ('by_lane_L2','routed_to_L0','routed_to_l5_subsystem_k')];print(sum(1 for t in r if t.get('routing_reason')),len(r))")"
echo "M6 $(python -c "import yaml;d=yaml.safe_load(open('access/checks/negative-tests.yaml'));print(sum(1 for t in d['tests'] if t['execution_mode']=='at_headcount'))")"
echo "M7 $(python -c "import yaml;d=yaml.safe_load(open('access/checks/negative-tests.yaml'));print([t for t in d['tests'] if t['id']=='NEG-03'][0]['execution_mode'])")"
cp access/branch-protection/branch-protection.yaml access/branch-protection/branch-protection.yaml.bak
trap 'cp access/branch-protection/branch-protection.yaml.bak access/branch-protection/branch-protection.yaml; rm -f access/branch-protection/branch-protection.yaml.bak' EXIT
sed -i 's/^  control_plane_repository: none$/  control_plane_repository: renovate/' access/branch-protection/branch-protection.yaml
ec=0; python access/checks/phase1_assertions.py >/dev/null 2>&1 || ec=$?; echo "M8 $ec"
git checkout -- access/branch-protection/branch-protection.yaml
rm access/branch-protection/branch-protection.yaml.bak
trap - EXIT
echo "M9 $(git diff --name-only origin/integration...HEAD | grep -cv '^access/' | tr -d ' ')"
```

Expected output, exactly:

```
M1 ACCESS CONFIG VALIDATION PASSED (11 documents)
M2 PHASE1-ACCESS-CHECK: PASS (8 assertions, 4 routed)
M3 12
M4 0
M5 4 4
M6 2
M7 offline_now
M8 1
M9 0
```

### STOP

Stop and file a blocker if any of the following is true.

- `M2` prints a `FAIL` line. Read which `P1-` assertion failed; each maps to a named clause of the §98.2 completion check, and each has a task that owns it.
- `M8` prints `0`. The completion check does not notice a machine bypass actor on the control-plane repository — the exact condition D89 forbids.
- An `execution_mode` looks like it should move from `routed_to_L0` to `offline_now` so the number goes up. The routed clauses are routed because their artifacts are not `access/**` paths (§0.2). Claiming them is a partition violation.
- Any clause of §98.2 cannot be mapped to a row here. Do not drop it; file the blocker so L0 assigns it.

```bash
set -euo pipefail
bash access/tools/blocker.sh L5-01-13 "the Phase 1 access completion check does not hold" "<the failing criterion line>" "bash access/checks/phase1-access-check.sh" "<its exact output>" "PHASE1-ACCESS-CHECK: PASS (8 assertions, 4 routed)" "<one sentence of fact>"
```

---

## L5-01-14 — Per-repository transition note template and generator (§95.4)

| Field | Value |
|---|---|
| Size | S |
| Depends on | L5-01-12 |
| Writes | `access/runbooks/transition-note.template.md`, `access/tools/generate_transition_note.py`, `access/schemas/transition-note-input.schema.json`, `access/testdata/transition/reference-input.json`, `access/testdata/transition/routing-claimed-but-empty.json`, `access/testdata/transition/short-window.json` |
| Spec | §95.4 ("Phase 1 also produces a **one-page per-repository transition note**…"); §98.2 Phase 1 |

§95.4 is precise about what this note must contain and about the one thing it must never do:

* how to merge this week under the new branch protection, who reviews what, and what changes when the next gate arms;
* who to ask when a merge blocks — **a named human**, the Founder during bootstrap and the Team Lead once the role fills — with a **same-day response commitment for the two weeks after branch protection lands on a repository**;
* and *"where the note would have to state a review routing that does not yet exist, it says so and names the date Phase 3 populates the assignment registries, rather than publishing a routing nothing can resolve."*

The generator enforces the last point in code. A note claiming a routing it cannot resolve is refused, and the two-week response window is checked arithmetically rather than trusted.

**Commands**

```bash
set -e
cd "$(git rev-parse --show-toplevel)"
export CONTROL_PLANE_ROOT="$PWD"
git fetch origin
git checkout integration
git pull --ff-only origin integration
test -f access/runbooks/README.md || { echo "MISSING DEPENDENCY L5-01-12"; exit 1; }
git checkout -b lane/5/p1-transition-note
mkdir -p access/testdata/transition
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/runbooks/transition-note.template.md <<'EOF'
# Transition note — {{PRODUCT_ID}}

Branch protection lands on this repository on **{{PROTECTION_LANDS_ON}}**, in the
**{{PROFILE}}** profile.

## How to merge this week

1. Push your branch. Direct pushes to the default branch are blocked from today.
2. Open a pull request against the default branch.
3. {{APPROVAL_SENTENCE}}
4. Pushing a new commit dismisses existing approvals. Get the approval last.

## Who reviews what

{{ROUTING_SECTION}}

## What changes when the next gate arms

{{NEXT_GATE_SENTENCE}}

## When a merge blocks

Ask **{{ASK_WHEN_BLOCKED}}**. Until **{{SAME_DAY_RESPONSE_UNTIL}}** — the two
weeks after branch protection lands here — you have a same-day response
commitment on any blocked merge.

If the block is a required status check that no run reports, that is a
configuration fault and not your change: say so and it is fixed, not worked
around.
EOF
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/testdata/transition/reference-input.json <<'JSONEOF'
{
  "product_id": "example-product",
  "profile": "unarmed",
  "protection_lands_on": "2026-09-03",
  "same_day_response_until": "2026-09-17",
  "ask_when_blocked": "the Founder (the Team Lead once that role fills)",
  "review_routing": {
    "available": false,
    "populated_at_phase": 3,
    "populated_on": "2026-09-15",
    "primary_owner": "",
    "cross_reviewer": ""
  },
  "next_gate": {
    "id": "BP-02",
    "arms_at": "two humans with Write",
    "effect": "required approving reviews moves from 0 to 1, Code Owner review becomes required, and approval of the most recent reviewable push becomes required"
  }
}
JSONEOF

cat > access/testdata/transition/routing-claimed-but-empty.json <<'JSONEOF'
{
  "product_id": "example-product",
  "profile": "armed",
  "protection_lands_on": "2026-09-03",
  "same_day_response_until": "2026-09-17",
  "ask_when_blocked": "the Founder",
  "review_routing": {
    "available": true,
    "populated_at_phase": 3,
    "populated_on": "2026-09-15",
    "primary_owner": "",
    "cross_reviewer": ""
  },
  "next_gate": {"id": "BP-06", "arms_at": "Phase 4", "effect": "required status checks appear"}
}
JSONEOF

cat > access/testdata/transition/short-window.json <<'JSONEOF'
{
  "product_id": "example-product",
  "profile": "unarmed",
  "protection_lands_on": "2026-09-03",
  "same_day_response_until": "2026-09-10",
  "ask_when_blocked": "the Founder",
  "review_routing": {
    "available": false,
    "populated_at_phase": 3,
    "populated_on": "2026-09-15",
    "primary_owner": "",
    "cross_reviewer": ""
  },
  "next_gate": {"id": "BP-02", "arms_at": "two humans with Write", "effect": "approvals become required"}
}
JSONEOF
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/schemas/transition-note-input.schema.json <<'JSONEOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  # NEEDS_URN (FD-050): replace with urn:multiproduct:schemas:<type>:<version>
  "$id": "https://control-plane.invalid/access/transition-note-input.schema.json",
  "x-target": "access/testdata/transition/reference-input.json",
  "title": "Per-repository transition note input (spec Section 95.4)",
  "description": "Supplied on the command line to access/tools/generate_transition_note.py. The x-target is the reference fixture, this interface's committed conformance witness.",
  "type": "object",
  "additionalProperties": false,
  "required": ["product_id", "profile", "protection_lands_on", "same_day_response_until",
               "ask_when_blocked", "review_routing", "next_gate"],
  "properties": {
    "product_id": {"type": "string", "minLength": 1},
    "profile": {"enum": ["unarmed", "armed"]},
    "protection_lands_on": {"type": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"},
    "same_day_response_until": {"type": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"},
    "ask_when_blocked": {"type": "string", "minLength": 1},
    "review_routing": {
      "type": "object",
      "additionalProperties": false,
      "required": ["available", "populated_at_phase", "populated_on",
                   "primary_owner", "cross_reviewer"],
      "properties": {
        "available": {"type": "boolean"},
        "populated_at_phase": {"const": 3},
        "populated_on": {"type": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"},
        "primary_owner": {"type": "string"},
        "cross_reviewer": {"type": "string"}
      }
    },
    "next_gate": {
      "type": "object",
      "additionalProperties": false,
      "required": ["id", "arms_at", "effect"],
      "properties": {
        "id": {"type": "string", "minLength": 1},
        "arms_at": {"type": "string", "minLength": 1},
        "effect": {"type": "string", "minLength": 1}
      }
    }
  }
}
JSONEOF
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
cat > access/tools/generate_transition_note.py <<'PYEOF'
#!/usr/bin/env python
"""Render the per-repository transition note of spec Section 95.4.

"The note is the difference between a team that experiences governance arriving
 and a team that experiences its merges mysteriously breaking."

Two rules are enforced in code rather than trusted:

  1. Where the review routing does not yet exist, the note SAYS SO and names the
     date Phase 3 populates the assignment registries. It never publishes a
     routing nothing can resolve. Claiming an available routing while the
     routing fields are empty is refused (exit 3).
  2. The same-day response commitment runs for exactly the two weeks after
     branch protection lands (Section 95.4). A window that is not 14 days is
     refused (exit 3).

Usage: generate_transition_note.py --input INPUT.json [--template PATH]
Exit codes: 0 note on stdout | 3 input refused
"""
import argparse
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
TEMPLATE = os.path.join(ROOT, "access", "runbooks", "transition-note.template.md")

APPROVAL = {
    "unarmed": ("A review is requested automatically from the Code Owners. "
                "No approving review is required to merge yet; that arms later."),
    "armed": ("One approving review is required, it must come from a Code Owner, "
              "and it must approve the most recent reviewable push. "
              "A review from an account holding only Read does not count."),
}


def refuse(reason):
    sys.stderr.write("TRANSITION-NOTE-REFUSED %s\n" % reason)
    sys.exit(3)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--template", default=TEMPLATE)
    args = parser.parse_args()

    if not os.path.exists(args.input):
        refuse("input document not found: %s" % args.input)
    with open(args.input, "r", encoding="utf-8") as handle:
        try:
            doc = json.load(handle)
        except ValueError as exc:
            refuse("input document is not valid JSON: %s" % exc)

    try:
        lands = datetime.date(*[int(part) for part in doc["protection_lands_on"].split("-")])
        until = datetime.date(*[int(part) for part in doc["same_day_response_until"].split("-")])
    except (KeyError, TypeError, ValueError):
        refuse("protection_lands_on and same_day_response_until must both be YYYY-MM-DD")
    if (until - lands).days != 14:
        refuse("the same-day response commitment must run exactly 14 days from "
               "protection_lands_on (Section 95.4); got %d" % (until - lands).days)

    routing = doc["review_routing"]
    if routing["available"]:
        if not routing.get("primary_owner") or not routing.get("cross_reviewer"):
            refuse("review_routing.available is true but the routing is empty. "
                   "Section 95.4: never publish a routing nothing can resolve.")
        routing_section = (
            "- Primary Owner: %s\n- Cross-Reviewer: %s\n\n"
            "A Cross-Reviewer holds Write on this repository. That is not a "
            "privilege escalation: an approval from an account holding only Read "
            "does not satisfy branch protection, so a Read-only cross-review "
            "leaves the merge blocked."
            % (routing["primary_owner"], routing["cross_reviewer"])
        )
    else:
        routing_section = (
            "**The review routing for this repository does not exist yet.** The "
            "assignment registries are populated at Phase 3, on %s. Until then, "
            "review requests route to the Code Owners generated from the interim "
            "assignment set, and this note deliberately publishes no routing "
            "table rather than one nothing can resolve."
            % routing["populated_on"]
        )

    with open(args.template, "r", encoding="utf-8") as handle:
        text = handle.read()

    replacements = [
        ("{{PRODUCT_ID}}", doc["product_id"]),
        ("{{PROFILE}}", doc["profile"]),
        ("{{PROTECTION_LANDS_ON}}", doc["protection_lands_on"]),
        ("{{SAME_DAY_RESPONSE_UNTIL}}", doc["same_day_response_until"]),
        ("{{ASK_WHEN_BLOCKED}}", doc["ask_when_blocked"]),
        ("{{APPROVAL_SENTENCE}}", APPROVAL[doc["profile"]]),
        ("{{ROUTING_SECTION}}", routing_section),
        ("{{NEXT_GATE_SENTENCE}}",
         "Gate %s arms at %s. Effect: %s."
         % (doc["next_gate"]["id"], doc["next_gate"]["arms_at"],
            doc["next_gate"]["effect"])),
    ]
    for token, value in replacements:
        text = text.replace(token, value)

    if "{{" in text:
        refuse("an unfilled template token remains: a note with a placeholder is "
               "not a note")

    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
PYEOF
chmod +x access/tools/generate_transition_note.py
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
python access/tools/validate_access_config.py
python access/tools/generate_transition_note.py --input access/testdata/transition/reference-input.json
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
git add access
git commit -m "$(printf 'L5-01-14: per-repository transition note template and generator (Section 95.4)\n\nLane: L5\n')"
git push -u origin lane/5/p1-transition-note
```

### Acceptance criteria

| # | Criterion | Proving command | Expected output |
|---|---|---|---|
| N1 | All twelve documents validate | `python access/tools/validate_access_config.py \| tail -1` | `ACCESS CONFIG VALIDATION PASSED (12 documents)` |
| N2 | The reference note renders | `python access/tools/generate_transition_note.py --input access/testdata/transition/reference-input.json >/dev/null 2>&1; echo $?` | `0` |
| N3 | No template token survives | `python access/tools/generate_transition_note.py --input access/testdata/transition/reference-input.json \| grep -c '{{' \|\| true` | `0` |
| N4 | The absent routing is stated, not invented | `python access/tools/generate_transition_note.py --input access/testdata/transition/reference-input.json \| grep -c 'does not exist yet'` | `1` |
| N5 | The Phase 3 date is named | `python access/tools/generate_transition_note.py --input access/testdata/transition/reference-input.json \| grep -c '2026-09-15'` | `1` |
| N6 | The same-day commitment appears | `python access/tools/generate_transition_note.py --input access/testdata/transition/reference-input.json \| grep -c 'same-day response'` | `1` |
| N7 | A claimed-but-empty routing is refused (negative test) | `python access/tools/generate_transition_note.py --input access/testdata/transition/routing-claimed-but-empty.json >/dev/null 2>&1; echo $?` | `3` |
| N8 | A response window shorter than two weeks is refused (negative test) | `python access/tools/generate_transition_note.py --input access/testdata/transition/short-window.json >/dev/null 2>&1; echo $?` | `3` |
| N9 | No path outside `access/` touched | `git diff --name-only origin/integration...HEAD \| grep -cv '^access/' \| tr -d ' '` | `0` |

### SELF-VERIFY

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
echo "N1 $(python access/tools/validate_access_config.py | tail -1)"
ec=0; python access/tools/generate_transition_note.py --input access/testdata/transition/reference-input.json >/dev/null 2>&1 || ec=$?; echo "N2 $ec"
echo "N3 $(python access/tools/generate_transition_note.py --input access/testdata/transition/reference-input.json | grep -c '{{' || true)"
echo "N4 $(python access/tools/generate_transition_note.py --input access/testdata/transition/reference-input.json | grep -c 'does not exist yet')"
echo "N5 $(python access/tools/generate_transition_note.py --input access/testdata/transition/reference-input.json | grep -c '2026-09-15')"
echo "N6 $(python access/tools/generate_transition_note.py --input access/testdata/transition/reference-input.json | grep -c 'same-day response')"
ec=0; python access/tools/generate_transition_note.py --input access/testdata/transition/routing-claimed-but-empty.json >/dev/null 2>&1 || ec=$?; echo "N7 $ec"
ec=0; python access/tools/generate_transition_note.py --input access/testdata/transition/short-window.json >/dev/null 2>&1 || ec=$?; echo "N8 $ec"
echo "N9 $(git diff --name-only origin/integration...HEAD | grep -cv '^access/' | tr -d ' ')"
```

Expected output, exactly:

```
N1 ACCESS CONFIG VALIDATION PASSED (12 documents)
N2 0
N3 0
N4 1
N5 1
N6 1
N7 3
N8 3
N9 0
```

### STOP

Stop and file a blocker if any of the following is true.

- `N7` prints `0`. The generator published a routing table with empty routing. §95.4 forbids exactly that: *rather than publishing a routing nothing can resolve.*
- `N8` prints `0`. The two-week same-day response commitment is not enforced, and §95.4 makes it part of the note, not an aspiration.
- A routing field would have to be filled with a plausible name so the note "looks complete". A fabricated routing is worse than a declared absence, and it is a STOP.
- A rendered note is about to be sent to anyone. This task generates the note; distributing it is the Founder's, per §95.4 ("owned by the Founder").

```bash
set -euo pipefail
bash access/tools/blocker.sh L5-01-14 "the transition-note generator publishes an unresolvable routing" "<the failing criterion line>" "python access/tools/generate_transition_note.py --input access/testdata/transition/routing-claimed-but-empty.json" "<its exact output>" "TRANSITION-NOTE-REFUSED review_routing.available is true but the routing is empty." "<one sentence of fact>"
```

---

## L5-01-15 — Lane integration PR

| Field | Value |
|---|---|
| Size | S |
| Depends on | L5-01-13, L5-01-14 |
| Writes | nothing new — this task opens the pull request |
| Spec | PARTITION §"Branch & merge model"; §"Merge train" (L5 integrates last) |

Every preceding task pushed its own branch and its own pull request. This task rebases on `integration`, runs the whole lane's evidence once more on the merged result, and opens the lane's Phase 1 integration pull request. It writes no new file: a task that adds a file at integration time is a task that was never verified.

**Commands**

```bash
set -e
cd "$(git rev-parse --show-toplevel)"
export CONTROL_PLANE_ROOT="$PWD"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/5/p1-integration
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
# Every artifact this file promised must exist on integration before the PR opens.
for f in \
  access/README.md \
  access/tools/requirements.txt \
  access/tools/blocker.sh \
  access/tools/validate_access_config.py \
  access/schemas/README.md \
  access/model/organisation.yaml \
  access/model/owner-continuity.yaml \
  access/model/permission-semantics.yaml \
  access/model/teams.yaml \
  access/codeowners/generate_codeowners.py \
  access/codeowners/machine-identity-denylist.yaml \
  access/codeowners/test_generate_codeowners.sh \
  access/branch-protection/branch-protection.yaml \
  access/branch-protection/required-checks.md \
  access/environments/deployment-policies.yaml \
  access/plan-tier/plan-tier.yaml \
  access/arming/arming-order.yaml \
  access/runbooks/README.md \
  access/runbooks/apply-organisation.sh \
  access/runbooks/apply-teams.sh \
  access/runbooks/apply-branch-protection.sh \
  access/runbooks/apply-environments.sh \
  access/runbooks/transition-note.template.md \
  access/checks/phase1-access-check.sh \
  access/checks/phase1_assertions.py \
  access/checks/negative-tests.yaml \
  access/tools/check_permission_semantics.py \
  access/tools/check_team_derivation.py \
  access/tools/check_arming_order.py \
  access/tools/check_no_enterprise_dependency.py \
  access/tools/render_protection_payload.py \
  access/tools/render_environment_payload.py \
  access/tools/generate_transition_note.py \
  ; do
  test -f "$f" || { echo "MISSING ARTIFACT $f"; exit 1; }
done
echo "ALL 33 ARTIFACTS PRESENT"
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
python access/tools/validate_access_config.py | tail -1
bash access/checks/phase1-access-check.sh | tail -1
bash access/codeowners/test_generate_codeowners.sh | tail -1
python access/tools/check_permission_semantics.py
python access/tools/check_team_derivation.py
python access/tools/check_no_enterprise_dependency.py
python access/tools/check_arming_order.py
```

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
git commit --allow-empty -m "$(printf 'L5-01-15: Phase 1 access model integration - full lane evidence green\n\nLane: L5\n')"
git push -u origin lane/5/p1-integration
gh pr create --base integration --head lane/5/p1-integration \
  --title "L5-01: GitHub organisation and access model (Phase 1)" \
  --body "$(cat <<'BODY'
Lane L5, plan file Code/implementation/lanes/L5-01-org-and-access.md.
Tasks L5-01-01 through L5-01-15. Paths: access/** only.

Spec: Sections 11, 11.1, 11.2, 11.3, 11.4, 33.4, 95.2, 95.4, 98.2 Phase 1.
Decisions: D101, D73, D53, D89, D106. Signal SIG-03. Invariants 9, 79, 87.

Evidence, all offline and reproducible with no credentials:

  python access/tools/validate_access_config.py         -> PASSED (12 documents)
  bash   access/checks/phase1-access-check.sh           -> PASS (8 assertions, 4 routed)
  bash   access/codeowners/test_generate_codeowners.sh  -> PASS (8 cases)
  python access/tools/check_permission_semantics.py     -> PASS (7 assertions)
  python access/tools/check_team_derivation.py          -> PASS (6 assertions)
  python access/tools/check_no_enterprise_dependency.py -> PASS (4 assertions)
  python access/tools/check_arming_order.py             -> PASS (5 assertions)

Executed negative tests: the CODEOWNERS generator refuses a machine identity;
the arming gate rejects an order that grants Write after arming; the transition
note generator refuses a routing nothing can resolve.

Routed, not claimed: exceptions.yaml and the organisation export (L0), the
non-default-branch environment-secret test (L2), the API-key-free check
(subsystem K, a different L5 phase file). See access/checks/negative-tests.yaml.
BODY
)"
```

### Acceptance criteria

| # | Criterion | Proving command | Expected output |
|---|---|---|---|
| O1 | Every promised artifact is present | the artifact loop above | `ALL 33 ARTIFACTS PRESENT` |
| O2 | All twelve documents validate | `python access/tools/validate_access_config.py \| tail -1` | `ACCESS CONFIG VALIDATION PASSED (12 documents)` |
| O3 | The Phase 1 access completion check passes | `bash access/checks/phase1-access-check.sh \| tail -1` | `PHASE1-ACCESS-CHECK: PASS (8 assertions, 4 routed)` |
| O4 | The CODEOWNERS negative tests pass | `bash access/codeowners/test_generate_codeowners.sh \| tail -1` | `CODEOWNERS-NEGATIVE-TESTS: PASS (8 cases)` |
| O5 | The four standalone checkers pass | see SELF-VERIFY | four `PASS` lines |
| O6 | The whole lane touched no foreign path | `git diff --name-only origin/integration...HEAD \| grep -cv '^access/' \| tr -d ' '` | `0` |
| O7 | The root `CODEOWNERS` was never written | `git log --name-only --pretty=format: origin/integration..HEAD \| sort -u \| grep -c '^CODEOWNERS$' \| tr -d ' '` | `0` |
| O8 | The pull request targets `integration`, never `main` | `gh pr view --json baseRefName --jq .baseRefName` | `integration` |

### SELF-VERIFY

```bash
set -e
cd "$CONTROL_PLANE_ROOT"
echo "O2 $(python access/tools/validate_access_config.py | tail -1)"
echo "O3 $(bash access/checks/phase1-access-check.sh | tail -1)"
echo "O4 $(bash access/codeowners/test_generate_codeowners.sh | tail -1)"
echo "O5 $(python access/tools/check_permission_semantics.py)"
echo "O5 $(python access/tools/check_team_derivation.py)"
echo "O5 $(python access/tools/check_no_enterprise_dependency.py)"
echo "O5 $(python access/tools/check_arming_order.py)"
echo "O6 $(git diff --name-only origin/integration...HEAD | grep -cv '^access/' | tr -d ' ')"
echo "O7 $(git log --name-only --pretty=format: origin/integration..HEAD | sort -u | grep -c '^CODEOWNERS$' | tr -d ' ')"
echo "O8 $(gh pr view --json baseRefName --jq .baseRefName)"
```

Expected output, exactly:

```
O2 ACCESS CONFIG VALIDATION PASSED (12 documents)
O3 PHASE1-ACCESS-CHECK: PASS (8 assertions, 4 routed)
O4 CODEOWNERS-NEGATIVE-TESTS: PASS (8 cases)
O5 PERMISSION-SEMANTICS: PASS (7 assertions)
O5 TEAM-DERIVATION: PASS (6 assertions)
O5 PLAN-TIER: PASS (4 assertions)
O5 ARMING-ORDER: PASS (5 assertions)
O6 0
O7 0
O8 integration
```

### STOP

Stop and file a blocker if any of the following is true.

- `O1` prints `MISSING ARTIFACT`. A task in `L5-01-01` … `L5-01-14` did not merge. Do not create the missing file here; re-run the task that owns it.
- `O6` prints anything other than `0`. A foreign path is in the lane's diff and the lane-guard check will fail the PR (PARTITION rule 1).
- `O8` prints `main`. L5 never merges to `main` (§0.6).
- The rebase on `integration` produces a conflict in `access/**`. No other lane owns `access/**`, so a conflict there means someone crossed the partition. That is a STOP, not a merge to resolve.

```bash
set -euo pipefail
bash access/tools/blocker.sh L5-01-15 "the lane integration PR cannot be opened green" "<the failing criterion line>" "bash access/checks/phase1-access-check.sh" "<its exact output>" "PHASE1-ACCESS-CHECK: PASS (8 assertions, 4 routed)" "<one sentence of fact>"
```

---

## Appendix — what this file leaves to other lanes, stated once

Nothing below is a gap in this file. Each is a path this file does not own (§0.2), recorded here so that the next reader does not go looking for it in `access/**`.

| Left undone here | Owner | Where it is recorded |
|---|---|---|
| `exceptions.yaml` and its minimal Phase 1 schema validator | L0 | `arming-order.yaml` step `AO-07`; `negative-tests.yaml` row `NEG-05` |
| The workflows that emit the eight required status-check contexts | L2 | `branch-protection/required-checks.md`; `arming-order.yaml` step `AO-09` |
| The executed test that a non-default-branch workflow declaring `environment: production` gets no secret | L2 | `deployment-policies.yaml` `negative_test`; `negative-tests.yaml` row `NEG-04` |
| The reconciler that compares live access state against these declarations and raises SIG-03 | L3 | `teams.yaml` `derivation` |
| Provisioning that calls `generate_codeowners.py` and `render_protection_payload.py` at product creation | L3 | §0.3 of this file |
| Append-only enforcement on the records repository (D107) | L4 | cited in §0.2; configured nowhere here |
| The organisation export schedule and its accepted-risk record (D80) | L0 | `negative-tests.yaml` row `NEG-11` |
| The API-key-free check | L5, subsystem K, a different phase file | `negative-tests.yaml` row `NEG-10` |
| `infra/**`, `ops-vm/**`, `notify/**`, `assets/**` | L5, other phase files | §0.2 |

This file is complete when `L5-01-15` opens its pull request and criteria `O1` through `O8` print the lines above.
