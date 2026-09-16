# L1-01 — PHASE 1: CONTROL-PLANE REPOSITORY SKELETON

> **REFERENCE ONLY** — FD-095 (2026-09-09): Task bodies absorbed into L1-05-tasks.md. Do not execute from this file.

**Lane:** L1 — Registries & Contracts (subsystems **A** control-plane repository, **B** schema validation and CI gate engine — spec §99.2).
**Merge-train position:** FIRST (`L1 → L4 → L2 → L3 → L5`, PARTITION.md "Branch & merge model").
**Branch prefix:** `lane/1/*`.
**Repository:** `control-plane` (PARTITION.md "Repositories").
**Owned paths (exclusive):** `schemas/registry/**`, `schemas/product/**`, `registries/**`, `validators/registry/**`.

**Why this phase exists, in the spec's own words.** §99.4 item 1: the control-plane repository, schemas and CI validation are built "with effective dating and append-only discipline from the start, because retrofitting history is impossible by definition." §63.1 gives the mechanism — "state transitions with `start_date` and `end_date` — effective-dating, never in-place mutation — plus git history in the control-plane repository as the durable record" — and marks it **Priority: P0 — retrofitting history is impossible by definition.** Invariant **§101.7 #47** makes append-only history binding. §97.2 states the same rule for records: every record "never edits in place (corrections are follow-up records)". §98.2 Phase 1 requires the control-plane repository to exist and `people.yaml`, `roles.yaml`, `platform.yaml` to be authored in Week 1. §52.6 is the closed inventory of what may ever live in the control plane.

---

## 0. BINDING PRE-READ FOR THE EXECUTOR

Read this whole section before running any command. It is not optional context; three tasks below fail without it.

### 0.1 Shell

Every fenced `bash` block in this document runs in **Git Bash** on the working machine (POSIX `sh`). Do not translate to PowerShell. Do not substitute `NUL` for `/dev/null`. Use forward slashes.

### 0.2 Path-ownership rule (PARTITION.md, non-negotiable rule 1)

This lane may create or edit files **only** under:

```
schemas/registry/**
schemas/product/**
registries/**
validators/registry/**
```

Any other path — including `Makefile`, `.gitignore`, `README.md`, `CODEOWNERS`, `docs/**`, `contracts/**` — belongs to **L0 Integrator**. A pull request from this lane touching a foreign path FAILS the lane-guard check. There are no exceptions and no "just this once".

Where this phase needs content in an L0-owned root file, it does **not** write that file. It writes the content into an owned path and files an **L0 HANDOVER** issue containing the literal text L0 must paste. Task **L1-01-12** does this once, for all three root files this phase needs. <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

### 0.3 PATH MAPPING (binding for this lane)

§52.6 names control-plane artifacts by filename (`people.yaml`, `roles.yaml`, `platform.yaml`, …) and does not state a directory. PARTITION.md assigns `registries/**` to this lane and all root files to L0. Therefore, for every artifact this lane owns, the canonical location in the `control-plane` repository is:

| §52.6 artifact name | Canonical path in this repository | Lane |
| --- | --- | --- |
| `people.yaml` | `registries/people.yaml` | L1 |
| `roles.yaml` | `registries/roles.yaml` | L1 |
| `platform.yaml` | `registries/platform.yaml` | L1 |
| `topology.yaml` | `registries/topology.yaml` | L1 (not this phase) |
| `os-health.yaml` | `registries/os-health.yaml` | L1 (not this phase) |
| `policies.yaml` | `registries/policies.yaml` | L1 (not this phase) |
| `exceptions.yaml` | `registries/exceptions.yaml` | L1 (not this phase) |
| `patterns.yaml` | `registries/patterns.yaml` | L1 (not this phase) |
| `economics.yaml` | `registries/economics.yaml` | L1 (not this phase) |
| `platform-roadmap.yaml` | `registries/platform-roadmap.yaml` | L1 (not this phase) |
| `tools.yaml` | `registries/tools.yaml` | L1 (not this phase) |
| `ai-toolchain.yaml` | `registries/ai-toolchain.yaml` | L1 (not this phase) |
| `records/**`, `events/**` | the `control-plane-records` repository | **L4 — never L1** |

Do not create any file in the third column marked "not this phase". This phase creates exactly the three registries §98.2 Phase 1 names.

### 0.4 Spec access

The spec is at `C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md` (10,214 lines). Several tasks below transcribe from it by line number using `sed -n 'A,Bp'`. Set this once per shell session:

```bash
export SPEC="/c/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md"
test -f "$SPEC" && echo "SPEC_OK" || echo "SPEC_MISSING"
```

Expected output: `SPEC_OK`. If `SPEC_MISSING`, stop and file the blocker of §0.6 with `BLOCKED_ON=spec-file-unreachable`.

### 0.5 Environment variables this phase requires

| Variable | Meaning | Supplied by |
| --- | --- | --- |
| `CP_ORG` | The GitHub organisation login that owns `control-plane` | L0, in the task issue |
| `CP_REPO` | Fixed value `control-plane` | this document |
| `SPEC` | Absolute Git-Bash path to the spec | this document, §0.4 |
| `CP_ROOT` | Absolute Git-Bash path to the local clone | set by T02 |

`CP_ORG` is **not** guessable. If it is unset, T02 stops. Never invent an organisation name.

### 0.6 The blocker-issue template

Every STOP rule below files exactly this issue and then halts. Fill only the four `<>` fields; change nothing else.

```bash
gh issue create \
  --repo "$CP_ORG/$CP_REPO" \
  --title "BLOCKER L1-01-<TASKID>: <one-line condition>" \
  --label "blocker,lane-1,phase-L1-01" \
  --body "$(cat <<'EOF'
## Blocker

**Lane:** L1 — Registries & Contracts
**Phase:** L1-01 (control-plane repository skeleton)
**Task:** <TASKID>
**Blocked on:** <BLOCKED_ON key>

### What I ran
```
<the exact command, pasted>
```

### What I expected
<the exact expected output, from the task's SELF-VERIFY block>

### What I got
```
<the exact output, pasted>
```

### What I need to proceed
<the exact artifact, value or decision, and who owns it per PARTITION.md>

### What I did NOT do
I did not guess, substitute, redesign, or touch any path outside
schemas/registry/**, schemas/product/**, registries/**, validators/registry/**.
I have stopped on this task and started no dependent task.
EOF
)"
```

If `gh issue create` itself fails because the repository does not yet exist (only possible at T01/T02), write the same body to `C:/Users/Paresh/AppData/Local/Temp/claude/blocker-L1-01-<TASKID>.md` and stop.

### 0.7 Judgment rule

If a step below ever appears to require choosing, designing, naming, or interpreting, you have misread it. Stop and file the blocker. Every content decision in this phase is either transcribed verbatim from a cited spec line range or handed to L0 in a **DECISION REQUIRED** block.

---

## 1. TASK INDEX

| Task ID | Title | Size | Depends on |
| --- | --- | --- | --- |
| L1-01-01 | Preflight: toolchain, auth and spec availability | S | — | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
| L1-01-02 | Repository bootstrap: `git init`, `gh repo create`, initial commit | S | T01 | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
| L1-01-03 | Lane branch and owned-directory skeleton | S | T02 | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
| L1-01-04 | Per-directory `.gitignore` files inside owned paths | S | T03 | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
| L1-01-05 | `schemas/registry/CONVENTIONS.md` — effective dating and append-only | M | T03 | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
| L1-01-06 | Shared effective-dating and envelope JSON Schemas | M | T05 | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
| L1-01-07 | `registries/INVENTORY.md` — the §52.6 registry-of-files, transcribed | M | T03 | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
| L1-01-08 | Seed `registries/roles.yaml` (verbatim from §8) | M | T06 | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
| L1-01-09 | Seed `registries/people.yaml` (empty, schema-valid) | S | T06 | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
| L1-01-10 | Seed `registries/platform.yaml` | M | T06 | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
| L1-01-11 | `validators/registry/check-append-only.sh` | M | T05 | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
| L1-01-12 | `validators/registry/registry.mk` + the L0 handover packet | M | T04, T07, T11 | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->
| L1-01-13 | Phase gate: rebase, lane-guard self-check, PR to `integration` | S | T08, T09, T10, T12 | <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

Sizes: **S** ≤ 30 min, **M** ≤ 2 h, **L** ≤ 1 day, for the executor profile described in PARTITION.md §"AI developer profile".

---

## L1-01-01 — Preflight: toolchain, auth and spec availability <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Size:** S **Depends on:** —
**Creates/edits:** nothing. This task is read-only.

### Commands

```bash
set -euo pipefail
export SPEC="/c/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md"
export CP_REPO="control-plane"

echo "--- git ---";    git --version
echo "--- gh ---";     gh --version | head -1
echo "--- gh auth ---";gh auth status 2>&1 | head -5
echo "--- python ---"; python3 --version || python --version
echo "--- pyyaml ---"; python3 -c "import yaml; print('pyyaml', yaml.__version__)"
echo "--- jq ---";     jq --version
echo "--- spec ---";   test -f "$SPEC" && echo "SPEC_OK" || echo "SPEC_MISSING"
echo "--- CP_ORG ---"; test -n "$CP_ORG" && echo "CP_ORG_SET=$CP_ORG" || echo "CP_ORG_MISSING"
```

If `pyyaml` reports `ModuleNotFoundError`, run exactly:

```bash
set -euo pipefail
python3 -m pip install --user "PyYAML==6.0.2"
python3 -c "import yaml; print('pyyaml', yaml.__version__)"
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
| --- | --- | --- | --- |
| 1 | git present | `git --version >/dev/null 2>&1; echo $?` | `0` |
| 2 | gh present | `gh --version >/dev/null 2>&1; echo $?` | `0` |
| 3 | gh authenticated | `gh auth status >/dev/null 2>&1; echo $?` | `0` |
| 4 | python3 present | `python3 --version >/dev/null 2>&1; echo $?` | `0` |
| 5 | PyYAML importable | `python3 -c "import yaml" >/dev/null 2>&1; echo $?` | `0` |
| 6 | jq present | `jq --version >/dev/null 2>&1; echo $?` | `0` |
| 7 | Spec readable | `test -f "$SPEC"; echo $?` | `0` |
| 8 | `CP_ORG` supplied | `test -n "$CP_ORG"; echo $?` | `0` |

### SELF-VERIFY

```bash
FAIL=0
for c in "git --version" "gh --version" "gh auth status" "python3 --version" \
         "python3 -c import\ yaml" "jq --version"; do
  eval "$c" >/dev/null 2>&1 || { echo "MISSING: $c"; FAIL=1; }
done
test -f "$SPEC" || { echo "MISSING: spec"; FAIL=1; }
test -n "$CP_ORG" || { echo "MISSING: CP_ORG"; FAIL=1; }
test "$FAIL" -eq 0 && echo "T01 PASS" || echo "T01 FAIL"
```

**Correct output:** the single line `T01 PASS` and nothing else.

### STOP rule

Do not proceed to T02 if any of the eight criteria fails. In particular: **do not install git, gh or python yourself beyond the one `pip install` line given above, and never invent a value for `CP_ORG`.**

File the §0.6 blocker with:
- `<TASKID>` = `T01`
- `<one-line condition>` = `preflight failed: <the MISSING: line>`
- `<BLOCKED_ON key>` = one of `toolchain-missing`, `gh-not-authenticated`, `spec-file-unreachable`, `cp-org-not-supplied`

---

## L1-01-02 — Repository bootstrap: `git init`, `gh repo create`, initial commit <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Size:** S **Depends on:** T01
**Creates/edits:** the `control-plane` repository object; `registries/.gitkeep` (owned path) as the sole file of the initial commit.

**Why the initial commit contains only `registries/.gitkeep`.** A git commit must contain at least one file. `README.md` and `.gitignore` are root files and belong to L0 (PARTITION.md, L0 row). `registries/.gitkeep` is inside an L1-owned path, so the bootstrap commit violates no ownership rule. L0 adds the root files in its own commit; the handover text is prepared by T12.

### Commands

```bash
set -euo pipefail
export CP_REPO="control-plane"
export CP_ROOT="/c/D_Drive/PS/MultiProduct/control-plane"

# --- Step 1: is the repository already created (e.g. by L0 Phase 0)? ---
if gh repo view "$CP_ORG/$CP_REPO" >/dev/null 2>&1; then
  echo "REPO_EXISTS"
else
  echo "REPO_ABSENT"
fi
```

**Branch A — output was `REPO_ABSENT`. Run the full bootstrap:**

```bash
set -euo pipefail
mkdir -p "$CP_ROOT"
cd "$CP_ROOT"

git init --initial-branch=main
git config user.name  "$(gh api user --jq .login)"
git config user.email "$(gh api user --jq '.email // "noreply@users.noreply.github.com"')"

mkdir -p registries
: > registries/.gitkeep

git add registries/.gitkeep
git commit -m "$(cat <<'EOF'
chore(l1): bootstrap control-plane repository

Creates the control-plane repository required by spec Section 98.2
Phase 1 ("Create the control-plane repository") and Section 99.2
subsystem A.

The commit carries only registries/.gitkeep because every root file
(README.md, .gitignore, Makefile, CODEOWNERS) is owned by L0 under the
frozen partition contract; L1 owns registries/** and adds nothing else
here.

Refs: spec Sections 98.2, 99.2 (subsystem A), 52.6
Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"

gh repo create "$CP_ORG/$CP_REPO" \
  --private \
  --source . \
  --remote origin \
  --description "Control plane: registries, contracts, schemas, validators (spec Section 99.2 subsystem A)" \
  --push

git branch integration main
git push -u origin integration
```

**Branch B — output was `REPO_EXISTS`. Clone instead of creating:**

```bash
set -euo pipefail
rm -rf "$CP_ROOT"
gh repo clone "$CP_ORG/$CP_REPO" "$CP_ROOT"
cd "$CP_ROOT"
git fetch origin
git checkout integration 2>/dev/null || { git checkout -b integration origin/main && git push -u origin integration; }
mkdir -p registries && : > registries/.gitkeep
git add registries/.gitkeep
git diff --cached --quiet || git commit -m "chore(l1): add registries/ root for lane 1

Refs: spec Sections 98.2, 99.2 (subsystem A)
Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
git push origin integration
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
| --- | --- | --- | --- |
| 1 | Repository exists on GitHub | `gh repo view "$CP_ORG/$CP_REPO" --json name --jq .name` | `control-plane` |
| 2 | Repository is private | `gh repo view "$CP_ORG/$CP_REPO" --json isPrivate --jq .isPrivate` | `true` |
| 3 | Local clone is a git work tree | `cd "$CP_ROOT" && git rev-parse --is-inside-work-tree` | `true` |
| 4 | `origin` points at the right repo | `cd "$CP_ROOT" && git remote get-url origin \| grep -c "$CP_REPO"` | `1` |
| 5 | `main` exists on the remote | `gh api "repos/$CP_ORG/$CP_REPO/branches/main" --jq .name` | `main` |
| 6 | `integration` exists on the remote | `gh api "repos/$CP_ORG/$CP_REPO/branches/integration" --jq .name` | `integration` |
| 7 | No foreign path in history | `cd "$CP_ROOT" && git ls-tree -r --name-only HEAD \| grep -vcE '^(schemas/registry/|schemas/product/|registries/|validators/registry/)'` | `0` |

Criterion 7 is the ownership proof. If it returns anything other than `0` on Branch A, the bootstrap wrote a file it must not have; delete that file and re-commit before proceeding. On Branch B a non-zero count is expected only for files L0 already committed — in that case run instead:

```bash
cd "$CP_ROOT"
git log --format=%H -n1 -- . >/dev/null
git show --stat --name-only --format="" HEAD | grep -vcE '^(schemas/registry/|schemas/product/|registries/|validators/registry/)|^$'
```
which must print `0` (this lane's own last commit touched owned paths only).

### SELF-VERIFY

```bash
cd "$CP_ROOT"
A=$(gh repo view "$CP_ORG/$CP_REPO" --json name --jq .name)
B=$(gh repo view "$CP_ORG/$CP_REPO" --json isPrivate --jq .isPrivate)
C=$(git rev-parse --is-inside-work-tree)
D=$(gh api "repos/$CP_ORG/$CP_REPO/branches/integration" --jq .name 2>/dev/null)
E=$(git show --stat --name-only --format="" HEAD | grep -vcE '^(schemas/registry/|schemas/product/|registries/|validators/registry/)|^$')
if [ "$A" = "control-plane" ] && [ "$B" = "true" ] && [ "$C" = "true" ] \
   && [ "$D" = "integration" ] && [ "$E" = "0" ]; then echo "T02 PASS"; else echo "T02 FAIL A=$A B=$B C=$C D=$D E=$E"; fi
```

**Correct output:** the single line `T02 PASS`.

### STOP rule

Do not proceed if `gh repo create` fails with `HTTP 403`, `Resource not accessible by integration`, or `Name already exists on this account` in a form Branch B cannot handle. Do not create the repository under your personal account as a substitute. Do not make it public.

File the §0.6 blocker with `<TASKID>` = `T02` and `<BLOCKED_ON key>` = one of `no-org-repo-create-permission`, `org-login-wrong`, `repo-name-collision`.

> **DECISION REQUIRED — L0**
> **Subject:** GitHub organisation login and repository visibility for `control-plane`.
> **Why L1 cannot decide it:** the organisation login is estate configuration, not a lane artifact; §98.2 Phase 1 requires "one company-owned GitHub organisation" but names no login, and §99.5 fixes only the host (GitHub) and the plan tier (Team, D73).
> **What L0 must supply, exactly:** the value of `CP_ORG`, in the T02 task issue, before T02 is dispatched.
> **Blocking:** T02 and everything after it.

---

## L1-01-03 — Lane branch and owned-directory skeleton <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Size:** S **Depends on:** T02
**Creates/edits:**
```
schemas/registry/.gitkeep
schemas/registry/common/.gitkeep
schemas/product/.gitkeep
registries/.gitkeep          (already present from T02)
validators/registry/.gitkeep
```

### Commands

```bash
set -euo pipefail
cd "$CP_ROOT"
git fetch origin
git checkout integration
git pull --ff-only origin integration
git checkout -b lane/1/01-repo-skeleton

mkdir -p schemas/registry/common schemas/product registries validators/registry
: > schemas/registry/.gitkeep
: > schemas/registry/common/.gitkeep
: > schemas/product/.gitkeep
: > registries/.gitkeep
: > validators/registry/.gitkeep

git add schemas registries validators
git commit -m "$(cat <<'EOF'
chore(l1): create lane-1 owned directory skeleton

Creates the four path roots this lane owns exclusively under the frozen
partition contract: schemas/registry/**, schemas/product/**,
registries/**, validators/registry/**.

Refs: spec Sections 99.2 (subsystems A, B), 52.6
Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
git push -u origin lane/1/01-repo-skeleton
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
| --- | --- | --- | --- |
| 1 | On the lane branch | `git rev-parse --abbrev-ref HEAD` | `lane/1/01-repo-skeleton` |
| 2 | All four roots tracked | `git ls-files \| grep -cE '^(schemas/registry/|schemas/product/|registries/|validators/registry/)'` | `5` |
| 3 | Zero foreign paths tracked | `git ls-files \| grep -vcE '^(schemas/registry/|schemas/product/|registries/|validators/registry/)'` | `0` |
| 4 | Branch pushed | `git rev-parse HEAD` equals `git rev-parse origin/lane/1/01-repo-skeleton` | identical 40-char SHAs |

### SELF-VERIFY

```bash
cd "$CP_ROOT"
BR=$(git rev-parse --abbrev-ref HEAD)
OWNED=$(git ls-files | grep -cE '^(schemas/registry/|schemas/product/|registries/|validators/registry/)')
FOREIGN=$(git ls-files | grep -vcE '^(schemas/registry/|schemas/product/|registries/|validators/registry/)')
SAME=$([ "$(git rev-parse HEAD)" = "$(git rev-parse origin/lane/1/01-repo-skeleton)" ] && echo yes || echo no)
[ "$BR" = "lane/1/01-repo-skeleton" ] && [ "$OWNED" = "5" ] && [ "$FOREIGN" = "0" ] && [ "$SAME" = "yes" ] \
  && echo "T03 PASS" || echo "T03 FAIL BR=$BR OWNED=$OWNED FOREIGN=$FOREIGN SAME=$SAME"
```

**Correct output:** the single line `T03 PASS`.

### STOP rule

Do not proceed if criterion 3 returns anything other than `0`. That means a foreign path is tracked on this branch and the lane-guard check will reject the eventual PR (PARTITION.md rule 1). Do not delete a foreign file that L0 committed on `integration` — that is L0's file. Instead file the §0.6 blocker with `<TASKID>` = `T03`, `<BLOCKED_ON key>` = `foreign-path-on-lane-branch`, listing the offending paths from `git ls-files | grep -vE '^(schemas/registry/|schemas/product/|registries/|validators/registry/)'`.

---

## L1-01-04 — Per-directory `.gitignore` files inside owned paths <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Size:** S **Depends on:** T03
**Creates/edits:**
```
registries/.gitignore
schemas/registry/.gitignore
schemas/product/.gitignore
validators/registry/.gitignore
```

**Why not a root `.gitignore`.** The root `.gitignore` is an L0-owned root file (PARTITION.md, L0 row). Git honours a `.gitignore` in any directory, so this lane's ignore rules live in its own directories and require no foreign write. The proposed **root** `.gitignore` text is handed to L0 by T12.

### Commands

```bash
set -euo pipefail
cd "$CP_ROOT"

cat > registries/.gitignore <<'EOF'
# Lane 1 (Registries & Contracts) — registries/ ignore rules.
# Owned by L1 per the frozen partition contract. The ROOT .gitignore is
# owned by L0; see validators/registry/l0-handover/root-gitignore.proposed.
#
# Registries are the declared source of truth (spec Section 5.1) and are
# append-only under effective dating (Sections 63.1, 101.7 #47). Nothing
# generated, derived or transient may be committed beside them, because a
# derived file beside a declared one is how "derived data is computed,
# never hand-maintained" (invariant 46) silently stops being true.

*.generated.yaml
*.generated.yml
*.derived.yaml
*.derived.yml
*.rendered.yaml
*.bak
*.orig
*.rej
*~
.DS_Store
Thumbs.db
EOF

cat > schemas/registry/.gitignore <<'EOF'
# Lane 1 (Registries & Contracts) — schemas/registry/ ignore rules.
# schemas/registry/** is exclusively owned by L1 (PARTITION.md rule 1).
# Compiled or bundled schema output is build product, never source.

*.bundle.json
*.compiled.json
*.resolved.json
node_modules/
__pycache__/
*.pyc
*.bak
*.orig
*.rej
*~
.DS_Store
Thumbs.db
EOF

cat > schemas/product/.gitignore <<'EOF'
# Lane 1 (Registries & Contracts) — schemas/product/ ignore rules.
# schemas/product/** is exclusively owned by L1 (PARTITION.md rule 1).
# Compiled or bundled schema output is build product, never source.

*.bundle.json
*.compiled.json
*.resolved.json
node_modules/
__pycache__/
*.pyc
*.bak
*.orig
*.rej
*~
.DS_Store
Thumbs.db
EOF

cat > validators/registry/.gitignore <<'EOF'
# Lane 1 (Registries & Contracts) — validators/registry/ ignore rules.
# Validator run output is evidence, and evidence lives in the records
# repository (Section 97.1, D89), never here.

.venv/
__pycache__/
*.pyc
*.log
report/
out/
*.bak
*.orig
*.rej
*~
.DS_Store
Thumbs.db
EOF

git add registries/.gitignore schemas/registry/.gitignore schemas/product/.gitignore validators/registry/.gitignore
git commit -m "$(cat <<'EOF'
chore(l1): per-directory .gitignore for lane-1 owned paths

Ignore rules live in the lane's own directories because the root
.gitignore is an L0-owned root file under the frozen partition contract.
Excludes generated, derived and transient files from the declared-state
paths, per invariant 46 (derived data is computed, never hand-maintained)
and Section 97.1/D89 (validator output is evidence and belongs in the
records repository).

Refs: spec Sections 5.1, 97.1, 101.7 #46
Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
git push origin lane/1/01-repo-skeleton
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
| --- | --- | --- | --- |
| 1 | Four ignore files tracked | `git ls-files \| grep -c '\.gitignore$'` | `4` |
| 2 | No root `.gitignore` created by this lane | `git ls-files \| grep -c '^\.gitignore$'` | `0` |
| 3 | No bare `schemas/.gitignore` (foreign path) | `git ls-files \| grep -c '^schemas/\.gitignore$'` | `0` |
| 4 | All tracked gitignores are inside owned prefixes | `git ls-files \| grep '\.gitignore$' \| grep -vcE '^(schemas/registry/|schemas/product/|registries/|validators/registry/)'` | `0` |
| 5 | Rules are active | `touch registries/x.generated.yaml && git status --porcelain registries/x.generated.yaml \| wc -l` | `0` |
| 6 | Cleanup done | `rm -f registries/x.generated.yaml; test -e registries/x.generated.yaml; echo $?` | `1` |

### SELF-VERIFY

```bash
cd "$CP_ROOT"
N=$(git ls-files | grep -c '\.gitignore$')
R=$(git ls-files | grep -c '^\.gitignore$')
touch registries/x.generated.yaml
IG=$(git status --porcelain registries/x.generated.yaml | wc -l | tr -d ' ')
rm -f registries/x.generated.yaml
FOREIGN=$(git ls-files | grep '\.gitignore$' | grep -vcE '^(schemas/registry/|schemas/product/|registries/|validators/registry/)' || true)
[ "$N" = "4" ] && [ "$R" = "0" ] && [ "$IG" = "0" ] && [ "$FOREIGN" = "0" ] && echo "T04 PASS" || echo "T04 FAIL N=$N R=$R IG=$IG FOREIGN=$FOREIGN"
```

**Correct output:** the single line `T04 PASS`.

### STOP rule

Do not create `.gitignore` at the repository root, and do not edit one if L0 has already created it. If criterion 3 fails because a root `.gitignore` from L0 contradicts these rules (for example by force-including `*.generated.yaml`), file the §0.6 blocker with `<TASKID>` = `T04`, `<BLOCKED_ON key>` = `root-gitignore-conflict`, quoting the conflicting root line.

---

## L1-01-05 — `schemas/registry/CONVENTIONS.md`: effective dating and append-only <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Size:** M **Depends on:** T03
**Creates/edits:** `schemas/registry/CONVENTIONS.md`

This is the day-one discipline §99.4 item 1 says cannot be retrofitted. Every rule below is transcribed from a cited spec line; none is invented.

### Commands

```bash
set -euo pipefail
cd "$CP_ROOT"
cat > schemas/registry/CONVENTIONS.md <<'EOF'
# Registry record conventions — effective dating and append-only

**Status:** binding from the first commit of this repository.
**Owner:** Lane 1 (Registries & Contracts), subsystems A and B of spec Section 99.2.
**Scope:** every file under `registries/**`, and every schema under
`schemas/registry/**` and `schemas/product/**` that validates one.

## 0. Why this file exists before anything else

Spec Section 99.4, item 1 of the minimal honest V1:

> Control-plane repository, schemas and CI validation — with effective dating and
> append-only discipline from the start, because retrofitting history is impossible
> by definition.

Spec Section 63.1 marks immutable history **Priority: P0 — retrofitting history is
impossible by definition**, and invariant 47 (Section 101.7) makes it
non-negotiable:

> History is append-only for state, decisions, approvals and records; records are
> not deleted and state changes are recorded, not overwritten.

## 1. The effective-dating mechanism

Section 63.1 states the mechanism exactly:

> **Mechanism:** state transitions with `start_date` and `end_date` — effective-dating,
> never in-place mutation — plus git history in the control-plane repository as the
> durable record. No separate audit database is introduced.

Therefore:

* **C1 — Dated fields are named `start_date` and `end_date`.** No synonym is
  permitted anywhere in `registries/**`: not `from`/`to`, not `valid_from`,
  not `effective_from`, not `since`. Section 7 uses `start_date` and `end_date`
  on every person record; Section 60.3 uses `deadline` for a migration target,
  which is a different concept and is not an effective-dating field.
* **C2 — `end_date` is always present, and `null` means open-ended.** An absent
  key is a malformed record, not an open interval. Section 7 writes
  `end_date: null` explicitly on an open-ended employee record.
* **C3 — `end_date` is mandatory and non-null for every non-employee.**
  Section 7.1: "`end_date` **is mandatory for every non-employee.** A CI check
  fails if a contractor, intern, temporary specialist or consultant has a null
  end date."
* **C4 — Dates are ISO-8601 calendar dates, `YYYY-MM-DD`.** Timestamps, where a
  registry carries one, are UTC with offset, per Section 97.1: "Every record and
  event timestamp is stored in UTC with its offset."
* **C5 — Business-day and working-hour rules never resolve against a runner's
  local clock.** Section 97.1: they resolve "against the declared working
  calendar and operating timezone held in the leave records (Section 6.4) —
  never against a runner's local time." Timezones in `registries/people.yaml`
  are IANA identifiers, never UTC offsets (Section 7 `work_arrangement.timezone`).

## 2. The append-only rules

Section 63.1 names what is never overwritten destructively:

> ownership, reviewer assignments, platform versions in use, product lifecycle
> state, assignments, approvals, policy text, exception records, classification
> and both criticality fields, domain membership.

Therefore:

* **A1 — Identifiers are stable and are never reused.** Section 63.1: "The system
  refuses to delete departed people and refuses to reuse identifiers." Section 7
  marks the person `id` "stable identifier, never reused". A validator enforces
  this; see `validators/registry/check-append-only.sh`.
* **A2 — A state change closes the old interval and opens a new one.** Set the
  old entry's `end_date`; add a new entry. Never edit a field of a closed
  interval in place.
* **A3 — Departure is a state, not a deletion.** Section 7.1: "A departed
  person's record is retained with `availability: departed` and
  `access_status: revoked` so that historical evidence — who approved what, who
  reviewed what — remains interpretable. Their identifier is never reused."
* **A4 — Corrections are follow-up entries, never in-place rewrites.** Section
  97.2 states this for records — "never edits in place (corrections are
  follow-up records)" — and Section 63.1 generalises the principle to "every
  operating-system record".
* **A5 — Git history is the audit trail.** No separate audit file, no changelog
  registry, no "history" block inside a registry file. Section 63.1 is explicit
  that git plus GitHub's audit log plus the deployment records already carry it.
* **A6 — No shared mutable index.** One entry per item; period and portfolio
  views are derived by aggregation, never by appending to a shared list file.
  Section 97.3 states the rule for events — "written as its own file, one file
  per event, never a concurrent append to a shared period file" — and it is why
  parallel work in this repository never contends for the same file.

## 3. Version fields

Section 60.2 fixes the version field per contract. The three this lane seeds in
Phase 1:

| Contract | File | Version field |
| --- | --- | --- |
| People Registry | `registries/people.yaml` | `registry_version` |
| Role Registry | `registries/roles.yaml` | `registry_version` |
| Event-type enum and platform record | `registries/platform.yaml` | `platform_version` |

* **V1 — A schema change writes v2 alongside v1; it never replaces v1.**
  Section 60.2: "Write the v2 schema alongside v1 — do not replace"; the
  validator supports both; v1 support is removed only after every consumer has
  migrated.
* **V2 — Simultaneous fleet migration is never required** (Section 60.2).

## 4. The telemetry carve-out

Section 63.1 and Section 97.6: append-only permanence applies to state,
decisions, approvals and records. Raw activity telemetry may be aggregated or
discarded after its declared diagnostic window, and retention classes are
declared in the control plane and owned by the Founder. Nothing in
`registries/**` is telemetry, so the carve-out never applies to a file this lane
owns.

## 5. What this file does NOT govern

* `records/**` and `events/**` live in the **`control-plane-records`** repository,
  not here (Section 52.6 row for `records/`/`events/`; Section 40.1, D89). Their
  envelopes carry `record_schema_version` and `event_schema_version`
  (Section 97.2, 97.3) and are owned by Lane 4.
* Layer B stores and the conduct-records store are never in any org-readable
  repository (Section 52.6, Section 90).
EOF

git add schemas/registry/CONVENTIONS.md
git commit -m "$(cat <<'EOF'
docs(l1): registry effective-dating and append-only conventions

The day-one discipline of Section 99.4 item 1 — effective dating and
append-only from the start, because retrofitting history is impossible
by definition. Mechanism transcribed from Section 63.1 (start_date /
end_date, git as the durable record), rules from Sections 7.1, 60.2,
97.1, 97.2, 97.3, 97.6 and invariant 101.7 #47.

Refs: spec Sections 7.1, 60.2, 63.1, 97, 99.4, 101.7 #47
Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
git push origin lane/1/01-repo-skeleton
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
| --- | --- | --- | --- |
| 1 | File exists and is tracked | `git ls-files schemas/registry/CONVENTIONS.md` | `schemas/registry/CONVENTIONS.md` |
| 2 | All six append-only rules present | `grep -c '^\* \*\*A[1-6] ' schemas/registry/CONVENTIONS.md` | `6` |
| 3 | All five dating rules present | `grep -c '^\* \*\*C[1-5] ' schemas/registry/CONVENTIONS.md` | `5` |
| 4 | Both version rules present | `grep -c '^\* \*\*V[1-2] ' schemas/registry/CONVENTIONS.md` | `2` |
| 5 | No forbidden date synonym is used as a field | `grep -cE '^[[:space:]]*(valid_from|effective_from|since):' schemas/registry/CONVENTIONS.md` | `0` |
| 6 | Section 99.4 quote present verbatim | `grep -c 'retrofitting history is impossible' schemas/registry/CONVENTIONS.md` | `3` |
| 7 | Records/events correctly disclaimed | `grep -c 'control-plane-records' schemas/registry/CONVENTIONS.md` | `1` |

### SELF-VERIFY

```bash
cd "$CP_ROOT"
A=$(grep -c '^\* \*\*A[1-6] ' schemas/registry/CONVENTIONS.md)
C=$(grep -c '^\* \*\*C[1-5] ' schemas/registry/CONVENTIONS.md)
V=$(grep -c '^\* \*\*V[1-2] ' schemas/registry/CONVENTIONS.md)
R=$(grep -c 'control-plane-records' schemas/registry/CONVENTIONS.md)
[ "$A" = "6" ] && [ "$C" = "5" ] && [ "$V" = "2" ] && [ "$R" = "1" ] \
  && echo "T05 PASS" || echo "T05 FAIL A=$A C=$C V=$V R=$R"
```

**Correct output:** the single line `T05 PASS`.

### STOP rule

Do not add, remove, reword or reorder any rule in this file. Every rule is a transcription of a cited spec line; changing one is a spec change, and a spec change is a Contract Change Request to L0 (PARTITION.md rule 2), never a lane edit. If a rule appears to contradict another lane's artifact, file the §0.6 blocker with `<TASKID>` = `T05`, `<BLOCKED_ON key>` = `convention-conflicts-with-contract`, quoting both texts.

---

## L1-01-06 — Shared effective-dating and envelope JSON Schemas <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Size:** M **Depends on:** T05
**Creates/edits:**
```
schemas/registry/common/effective-dating.schema.json
schemas/registry/common/registry-envelope.schema.json
```

### Commands

```bash
set -euo pipefail
cd "$CP_ROOT"

cat > schemas/registry/common/effective-dating.schema.json <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  # NEEDS_URN (FD-050): replace with urn:multiproduct:schemas:<type>:<version>
  "$id": "https://control-plane.invalid/schemas/registry/common/effective-dating.schema.json",
  "title": "Effective-dating primitives",
  "description": "Shared $defs for every control-plane registry. Mechanism per spec Section 63.1: state transitions with start_date and end_date, effective-dating, never in-place mutation. Rules C1-C5 and A1-A6 of schemas/registry/CONVENTIONS.md.",
  "$defs": {
    "date": {
      "title": "ISO-8601 calendar date",
      "type": "string",
      "pattern": "^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$"
    },
    "utcTimestamp": {
      "title": "UTC timestamp with explicit offset (Section 97.1)",
      "type": "string",
      "pattern": "^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]+)?(Z|[+-]([01][0-9]|2[0-3]):[0-5][0-9])$"
    },
    "stableId": {
      "title": "Stable identifier, never reused (Sections 7, 63.1; rule A1)",
      "type": "string",
      "pattern": "^[a-z0-9]([a-z0-9-]*[a-z0-9])?$",
      "minLength": 2,
      "maxLength": 64
    },
    "ianaTimezone": {
      "title": "IANA timezone identifier, never a UTC offset (Section 7.3; rule C5)",
      "type": "string",
      "pattern": "^[A-Za-z][A-Za-z0-9_+-]*(/[A-Za-z0-9_+-]+)+$"
    },
    "effectiveInterval": {
      "title": "An effective-dated interval",
      "description": "end_date is always present; null means open-ended (rule C2). Non-employees must carry a non-null end_date (rule C3, Section 7.1).",
      "type": "object",
      "properties": {
        "start_date": { "$ref": "#/$defs/date" },
        "end_date": {
          "anyOf": [
            { "$ref": "#/$defs/date" },
            { "type": "null" }
          ]
        }
      },
      "required": ["start_date", "end_date"]
    }
  }
}
EOF

cat > schemas/registry/common/registry-envelope.schema.json <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  # NEEDS_URN (FD-050): replace with urn:multiproduct:schemas:<type>:<version>
  "$id": "https://control-plane.invalid/schemas/registry/common/registry-envelope.schema.json",
  "title": "Control-plane registry envelopes",
  "description": "Version-field envelopes per spec Section 60.2. People Registry and Role Registry carry registry_version; platform.yaml carries platform_version.",
  "$defs": {
    "registryEnvelope": {
      "title": "registry_version envelope (Section 60.2)",
      "type": "object",
      "properties": {
        "registry_version": { "type": "integer", "minimum": 1 }
      },
      "required": ["registry_version"]
    },
    "platformEnvelope": {
      "title": "platform_version envelope (Sections 60.1, 60.2)",
      "type": "object",
      "properties": {
        "platform_version": { "type": ["number", "string"] }
      },
      "required": ["platform_version"]
    }
  }
}
EOF

git add schemas/registry/common/effective-dating.schema.json \
        schemas/registry/common/registry-envelope.schema.json
git commit -m "$(cat <<'EOF'
feat(l1): shared effective-dating and registry-envelope schemas

$defs for start_date/end_date intervals, stable never-reused ids, UTC
timestamps with offset and IANA timezones, plus the registry_version /
platform_version envelopes of Section 60.2. These are the primitives
every registry schema in this lane references, so effective dating exists
from the first schema rather than being retrofitted (Section 99.4 item 1).

Refs: spec Sections 7, 7.3, 60.1, 60.2, 63.1, 97.1, 99.4
Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
git push origin lane/1/01-repo-skeleton
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
| --- | --- | --- | --- |
| 1 | Both files are valid JSON | `jq -e . schemas/registry/common/effective-dating.schema.json >/dev/null && jq -e . schemas/registry/common/registry-envelope.schema.json >/dev/null; echo $?` | `0` |
| 2 | Five `$defs` in the dating schema | `jq -r '.["$defs"] \| keys \| length' schemas/registry/common/effective-dating.schema.json` | `5` |
| 3 | Interval requires both fields | `jq -r '.["$defs"].effectiveInterval.required \| join(",")' schemas/registry/common/effective-dating.schema.json` | `start_date,end_date` |
| 4 | Two `$defs` in the envelope schema | `jq -r '.["$defs"] \| keys \| join(",")' schemas/registry/common/registry-envelope.schema.json` | `platformEnvelope,registryEnvelope` |
| 5 | Dating pattern accepts a real date | `python3 -c "import re,json;p=json.load(open('schemas/registry/common/effective-dating.schema.json'))['\$defs']['date']['pattern'];print(bool(re.match(p,'2026-08-27')))"` | `True` |
| 6 | Dating pattern rejects a bad date | `python3 -c "import re,json;p=json.load(open('schemas/registry/common/effective-dating.schema.json'))['\$defs']['date']['pattern'];print(bool(re.match(p,'2026-8-27')))"` | `False` |

### SELF-VERIFY

```bash
cd "$CP_ROOT"
jq -e . schemas/registry/common/effective-dating.schema.json >/dev/null || echo "BAD JSON 1"
jq -e . schemas/registry/common/registry-envelope.schema.json >/dev/null || echo "BAD JSON 2"
D=$(jq -r '.["$defs"] | keys | length' schemas/registry/common/effective-dating.schema.json)
E=$(jq -r '.["$defs"] | keys | join(",")' schemas/registry/common/registry-envelope.schema.json)
R=$(jq -r '.["$defs"].effectiveInterval.required | join(",")' schemas/registry/common/effective-dating.schema.json)
[ "$D" = "5" ] && [ "$E" = "platformEnvelope,registryEnvelope" ] && [ "$R" = "start_date,end_date" ] \
  && echo "T06 PASS" || echo "T06 FAIL D=$D E=$E R=$R"
```

**Correct output:** the single line `T06 PASS`.

### STOP rule

Do not add a `format: date` keyword in place of the pattern, do not add extra `$defs`, and do not rename `start_date`/`end_date` (rule C1). Do not create any schema under `schemas/records/**` — that path belongs to Lane 4 (PARTITION.md, L4 row). If a task issue asks you to, file the §0.6 blocker with `<TASKID>` = `T06`, `<BLOCKED_ON key>` = `foreign-lane-path-requested`.

---

## L1-01-07 — `registries/INVENTORY.md`: the §52.6 registry-of-files, transcribed <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Size:** M **Depends on:** T03
**Creates/edits:** `registries/INVENTORY.md`

§52.6: "Every control-plane artifact is listed here with its owner and purpose… This table is the complete inventory — twenty-nine entries. Any proposal for a new control-plane artifact must state which existing file cannot hold the content; if an existing file can hold it, the proposal is rejected."

The transcription is **mechanical**: the table body is spec lines **4619–4647** inclusive. Do not retype it, do not reorder it, do not summarise it.

### Commands

```bash
set -euo pipefail
cd "$CP_ROOT"

# Header, written by hand.
cat > registries/INVENTORY.md <<'EOF'
# Registry of control-plane files — the closed inventory

**Source:** spec Section 52.6, "Registry of control-plane files", table body at
spec lines 4619-4647 inclusive. Transcribed verbatim by
`make registry-inventory-check`; never hand-edited.

**Binding rule, Section 52.6:** "This table is the complete inventory — twenty-nine
entries. Any proposal for a new control-plane artifact must state which existing
file cannot hold the content; if an existing file can hold it, the proposal is
rejected."

**Scope note, Section 52.6:** the inventory spans both control-plane repositories
— this repository and the `control-plane-records` repository (Section 40.1, D89).
The `records/`, `events/` and Leave-records rows belong to `control-plane-records`
and are owned by Lane 4; the Layer B stores and the conduct-records store are
never in any org-readable repository.

**Path mapping:** Section 52.6 names artifacts by filename and states no directory.
In this repository the artifacts this lane owns live at `registries/<name>.yaml`
per the path-ownership contract in PARTITION.md. The filenames below are the
Section 52.6 names, unchanged.

**Transcription note:** the table below has **29 markdown rows**, matching the
"twenty-nine entries" the section states. Spec line 4644 carries **two** artifacts
in one markdown row — the conduct-records store and `templates/` — because the
row separator is absent in the source. The row is transcribed exactly as it
appears; it is not split, because splitting it would change the stated count.

---

EOF

# Table body, extracted from the spec by line range. Header rows first.
sed -n '4617,4618p' "$SPEC" >> registries/INVENTORY.md
sed -n '4619,4647p' "$SPEC" >> registries/INVENTORY.md

# Record the provenance so a later spec revision is detectable.
{
  echo ""
  echo "---"
  echo ""
  echo "## Provenance"
  echo ""
  echo "| Field | Value |"
  echo "| --- | --- |"
  echo "| Spec file | \`MultiProduct_MasterSpec_v4.0.md\` |"
  echo "| Spec section | 52.6 |"
  echo "| Table body lines | 4619-4647 (29 rows) |"
  echo "| Table body sha256 | \`$(sed -n '4619,4647p' "$SPEC" | sha256sum | cut -d' ' -f1)\` |"
} >> registries/INVENTORY.md

git add registries/INVENTORY.md
git commit -m "$(cat <<'EOF'
docs(l1): transcribe the Section 52.6 control-plane file inventory

The closed twenty-nine-entry registry of control-plane files, extracted
verbatim from spec lines 4619-4647 with a sha256 provenance stamp so a
later spec revision is detectable rather than silently divergent. Records
the split of the inventory across the control-plane and
control-plane-records repositories (Section 40.1, D89).

Refs: spec Sections 40.1, 52.6, D89
Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
git push origin lane/1/01-repo-skeleton
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
| --- | --- | --- | --- |
| 1 | File tracked | `git ls-files registries/INVENTORY.md` | `registries/INVENTORY.md` |
| 2 | Exactly 29 body rows | `awk '/^\| --- \| --- \| --- \|$/{f=1;next} f&&/^\|/{c++} f&&!/^\|/{exit} END{print c}' registries/INVENTORY.md` | `29` |
| 3 | Body matches the spec byte-for-byte | see SELF-VERIFY | `MATCH` |
| 4 | `people.yaml` row present | `grep -c '^| `people.yaml` | Founder |' registries/INVENTORY.md` | `1` |
| 5 | `platform.yaml` row present | `grep -c '^| `platform.yaml` | Team Lead |' registries/INVENTORY.md` | `1` |
| 6 | Provenance hash recorded | `grep -c 'Table body sha256' registries/INVENTORY.md` | `1` |
| 7 | No invented row | `grep -c 'TBD\|TODO\|placeholder' registries/INVENTORY.md` | `0` |

### SELF-VERIFY

```bash
cd "$CP_ROOT"
ROWS=$(awk '/^\| --- \| --- \| --- \|$/{f=1;next} f&&/^\|/{c++} f&&!/^\|/{exit} END{print c+0}' registries/INVENTORY.md)
SPEC_SHA=$(sed -n '4619,4647p' "$SPEC" | sha256sum | cut -d' ' -f1)
FILE_SHA=$(awk '/^\| --- \| --- \| --- \|$/{f=1;next} f&&/^\|/{print} f&&!/^\|/{exit}' registries/INVENTORY.md | sha256sum | cut -d' ' -f1)
[ "$SPEC_SHA" = "$FILE_SHA" ] && M=MATCH || M=DIFFER
STAMP=$(grep -c 'Table body sha256' registries/INVENTORY.md)
[ "$ROWS" = "29" ] && [ "$M" = "MATCH" ] && [ "$STAMP" = "1" ] \
  && echo "T07 PASS" || echo "T07 FAIL ROWS=$ROWS M=$M STAMP=$STAMP"
```

**Correct output:** the single line `T07 PASS`.

### STOP rule

Do not proceed if `ROWS` is anything other than `29`, or if `M=DIFFER`. Either means the spec at those line numbers is not the §52.6 table — the spec file has been revised, or `$SPEC` points at a different version. **Do not adjust the line numbers to make it fit, and do not hand-write the table.** File the §0.6 blocker with `<TASKID>` = `T07`, `<BLOCKED_ON key>` = `spec-line-range-drift`, including the output of:

```bash
sed -n '4613,4618p' "$SPEC"
grep -n '^### 52.6 Registry of control-plane files' "$SPEC"
```

---

## L1-01-08 — Seed `registries/roles.yaml` (verbatim from §8) <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Size:** M **Depends on:** T06
**Creates/edits:** `registries/roles.yaml`

§98.2 Phase 1 requires `roles.yaml` in Week 1. §8 gives the eleven role entries in full, so this seed is a transcription, not a design. §8 also states the constraint that CI will later enforce (D106): a role default must never contain a dangerous capability.

### Commands

```bash
set -euo pipefail
cd "$CP_ROOT"
cat > registries/roles.yaml <<'EOF'
# roles.yaml — control-plane repository
# Transcribed verbatim from spec Section 8 (Role Registry), Priority P0.
#
# Section 8: "Roles are configuration. New roles are added without workflow
# redesign because every authority decision is made against capability, never
# against role name."
#
# D106 / Section 8: no role default carries a dangerous capability. The
# explicit-grant-only set is production-approval, platform-change-approval,
# platform-admin, security-review, migration-review, exceptional-approval,
# lifecycle-decision, people-intelligence. Control-plane CI rejects a
# roles.yaml default containing any of them (enforced in phase L1-02).
#
# Effective dating and append-only: schemas/registry/CONVENTIONS.md.
# Version field per Section 60.2: registry_version.

registry_version: 1

roles:
  - id: founder
    default_capabilities: [strategy, budget, hiring, lifecycle-decision,
                           customer-commitment, exceptional-approval,
                           people-intelligence]
  - id: team_lead
    default_capabilities: [architecture, plan-approval, escalation,
                           reviewer-matrix-change]
                                    # production-approval and
                                    # platform-change-approval are granted
                                    # explicitly, never by default — see 8.1
  - id: acting_team_lead
    default_capabilities: [architecture, plan-approval, escalation,
                           reviewer-matrix-change]
                                    # dormant until activation (Section 13.1);
                                    # production-approval granted explicitly
                                    # for the recorded activation period
  - id: developer
    default_capabilities: [code-review]
  - id: mobile_developer
    default_capabilities: [code-review, mobile-release]
  - id: senior_developer
    default_capabilities: [code-review, architecture]
  - id: qa
    default_capabilities: [verification, uat, release-signoff]
  - id: devops
    default_capabilities: [devops, code-review]
  - id: foundational_developer
    default_capabilities: [code-review]
  - id: specialist
    default_capabilities: []        # granted explicitly, never by default
  - id: contractor
    default_capabilities: []        # granted explicitly, never by default
EOF

python3 - <<'PY'
import yaml
d = yaml.safe_load(open('registries/roles.yaml'))
assert d['registry_version'] == 1, d['registry_version']
ids = [r['id'] for r in d['roles']]
assert len(ids) == 11, ids
assert len(set(ids)) == 11, "duplicate role id"
DANGEROUS = {"production-approval","platform-change-approval","platform-admin",
             "security-review","migration-review","exceptional-approval",
             "lifecycle-decision","people-intelligence"}
for r in d['roles']:
    bad = DANGEROUS & set(r.get('default_capabilities') or [])
    if r['id'] != 'founder' and bad:
        raise SystemExit("D106 violation in role %s: %s" % (r['id'], sorted(bad)))
print("ROLES_OK", len(ids))
PY

git add registries/roles.yaml
git commit -m "$(cat <<'EOF'
feat(l1): seed registries/roles.yaml from spec Section 8

The eleven-role registry required by Section 98.2 Phase 1, transcribed
verbatim from Section 8 including the explicit-grant notes for
production-approval and platform-change-approval. registry_version: 1 per
Section 60.2.

Refs: spec Sections 8, 60.2, 98.2, D106
Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
git push origin lane/1/01-repo-skeleton
```

> **Note on the `founder` row.** §8's own listing gives `founder` the defaults
> `lifecycle-decision`, `exceptional-approval` and `people-intelligence`, which
> appear in D106's dangerous set. The transcription above preserves §8 exactly and
> the check exempts `founder` for that reason. Do not "fix" this. It is flagged to
> L0 in the DECISION REQUIRED block below.

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
| --- | --- | --- | --- |
| 1 | Parses as YAML | `python3 -c "import yaml;yaml.safe_load(open('registries/roles.yaml'))"; echo $?` | `0` |
| 2 | Eleven roles | `python3 -c "import yaml;print(len(yaml.safe_load(open('registries/roles.yaml'))['roles']))"` | `11` |
| 3 | `registry_version` is 1 | `python3 -c "import yaml;print(yaml.safe_load(open('registries/roles.yaml'))['registry_version'])"` | `1` |
| 4 | Role ids unique | `python3 -c "import yaml;r=[x['id'] for x in yaml.safe_load(open('registries/roles.yaml'))['roles']];print(len(r)==len(set(r)))"` | `True` |
| 5 | No non-founder role holds a dangerous default | the D106 check inside the block above | `ROLES_OK 11` |
| 6 | Exact id set matches §8 | see SELF-VERIFY | `IDS_OK` |

### SELF-VERIFY

```bash
cd "$CP_ROOT"
python3 - <<'PY'
import yaml
d = yaml.safe_load(open('registries/roles.yaml'))
expected = ['founder','team_lead','acting_team_lead','developer','mobile_developer',
            'senior_developer','qa','devops','foundational_developer','specialist','contractor']
got = [r['id'] for r in d['roles']]
print("IDS_OK" if got == expected else "IDS_FAIL %s" % got)
print("T08 PASS" if (got == expected and d['registry_version'] == 1) else "T08 FAIL")
PY
```

**Correct output:** exactly two lines, `IDS_OK` then `T08 PASS`.

### STOP rule

Do not add a role, remove a role, or change any `default_capabilities` list. The roster of *people* is not this file and is not this task. If the task issue supplies a role not in §8, file the §0.6 blocker with `<TASKID>` = `T08`, `<BLOCKED_ON key>` = `role-not-in-spec-section-8`.

> **DECISION REQUIRED — L0**
> **Subject:** the `founder` role's `default_capabilities` contains three members of the D106 dangerous set (`lifecycle-decision`, `exceptional-approval`, `people-intelligence`).
> **Why L1 cannot decide it:** §8's role listing and D106's blanket rule ("Control-plane CI rejects a `roles.yaml` default containing any of them") are in tension for exactly this one row. Resolving it changes what the Phase-2 validator rejects.
> **What L0 must decide, exactly:** either (a) the D106 CI check exempts `founder`, or (b) `registries/roles.yaml` drops those three from the `founder` default and they are granted per-person in `registries/people.yaml`.
> **Where the answer must land:** a frozen entry under `contracts/**`, consumed by phase L1-02's validator.
> **Blocking:** phase L1-02's D106 check. **Not** blocking T08 — the transcription above is correct either way.

---

## L1-01-09 — Seed `registries/people.yaml` (empty, schema-valid) <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Size:** S **Depends on:** T06
**Creates/edits:** `registries/people.yaml`

§98.2 Phase 1 requires `people.yaml` to be authored in Week 1. Its **content** — the actual roster, capabilities and access states — is Founder-owned (§52.6 owner column: Founder) and is a registry-lane edit under §26.4, not a build-lane artifact. This task seeds the **file and its envelope only**, with an empty `people` list, so that the schema, the validator and the append-only guard have something real to run against from day one.

### Commands

```bash
set -euo pipefail
cd "$CP_ROOT"
cat > registries/people.yaml <<'EOF'
# people.yaml — control-plane repository
# Section 7 (People Registry), Priority P0. Owner: Founder (Section 52.6).
#
# Section 7: "A single declarative file in the control-plane repository,
# version-controlled and CI-validated. Not an HR system - an operational
# identity and capability registry."
#
# This file is seeded EMPTY by the build lane. Person entries are authored by
# the Founder through the registry-change lane of Section 26.4 — CI schema
# validation, plus review by the file's declared owner, plus the linked
# decision record where one is required. A build lane never authors a person.
#
# Binding rules that apply from the first entry onward:
#   - id is a stable identifier and is NEVER reused (Sections 7, 63.1; rule A1)
#   - end_date is mandatory and non-null for every non-employee (Section 7.1)
#   - departure is a state, not a deletion: availability: departed with
#     access_status: revoked, record retained (Section 7.1; rule A3)
#   - new people enter at minimum authority; capabilities are granted
#     individually and explicitly, never inherited from a role default
#     (Sections 7.1, 8, 64.1, D106)
#   - work_arrangement.timezone is an IANA identifier, never a UTC offset
#     (Section 7.3; rule C5)
#
# Effective dating and append-only: schemas/registry/CONVENTIONS.md.
# Version field per Section 60.2: registry_version.

registry_version: 1

people: []
EOF

python3 - <<'PY'
import yaml
d = yaml.safe_load(open('registries/people.yaml'))
assert d['registry_version'] == 1, d
assert d['people'] == [], d
print("PEOPLE_SEED_OK")
PY

git add registries/people.yaml
git commit -m "$(cat <<'EOF'
feat(l1): seed registries/people.yaml envelope (empty roster)

Section 98.2 Phase 1 requires people.yaml in Week 1. The envelope is
seeded here so schemas, validators and the append-only guard have a real
file from day one; the roster itself is Founder-owned (Section 52.6) and
is authored through the registry-change lane of Section 26.4, never by a
build lane.

Refs: spec Sections 7, 7.1, 7.3, 26.4, 52.6, 60.2, 98.2
Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
git push origin lane/1/01-repo-skeleton
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
| --- | --- | --- | --- |
| 1 | Parses as YAML | `python3 -c "import yaml;yaml.safe_load(open('registries/people.yaml'))"; echo $?` | `0` |
| 2 | `registry_version` is 1 | `python3 -c "import yaml;print(yaml.safe_load(open('registries/people.yaml'))['registry_version'])"` | `1` |
| 3 | Roster is empty | `python3 -c "import yaml;print(yaml.safe_load(open('registries/people.yaml'))['people'])"` | `[]` |
| 4 | No invented person | `grep -cE '^[[:space:]]*- id:' registries/people.yaml` | `0` |
| 5 | No real name or login present | `grep -cE 'github_login:|display_name:' registries/people.yaml` | `0` |

### SELF-VERIFY

```bash
cd "$CP_ROOT"
python3 - <<'PY'
import yaml
d = yaml.safe_load(open('registries/people.yaml'))
ok = (d.get('registry_version') == 1 and d.get('people') == [])
print("T09 PASS" if ok else "T09 FAIL %r" % d)
PY
```

**Correct output:** the single line `T09 PASS`.

### STOP rule

**Do not add a person to this file.** Not a placeholder, not an example, not yourself, not the names that appear in spec §78. §78.1 states those snapshots are configuration captured from their source, never inferred from the spec document. A person entry created by a build lane is an unreviewed authority grant (§26.4: "an **authority delta** — a diff that adds a capability, adds an assignment type conferring Write, or changes `access_status` — fails CI without a linked decision record ID in the same commit").

If the task issue instructs you to populate the roster, file the §0.6 blocker with `<TASKID>` = `T09`, `<BLOCKED_ON key>` = `roster-authoring-is-not-a-build-lane-action`.

> **DECISION REQUIRED — L0**
> **Subject:** who authors the initial `registries/people.yaml` roster, and when.
> **Why L1 cannot decide it:** §52.6 names the Founder as owner; §26.4 routes registry edits through owner review plus a linked decision record for any authority delta. Neither is a build-lane action.
> **What L0 must arrange, exactly:** a Founder-authored roster PR on the registry-change lane after this phase merges, carrying the decision-record ID in the same commit.
> **Blocking:** nothing in phase L1-01. Blocks the §98.2 Phase 1 completion check ("Teams granting Write exist before branch protection is armed"), which is L5's dependency, not L1's.

---

## L1-01-10 — Seed `registries/platform.yaml` <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Size:** M **Depends on:** T06
**Creates/edits:** `registries/platform.yaml`

§98.2 Phase 1 requires `platform.yaml` in Week 1. §60.1 gives the file's shape. §52.6's `platform.yaml` row and §97.3 add the closed `event_type` enum: "The enum is declared in `platform.yaml` beside the supported contract versions… and the enum ships populated in Phase 1 so no workflow ever writes an untyped event."

Two parts of this file are **not** transcribable and are therefore read from L0's frozen contracts rather than invented here:

* `canary_set` — §60.1 marks it "configurable, reviewed quarterly"; §61.3 governs its selection. It is a choice about real products.
* `event_types` — §97.3 states the identifiers are "lower-case, underscore-separated, never renamed once shipped" and gives exactly one worked identifier (`plan_approved`); the taxonomy itself is prose. Turning prose into a closed, never-renamable enum is naming, and naming is a decision.

### Commands

```bash
set -euo pipefail
cd "$CP_ROOT"

# Step 1: require L0's frozen inputs. Both paths are L0-owned (contracts/**).
# RETIRED: event-types.txt cannot carry `retired` field (§97.3 requires it). Use the YAML contract instead.
test -f contracts/event-types.txt || { echo "MISSING contracts/event-types.txt"; }
test -f contracts/canary-set.txt  || { echo "MISSING contracts/canary-set.txt"; }
```

**If either file is missing, execute the STOP rule now. Do not continue.**

```bash
set -euo pipefail
# Step 2: build the file with the frozen enum and canary set spliced in.
{
cat <<'EOF'
# platform.yaml — control-plane repository
# Sections 60.1 (the platform record) and 97.3 (the closed event_type enum).
# Owner: Team Lead (Section 52.6).
#
# Section 60.1: "The platform carries a version, a changelog, a compatibility
# statement, a migration process, a rollout process and a rollback process —
# exactly as a product does."
#
# Section 97.3: the event_type enum "is declared in platform.yaml beside the
# supported contract versions, because it migrates exactly as a contract schema
# does (Section 60.2); control-plane CI rejects any event whose event_type is
# absent from it, and the enum ships populated in Phase 1 so no workflow ever
# writes an untyped event." Retiring an identifier marks it retired and never
# removes it, because the events that carry it are append-only.
#
# Effective dating and append-only: schemas/registry/CONVENTIONS.md.
# Version field per Section 60.2: platform_version.

platform_version: 4.0

supported_contract_versions:
  product: [1]
  verification: [1]
  people_registry: [1]
  service: [1]

reusable_workflow_versions:
  current: v1
  supported: [v1]
  deprecated: []
  deprecation_deadline: {}

canary_set:                      # configurable, reviewed quarterly (Section 60.1)
                                 # selection criteria: Section 61.3
                                 # frozen source: contracts/canary-set.txt
EOF
sed -e 's/^/  - /' contracts/canary-set.txt
cat <<'EOF'

event_types:                     # the closed enum of Section 97.3
                                 # lower-case, underscore-separated
                                 # never renamed once shipped; retired, never removed
                                 # RETIRED: event-types.txt cannot carry `retired` field (§97.3 requires it). Use the YAML contract instead.
EOF
# RETIRED: event-types.txt cannot carry `retired` field (§97.3 requires it). Use the YAML contract instead.
sed -e 's/^/  - /' contracts/event-types.txt
cat <<'EOF'

EOF
} > registries/platform.yaml

python3 - <<'PY'
import re, yaml
d = yaml.safe_load(open('registries/platform.yaml'))
assert d['platform_version'] == 4.0, d['platform_version']
for k in ('supported_contract_versions','reusable_workflow_versions','canary_set',
          'event_types','retired_event_types'):
    assert k in d, "missing key %s" % k
ets = d['event_types'] or []
assert len(ets) == len(set(ets)), "duplicate event_type"
pat = re.compile(r'^[a-z][a-z0-9]*(_[a-z0-9]+)*$')
bad = [e for e in ets if not pat.match(e)]
assert not bad, "event_type not lower_snake_case: %s" % bad
assert 'plan_approved' in ets, "spec Section 97.3 names plan_approved; it is absent"
print("PLATFORM_OK events=%d canary=%d" % (len(ets), len(d['canary_set'] or [])))
PY

git add registries/platform.yaml
git commit -m "$(cat <<'EOF'
feat(l1): seed registries/platform.yaml with the closed event_type enum

The platform record of Section 60.1 plus the closed event_type enum of
Section 97.3, which must ship populated in Phase 1 so no workflow ever
writes an untyped event. The enum and the canary set are spliced from
L0's frozen contracts/ inputs, never authored here: both are decisions,
not transcriptions. retired_event_types exists from day one because
retiring an identifier marks it retired and never removes it.

Refs: spec Sections 52.6, 60.1, 60.2, 61.3, 97.3, 98.2
Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
git push origin lane/1/01-repo-skeleton
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
| --- | --- | --- | --- |
| 1 | Parses as YAML | `python3 -c "import yaml;yaml.safe_load(open('registries/platform.yaml'))"; echo $?` | `0` |
| 2 | `platform_version` present | `python3 -c "import yaml;print(yaml.safe_load(open('registries/platform.yaml'))['platform_version'])"` | `4.0` |
| 3 | All five top-level keys present | the assert loop in the block above | no traceback |
| 4 | Enum is populated | `python3 -c "import yaml;print(len(yaml.safe_load(open('registries/platform.yaml'))['event_types'])>0)"` | `True` |
| 5 | Enum identifiers are lower_snake_case | the regex check above | no traceback |
| 6 | Enum has no duplicates | the set check above | no traceback |
| 7 | `plan_approved` present (§97.3 worked example) | `python3 -c "import yaml;print('plan_approved' in yaml.safe_load(open('registries/platform.yaml'))['event_types'])"` | `True` |
| 8 | `retired_event_types` exists and is empty | `python3 -c "import yaml;print(yaml.safe_load(open('registries/platform.yaml'))['retired_event_types'])"` | `[]` |

### SELF-VERIFY

```bash
cd "$CP_ROOT"
python3 - <<'PY'
import re, yaml
d = yaml.safe_load(open('registries/platform.yaml'))
ets = d.get('event_types') or []
pat = re.compile(r'^[a-z][a-z0-9]*(_[a-z0-9]+)*$')
ok = (d.get('platform_version') == 4.0
      and len(ets) > 0
      and len(ets) == len(set(ets))
      and all(pat.match(e) for e in ets)
      and 'plan_approved' in ets
      and d.get('retired_event_types') == []
      and 'canary_set' in d)
print("T10 PASS events=%d" % len(ets) if ok else "T10 FAIL %r" % {k: d.get(k) for k in
      ('platform_version','retired_event_types')})
PY
```

**Correct output:** one line beginning `T10 PASS events=` followed by a positive integer.

### STOP rule

Do not proceed if `contracts/event-types.txt` or `contracts/canary-set.txt` is missing, empty, or contains an identifier that fails the lower_snake_case regex. **RETIRED: event-types.txt cannot carry `retired` field (§97.3 requires it). Use the YAML contract instead.** **Do not derive the enum from the §97.3 prose yourself, and do not choose canary products.** An enum identifier is "never renamed once shipped" (§97.3) — a wrong guess is permanent and splits every metric derived from it.

File the §0.6 blocker with `<TASKID>` = `T10` and `<BLOCKED_ON key>` = one of `contracts-event-types-missing`, `contracts-canary-set-missing`, `event-type-identifier-malformed`.

> **DECISION REQUIRED — L0**
> **Subject:** the closed `event_type` enum and the initial `canary_set`.
> **Why L1 cannot decide it:** §97.3 requires the enum to ship populated in Phase 1 and states its identifiers are "never renamed once shipped", but gives the taxonomy as prose and only one worked identifier (`plan_approved`). Converting the ~110 prose event names of the §97.3 tracked-events paragraph into stable identifiers is naming. §60.1 marks `canary_set` "configurable, reviewed quarterly"; §61.3 gives the selection criteria and §61.5 forbids fleet rollout without a canary — the set names real products.
> **What L0 must supply, exactly:**
> - `contracts/event-types.txt` — one lower-case, underscore-separated identifier per line, no blank lines, no comments, derived one-to-one from the §97.3 tracked-events list, including `plan_approved`. **RETIRED: event-types.txt cannot carry `retired` field (§97.3 requires it). Use the YAML contract instead.**
> - `contracts/canary-set.txt` — one product id per line, chosen against §61.3; an empty-but-present file is acceptable only if L0 records that no canary set exists yet.
> **Blocking:** T10, and therefore T13 and the whole phase.

---

## L1-01-11 — `validators/registry/check-append-only.sh` <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Size:** M **Depends on:** T05
**Creates/edits:** `validators/registry/check-append-only.sh`

Rules A1–A4 of `schemas/registry/CONVENTIONS.md` are worthless unenforced. This is the minimal day-one guard: it fails when a change to `registries/**` deletes a file, removes an `id:` line, or removes a `start_date:` line, relative to the merge base with `integration`. Deeper referential and date validation is phase **L1-02** (subsystem B, §99.2).

### Commands

```bash
set -euo pipefail
cd "$CP_ROOT"
cat > validators/registry/check-append-only.sh <<'SH'
#!/usr/bin/env bash
# check-append-only.sh — day-one append-only guard for registries/**.
#
# Enforces rules A1-A4 of schemas/registry/CONVENTIONS.md, which transcribe
# spec Section 63.1 ("state transitions with start_date and end_date -
# effective-dating, never in-place mutation"), Section 7.1 ("Departure is a
# state, not a deletion... Their identifier is never reused") and invariant
# 101.7 #47 ("History is append-only... state changes are recorded, not
# overwritten").
#
# Scope, deliberately narrow: this guard proves that history was not destroyed.
# It does NOT validate schemas, referential integrity or date rules - that is
# phase L1-02 (subsystem B, Section 99.2).
#
# Usage:  validators/registry/check-append-only.sh [BASE_REF]
# BASE_REF defaults to origin/integration.
# Exit 0 = APPEND_ONLY_OK. Exit 1 = APPEND_ONLY_VIOLATION. Exit 2 = usage error.

set -euo pipefail

BASE_REF="${1:-origin/integration}"

if ! git rev-parse --verify --quiet "$BASE_REF" >/dev/null; then
  echo "APPEND_ONLY_ERROR: base ref not found: $BASE_REF" >&2
  exit 2
fi

BASE="$(git merge-base "$BASE_REF" HEAD)"
VIOLATIONS=0

# --- A3/A5: a registry file is never deleted or renamed away. ---
DELETED="$(git diff --diff-filter=DR --name-only "$BASE" HEAD -- registries/ || true)"
if [ -n "$DELETED" ]; then
  echo "APPEND_ONLY_VIOLATION: registry file deleted or renamed:"
  echo "$DELETED" | sed 's/^/  /'
  VIOLATIONS=$((VIOLATIONS + 1))
fi

# --- A1: an id line is never removed or changed. ---
REMOVED_IDS="$(git diff --unified=0 "$BASE" HEAD -- registries/ \
  | grep -E '^-[^-]' \
  | grep -E '^-[[:space:]]*(-[[:space:]]+)?id:' || true)"
if [ -n "$REMOVED_IDS" ]; then
  echo "APPEND_ONLY_VIOLATION: id removed or rewritten (rule A1, ids are never reused):"
  echo "$REMOVED_IDS" | sed 's/^/  /'
  VIOLATIONS=$((VIOLATIONS + 1))
fi

# --- A2: a start_date is never removed or rewritten; intervals close, never move. ---
REMOVED_STARTS="$(git diff --unified=0 "$BASE" HEAD -- registries/ \
  | grep -E '^-[^-]' \
  | grep -E '^-[[:space:]]*start_date:' || true)"
if [ -n "$REMOVED_STARTS" ]; then
  echo "APPEND_ONLY_VIOLATION: start_date removed or rewritten (rule A2):"
  echo "$REMOVED_STARTS" | sed 's/^/  /'
  VIOLATIONS=$((VIOLATIONS + 1))
fi

if [ "$VIOLATIONS" -gt 0 ]; then
  echo ""
  echo "Corrections are follow-up entries, never in-place rewrites (rule A4,"
  echo "spec Section 97.2). Close the old interval with end_date and add a new entry."
  exit 1
fi

echo "APPEND_ONLY_OK"
exit 0
SH

chmod +x validators/registry/check-append-only.sh
git update-index --chmod=+x validators/registry/check-append-only.sh 2>/dev/null || true

git add validators/registry/check-append-only.sh
git commit -m "$(cat <<'EOF'
feat(l1): day-one append-only guard for registries/**

Fails a change that deletes a registry file, removes an id line, or
removes a start_date line, relative to the merge base with integration.
Enforces rules A1-A4 of the registry conventions, which transcribe
Sections 7.1, 63.1 and 97.2 and invariant 101.7 #47. Schema, referential
and date validation are deliberately out of scope; they are phase L1-02
(subsystem B).

Refs: spec Sections 7.1, 63.1, 97.2, 99.2 (subsystem B), 101.7 #47
Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
git push origin lane/1/01-repo-skeleton
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
| --- | --- | --- | --- |
| 1 | Script is executable in the index | `git ls-files -s validators/registry/check-append-only.sh \| cut -d' ' -f1` | `100755` |
| 2 | Passes on the current clean branch | `validators/registry/check-append-only.sh origin/integration; echo "rc=$?"` | `APPEND_ONLY_OK` then `rc=0` |
| 3 | Detects a removed id (negative test) | see SELF-VERIFY | `NEG_ID_OK` |
| 4 | Detects a deleted registry file (negative test) | see SELF-VERIFY | `NEG_DEL_OK` |
| 5 | Errors cleanly on a bad base ref | `validators/registry/check-append-only.sh no/such/ref; echo "rc=$?"` | a line containing `APPEND_ONLY_ERROR` then `rc=2` |
| 6 | Working tree left clean by the tests | `git status --porcelain \| wc -l` | `0` |

### SELF-VERIFY

```bash
cd "$CP_ROOT"

# Positive case.
validators/registry/check-append-only.sh origin/integration >/dev/null 2>&1 && P=OK || P=FAIL

# Negative case 1: remove an id line from roles.yaml on a scratch commit.
git checkout -b tmp/append-only-negtest >/dev/null 2>&1
grep -v '  - id: contractor' registries/roles.yaml > /tmp/r.yaml && mv /tmp/r.yaml registries/roles.yaml
git commit -aqm "negtest: remove an id"
if validators/registry/check-append-only.sh origin/integration >/dev/null 2>&1; then N1=FAIL; else N1=OK; fi

# Negative case 2: delete a registry file.
git rm -q registries/people.yaml
git commit -qm "negtest: delete a registry file"
if validators/registry/check-append-only.sh origin/integration >/dev/null 2>&1; then N2=FAIL; else N2=OK; fi

# Teardown - the scratch branch is destroyed, never pushed.
git checkout -q lane/1/01-repo-skeleton
git branch -qD tmp/append-only-negtest

[ "$N1" = "OK" ] && echo "NEG_ID_OK"
[ "$N2" = "OK" ] && echo "NEG_DEL_OK"
DIRTY=$(git status --porcelain | wc -l | tr -d ' ')
[ "$P" = "OK" ] && [ "$N1" = "OK" ] && [ "$N2" = "OK" ] && [ "$DIRTY" = "0" ] \
  && echo "T11 PASS" || echo "T11 FAIL P=$P N1=$N1 N2=$N2 DIRTY=$DIRTY"
```

**Correct output:** exactly three lines — `NEG_ID_OK`, `NEG_DEL_OK`, `T11 PASS`.

### STOP rule

Do not push `tmp/append-only-negtest`. Do not widen this script into a schema validator, a referential-integrity checker or a date-rule checker — that scope is phase L1-02 and doing it here makes the two phases collide in the same file. Do not make the script tolerate a violation with a warning; §53 grades responses, and this guard is a **Block**, never a Warn.

If the positive case fails on a clean branch (`P=FAIL`), the merge base is wrong or `origin/integration` is stale. Run `git fetch origin` once and retry. If it still fails, file the §0.6 blocker with `<TASKID>` = `T11`, `<BLOCKED_ON key>` = `append-only-guard-false-positive`, including the full script output.

---

## L1-01-12 — `validators/registry/registry.mk` and the L0 handover packet <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Size:** M **Depends on:** T04, T07, T11
**Creates/edits:**
```
validators/registry/registry.mk
validators/registry/l0-handover/root-gitignore.proposed
validators/registry/l0-handover/root-makefile-include.proposed
validators/registry/l0-handover/codeowners-lane1.proposed
```

**Why a fragment and not the root `Makefile`.** PARTITION.md assigns `Makefile` and `CODEOWNERS` to L0. This lane therefore ships its targets as an includable fragment inside an owned path and hands L0 the one-line include. §33.1 makes the local-environment command set a per-product contract; this fragment is control-plane-side and adds only registry targets.

### Commands

```bash
set -euo pipefail
cd "$CP_ROOT"
mkdir -p validators/registry/l0-handover

cat > validators/registry/registry.mk <<'MK'
# registry.mk — Lane 1 (Registries & Contracts) make targets.
#
# Included by the ROOT Makefile, which is L0-owned under the frozen partition
# contract, with the single line:
#
#     -include validators/registry/registry.mk
#
# Lane 1 owns every target in this file. Phase L1-01 defines exactly four;
# phase L1-02 (subsystem B, Section 99.2) extends the same file and adds
# registry-schema-validate to the registry-verify chain.

REGISTRY_FILES := $(wildcard registries/*.yaml)
BASE_REF ?= origin/integration

.PHONY: registry-lint registry-append-only registry-inventory-check registry-verify

## registry-lint: every file in registries/ parses as YAML.
registry-lint:
	@test -n "$(REGISTRY_FILES)" || { echo "registry-lint: no registries/*.yaml found"; exit 1; }
	@python3 -c "import sys,yaml;[yaml.safe_load(open(f)) for f in sys.argv[1:]];print('REGISTRY_LINT_OK')" $(REGISTRY_FILES)

## registry-append-only: history was not destroyed (Sections 63.1, 97.2, invariant 47).
registry-append-only:
	@validators/registry/check-append-only.sh $(BASE_REF)

## registry-inventory-check: registries/INVENTORY.md still matches spec Section 52.6.
registry-inventory-check:
	@test -f registries/INVENTORY.md || { echo "registry-inventory-check: INVENTORY.md missing"; exit 1; }
	@rows=$$(awk '/^\| --- \| --- \| --- \|$$/{f=1;next} f&&/^\|/{c++} f&&!/^\|/{exit} END{print c+0}' registries/INVENTORY.md); \
	 test "$$rows" = "29" || { echo "registry-inventory-check: expected 29 rows, found $$rows (spec Section 52.6)"; exit 1; }; \
	 grep -q 'Table body sha256' registries/INVENTORY.md || { echo "registry-inventory-check: provenance stamp missing"; exit 1; }; \
	 echo "REGISTRY_INVENTORY_OK"

## registry-verify: the whole lane-1 gate. This is the target CI calls.
registry-verify: registry-lint registry-append-only registry-inventory-check
	@echo "REGISTRY_VERIFY_OK"
MK

cat > validators/registry/l0-handover/root-makefile-include.proposed <<'EOF'
# L0 HANDOVER — root Makefile
# Owner of the target file: L0 Integrator (PARTITION.md, L0 row: root files, Makefile).
# Requested by: Lane 1, phase L1-01, task T12.
#
# Add exactly this line to the root Makefile. Nothing else from Lane 1 goes there.

-include validators/registry/registry.mk

# It provides: registry-lint, registry-append-only, registry-inventory-check,
# registry-verify. Lane 1 extends the same fragment in phase L1-02; the include
# line never changes.
EOF

cat > validators/registry/l0-handover/root-gitignore.proposed <<'EOF'
# L0 HANDOVER — root .gitignore
# Owner of the target file: L0 Integrator (PARTITION.md, L0 row: root files).
# Requested by: Lane 1, phase L1-01, task T12.
#
# Lane 1's own ignore rules already live in registries/.gitignore,
# schemas/registry/.gitignore, schemas/product/.gitignore and
# validators/registry/.gitignore. The lines below are the
# repository-wide rules Lane 1 needs and cannot place itself.

# --- OS and editor noise ---
.DS_Store
Thumbs.db
*~
*.swp
.idea/
.vscode/

# --- Local tool state ---
.venv/
__pycache__/
*.pyc
node_modules/

# --- Secrets: never in the control-plane repository (Sections 36.6, 40.1) ---
# Section 98.2 Phase 1: "Verify env | grep -i api_key returns empty on every
# machine, including shell profiles and repository .env files."
.env
.env.*
*.pem
*.key
*.p12
*.pfx

# --- Derived output: invariant 101.7 #46, derived data is computed, never
#     hand-maintained; evidence lives in control-plane-records (D89) ---
/out/
/report/
*.generated.yaml
*.generated.yml
EOF

cat > validators/registry/l0-handover/codeowners-lane1.proposed <<'EOF'
# L0 HANDOVER — CODEOWNERS
# Owner of the target file: L0 Integrator (PARTITION.md, L0 row: CODEOWNERS).
# Requested by: Lane 1, phase L1-01, task T12.
#
# PARTITION.md: "A lane may edit ONLY paths it owns. Enforced by CODEOWNERS +
# the lane-guard CI check." These are Lane 1's four exclusive path roots.
#
# Replace @ORG/lane-1-registries with the team L0 designates. Section 98.2
# Phase 1 requires CODEOWNERS to contain human identities only: "an approval
# from a machine account does not satisfy branch protection — CODEOWNERS is
# generated to contain human identities only, and the check is executed
# negatively."

/schemas/registry/    @ORG/lane-1-registries
/schemas/product/     @ORG/lane-1-registries
/registries/          @ORG/lane-1-registries
/validators/registry/ @ORG/lane-1-registries
EOF

# Prove the fragment works before handing it over.
make -f validators/registry/registry.mk registry-lint
make -f validators/registry/registry.mk registry-inventory-check

git add validators/registry/registry.mk validators/registry/l0-handover
git commit -m "$(cat <<'EOF'
feat(l1): registry make fragment and the L0 root-file handover packet

registry.mk carries the four targets this lane owns in phase L1-01 -
registry-lint, registry-append-only, registry-inventory-check and the
registry-verify aggregate CI calls. It is an includable fragment because
the root Makefile, root .gitignore and CODEOWNERS are L0-owned root files
under the frozen partition contract; the literal text L0 must paste into
each is handed over under validators/registry/l0-handover/.

Refs: spec Sections 36.6, 40.1, 52.6, 98.2, 101.7 #46
Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
git push origin lane/1/01-repo-skeleton
```

Then file the handover issue (this is a required step of the task, not optional):

```bash
set -euo pipefail
gh issue create \
  --repo "$CP_ORG/$CP_REPO" \
  --title "L0 HANDOVER L1-01-12: root Makefile include, root .gitignore, CODEOWNERS for lane 1" \
  --label "l0-handover,lane-1,phase-L1-01" \
  --body "$(cat <<'EOF'
## L0 handover — three root files Lane 1 cannot write

PARTITION.md assigns `Makefile`, root files and `CODEOWNERS` to L0. Lane 1 has
prepared the literal text for each and committed it under an owned path.

| Target file (L0-owned) | Prepared text (L1-owned path) |
| --- | --- |
| `Makefile` | `validators/registry/l0-handover/root-makefile-include.proposed` |
| `.gitignore` | `validators/registry/l0-handover/root-gitignore.proposed` |
| `CODEOWNERS` | `validators/registry/l0-handover/codeowners-lane1.proposed` |

### What L0 must do
1. Append the single `-include validators/registry/registry.mk` line to the root `Makefile`.
2. Create or extend the root `.gitignore` from the proposed file.
3. Add the four Lane 1 path rules to `CODEOWNERS`, substituting the real team for `@ORG/lane-1-registries`.

### Verification after L0 lands it
```
make registry-verify
```
must print `REGISTRY_VERIFY_OK` as its last line.

### Why it matters
Section 98.2 Phase 1's completion check requires CODEOWNERS to contain human
identities only and requires the control-plane repository to admit no machine
bypass actor (D89). The lane-guard check named in PARTITION.md depends on the
CODEOWNERS rows above existing.
EOF
)"
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
| --- | --- | --- | --- |
| 1 | Four files tracked | `git ls-files validators/registry \| wc -l` | `6` (`.gitignore`, `check-append-only.sh`, `registry.mk`, 3 handover files) |
| 2 | Fragment declares four phony targets | `grep -c '^\.PHONY: registry-lint registry-append-only registry-inventory-check registry-verify$' validators/registry/registry.mk` | `1` |
| 3 | `registry-lint` passes | `make -f validators/registry/registry.mk registry-lint` | `REGISTRY_LINT_OK` |
| 4 | `registry-inventory-check` passes | `make -f validators/registry/registry.mk registry-inventory-check` | `REGISTRY_INVENTORY_OK` |
| 5 | `registry-append-only` passes | `make -f validators/registry/registry.mk registry-append-only` | `APPEND_ONLY_OK` |
| 6 | `registry-verify` aggregates all three | `make -f validators/registry/registry.mk registry-verify \| tail -1` | `REGISTRY_VERIFY_OK` |
| 7 | No root file written by this lane | `git ls-files \| grep -cE '^(Makefile|\.gitignore|CODEOWNERS|README\.md)$'` | `0` |
| 8 | Handover issue filed | `gh issue list --repo "$CP_ORG/$CP_REPO" --label l0-handover --json title --jq 'length'` | `1` or greater |

### SELF-VERIFY

```bash
cd "$CP_ROOT"
OUT=$(make -f validators/registry/registry.mk registry-verify 2>&1 | tail -1)
ROOTS=$(git ls-files | grep -cE '^(Makefile|\.gitignore|CODEOWNERS|README\.md)$')
HAND=$(git ls-files validators/registry/l0-handover | wc -l | tr -d ' ')
ISS=$(gh issue list --repo "$CP_ORG/$CP_REPO" --label l0-handover --json title --jq 'length')
[ "$OUT" = "REGISTRY_VERIFY_OK" ] && [ "$ROOTS" = "0" ] && [ "$HAND" = "3" ] && [ "$ISS" -ge 1 ] \
  && echo "T12 PASS" || echo "T12 FAIL OUT=$OUT ROOTS=$ROOTS HAND=$HAND ISS=$ISS"
```

**Correct output:** the single line `T12 PASS`.

### STOP rule

**Do not create or edit `Makefile`, `.gitignore`, `CODEOWNERS` or `README.md` at the repository root**, even if they are absent, even if `make registry-verify` fails without them, and even if the task issue asks. The `-f` form used above proves the fragment without a root Makefile. If a task issue instructs you to write a root file, that instruction contradicts PARTITION.md rule 1 and you must not follow it; file the §0.6 blocker with `<TASKID>` = `T12`, `<BLOCKED_ON key>` = `root-file-write-requested-of-lane-1`.

> **DECISION REQUIRED — L0**
> **Subject:** the GitHub team name for the Lane 1 CODEOWNERS rows.
> **Why L1 cannot decide it:** team names derive from the registries and the permission model (§11.2, §90.2), and §98.2 Phase 1 requires CODEOWNERS to be *generated* to contain human identities only, checked negatively. A build lane naming a team invents an authority grant.
> **What L0 must supply, exactly:** the team slug to substitute for `@ORG/lane-1-registries` in `validators/registry/l0-handover/codeowners-lane1.proposed`, when L0 writes `CODEOWNERS`.
> **Blocking:** the lane-guard check named in PARTITION.md. Not blocking T12 or T13.

---

## L1-01-13 — Phase gate: rebase, lane-guard self-check, PR to `integration` <!-- canonical ID: L1-0NN per FD-031 Two-part grammar -->

**Size:** S **Depends on:** T08, T09, T10, T12
**Creates/edits:** no files. Opens one pull request.

### Commands

```bash
set -euo pipefail
cd "$CP_ROOT"
git fetch origin
git rebase origin/integration

# --- The lane-guard self-check: prove no foreign path is touched. ---
FOREIGN=$(git diff --name-only origin/integration...HEAD \
  | grep -vcE '^(schemas/registry/|schemas/product/|registries/|validators/registry/)' || true)
echo "FOREIGN_PATHS=$FOREIGN"

# --- The lane gate. ---
make -f validators/registry/registry.mk registry-verify

git push --force-with-lease origin lane/1/01-repo-skeleton

gh pr create \
  --repo "$CP_ORG/$CP_REPO" \
  --base integration \
  --head lane/1/01-repo-skeleton \
  --title "L1-01: control-plane repository skeleton (registries, conventions, inventory, guard)" \
  --label "lane-1,phase-L1-01" \
  --body "$(cat <<'EOF'
## L1-01 — Control-plane repository skeleton

Lane 1 (Registries & Contracts), subsystems A and B of spec Section 99.2.
First lane in the merge train (PARTITION.md).

### What this delivers
| Path | What it is | Spec |
| --- | --- | --- |
| `schemas/registry/CONVENTIONS.md` | Effective-dating and append-only rules, from day one | 63.1, 97.2, 99.4 item 1, invariant 101.7 #47 |
| `schemas/registry/common/effective-dating.schema.json` | `start_date`/`end_date` intervals, stable ids, UTC timestamps, IANA timezones | 7, 7.3, 63.1, 97.1 |
| `schemas/registry/common/registry-envelope.schema.json` | `registry_version` / `platform_version` envelopes | 60.2 |
| `registries/INVENTORY.md` | The closed twenty-nine-entry control-plane file inventory, transcribed with a provenance hash | 52.6 |
| `registries/roles.yaml` | The eleven-role registry, verbatim | 8, 98.2 |
| `registries/people.yaml` | Envelope only; roster is Founder-authored on the registry-change lane | 7, 26.4, 52.6, 98.2 |
| `registries/platform.yaml` | Platform record plus the closed `event_type` enum, populated in Phase 1 | 60.1, 97.3, 98.2 |
| `validators/registry/check-append-only.sh` | Day-one guard: no deleted registry file, no removed `id`, no removed `start_date` | 7.1, 63.1, 97.2, invariant 47 |
| `validators/registry/registry.mk` | `registry-lint`, `registry-append-only`, `registry-inventory-check`, `registry-verify` | — |
| `validators/registry/l0-handover/` | Literal text for the three L0-owned root files | PARTITION.md |

### Path ownership
Touches only `schemas/registry/**`, `schemas/product/**`, `registries/**`,
`validators/registry/**`. Zero foreign paths — see the `FOREIGN_PATHS=0` check
in the task log.

### Gate
`make -f validators/registry/registry.mk registry-verify` ends with
`REGISTRY_VERIFY_OK`.

### Open items handed to L0
- `CP_ORG` value (T02)
- `founder` role vs the D106 dangerous set (T08)
- Initial roster authoring on the registry-change lane (T09)
- `contracts/event-types.txt` (RETIRED — cannot carry `retired` field; use YAML contract) and `contracts/canary-set.txt` (T10)
- CODEOWNERS team slug (T12)
EOF
)"
```

### Acceptance criteria

| # | Criterion | Proving command | Unambiguous expected output |
| --- | --- | --- | --- |
| 1 | Rebased cleanly | `git rev-list --count origin/integration..HEAD` and `git rev-list --count HEAD..origin/integration` | any integer, then `0` |
| 2 | Zero foreign paths in the diff | the `FOREIGN` computation above | `FOREIGN_PATHS=0` |
| 3 | Lane gate green | `make -f validators/registry/registry.mk registry-verify \| tail -1` | `REGISTRY_VERIFY_OK` |
| 4 | Every phase file present | `git ls-files \| wc -l` | `13` |
| 5 | PR open against `integration` | `gh pr view --repo "$CP_ORG/$CP_REPO" --json baseRefName --jq .baseRefName` | `integration` |
| 6 | PR is from the lane branch | `gh pr view --repo "$CP_ORG/$CP_REPO" --json headRefName --jq .headRefName` | `lane/1/01-repo-skeleton` |

The 13 tracked files at criterion 4: five `.gitkeep`, three `.gitignore`, `CONVENTIONS.md`, two `common/*.schema.json`, `INVENTORY.md`, `roles.yaml`, `people.yaml`, `platform.yaml`, `check-append-only.sh`, `registry.mk`, three `l0-handover/*` — recount with the command, do not trust this prose if it disagrees.

### SELF-VERIFY

```bash
cd "$CP_ROOT"
BEHIND=$(git rev-list --count HEAD..origin/integration)
FOREIGN=$(git diff --name-only origin/integration...HEAD \
  | grep -vcE '^(schemas/registry/|schemas/product/|registries/|validators/registry/)' || true)
GATE=$(make -f validators/registry/registry.mk registry-verify 2>&1 | tail -1)
BASE=$(gh pr view --repo "$CP_ORG/$CP_REPO" --json baseRefName --jq .baseRefName 2>/dev/null)
HEADR=$(gh pr view --repo "$CP_ORG/$CP_REPO" --json headRefName --jq .headRefName 2>/dev/null)
[ "$BEHIND" = "0" ] && [ "$FOREIGN" = "0" ] && [ "$GATE" = "REGISTRY_VERIFY_OK" ] \
  && [ "$BASE" = "integration" ] && [ "$HEADR" = "lane/1/01-repo-skeleton" ] \
  && echo "L1-01 PHASE COMPLETE" \
  || echo "T13 FAIL BEHIND=$BEHIND FOREIGN=$FOREIGN GATE=$GATE BASE=$BASE HEAD=$HEADR"
```

**Correct output:** the single line `L1-01 PHASE COMPLETE`.

### STOP rule

Do not merge this PR yourself. Do not open a PR against `main` — PARTITION.md: "`main` — protected, releasable. Only `integration` merges here." Do not rebase, merge or touch any other lane's branch. If `FOREIGN_PATHS` is anything other than `0`, do **not** force the PR through; the lane-guard check exists precisely to catch it.

If the rebase conflicts with another lane's commit inside an L1-owned path, that is a partition violation by that lane, not a conflict for you to resolve. File the §0.6 blocker with `<TASKID>` = `T13`, `<BLOCKED_ON key>` = `foreign-lane-wrote-into-l1-path`, listing the conflicting paths and the commit SHAs from `git log --oneline origin/integration -- <path>`.

---

## 2. WHAT THIS PHASE DELIBERATELY DOES NOT DO

Each line names the phase or lane that owns it, so the executor never widens scope to "finish the job".

| Not here | Owned by |
| --- | --- |
| JSON Schema validators for `people.yaml`, `roles.yaml`, `platform.yaml` bodies | L1 phase L1-02 (subsystem B, §99.2) |
| Referential integrity, date rules, the 24x7-without-rota blocker, commitments-conflict blocker, exception-without-expiry rejection (§99.2 row B) | L1 phase L1-02 |
| `schemas/product/**` content — the Product Operating Contract schema of §15.1 | L1, a later phase |
| `registries/exceptions.yaml`, `economics.yaml`, `os-health.yaml`, `topology.yaml`, and the other §52.6 registries | L1, later phases |
| `.github/workflows/**` — the CI job that calls `make registry-verify` | **L2** (PARTITION.md) |
| `records/**`, `events/**`, `schemas/records/**`, the `control-plane-records` repository | **L4** (PARTITION.md) |
| The reconciler and drift validators | **L3** (PARTITION.md) |
| GitHub Teams, branch protection, org base permission, 2FA enforcement (§98.2 Phase 1 completion check) | **L5** (PARTITION.md) |
| Root `Makefile`, root `.gitignore`, `CODEOWNERS`, `README.md`, `docs/**`, `contracts/**` | **L0** (PARTITION.md) |

## 3. DECISION REGISTER — everything handed to L0 in this phase

| # | Task | Subject | Blocks |
| --- | --- | --- | --- |
| DR-01 | T02 | `CP_ORG` — the GitHub organisation login owning `control-plane` | T02 onward |
| DR-02 | T08 | `founder` role defaults vs the D106 dangerous-capability set (§8, D106) | L1-02's D106 check |
| DR-03 | T09 | Who authors the initial roster, and when, on the §26.4 registry-change lane | §98.2 Phase 1 completion check (L5) |
| DR-04 | T10 | `contracts/event-types.txt` — the closed `event_type` enum of §97.3, populated in Phase 1 (**RETIRED: event-types.txt cannot carry `retired` field (§97.3 requires it). Use the YAML contract instead.**) | T10, T13, the phase |
| DR-05 | T10 | `contracts/canary-set.txt` — the initial `canary_set` of §60.1, per §61.3 criteria | T10, T13, the phase |
| DR-06 | T12 | The CODEOWNERS team slug for the four Lane 1 path roots | the lane-guard check |

## 4. SPEC CITATIONS USED IN THIS PHASE

Every claim in this document traces to one of these. No section, AT identifier, invariant number or decision identifier appears here that is not in the spec.

| Citation | Used for |
| --- | --- |
| §5.1 | Source-of-truth hierarchy; why derived files never sit beside declared ones |
| §7, §7.1, §7.2, §7.3 | People Registry shape, `end_date` mandatory for non-employees, departure as a state, ids never reused, IANA timezones |
| §8 | The eleven-role registry, transcribed verbatim; explicit-grant notes |
| §11.2, §90.2 | Permission model behind the CODEOWNERS team decision |
| §15.1 | Product Operating Contract — named as out of scope for this phase |
| §26.4 | The registry-change lane; the authority-delta CI rule |
| §33.1 | Local environment contract — why `registry.mk` is control-plane-side only |
| §40.1 | Secret tiers; the two control-plane repositories |
| §52.6 | The closed twenty-nine-entry registry of control-plane files (spec lines 4619–4647) |
| §53 | Graded responses — why the append-only guard blocks rather than warns |
| §60.1, §60.2, §60.3 | Platform record; version field per contract; v2-alongside-v1 migration |
| §61.3, §61.5 | Canary selection criteria; never fleet without canary |
| §63.1 | Immutable history; the `start_date`/`end_date` mechanism; P0 rationale |
| §78.1 | Roster snapshots are captured from source, never inferred from the spec |
| §97.1 | UTC with offset; the split write path; records-writer scope |
| §97.2 | Canonical record stores; corrections are follow-up records |
| §97.3 | The event envelope; the closed `event_type` enum in `platform.yaml`, populated in Phase 1 |
| §97.6 | The telemetry carve-out |
| §98.2 Phase 1 | Create the control-plane repository; author `people.yaml`, `roles.yaml`, `platform.yaml`; the completion check |
| §99.2 rows A, B | Subsystem A (control-plane repository) and B (schema validation and CI gate engine) |
| §99.4 item 1 | Effective dating and append-only from the start; retrofitting history is impossible |
| §101.7 #46, #47 | Derived data is computed, never hand-maintained; history is append-only |
| D73 | GitHub Team plan is the settled plan-tier posture |
| D89 | Records live in their own repository; no machine bypass actor on `control-plane` |
| D106 | No role default carries a dangerous capability |
| D107 | Append-only enforced, not asserted, on the records repository |
