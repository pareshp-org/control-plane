# 05 — The Git Workflow, Literally

**Audience:** the AI coding agent executing one lane task. You have no repo context and no memory of previous tasks. Everything you need is on this page or on your task card.

**What this file is:** every git command you will ever run on this programme, in the order you run them, with the output you should see. If a command you are about to type is not on this page, you are about to do something you are not authorised to do — stop and read [§14 Forbidden commands](#14-forbidden-commands).

**Authority:** this file implements the branch and merge model frozen in `C:/D_Drive/PS/MultiProduct/Code/implementation/PARTITION.md` ("Branch & merge model", "Non-negotiable anti-conflict rules"). Where this file and `PARTITION.md` disagree, `PARTITION.md` wins and this file is a defect — open a blocker (§15) rather than guessing. Protection behaviour cited here is from `C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md` §11.3 (branch protection configuration) and §40.1 (D89 repository split, D107 append-only enforcement).

**Shell:** every fenced block on this page is `bash`. On Windows run them in **Git Bash** (`C:\Program Files\Git\bin\bash.exe`), not PowerShell and not `cmd`. Paste blocks whole. Do not retype them from memory.

---

## 0. The five facts you must have before you type anything

Your task card gives you these. If **any** one of them is missing, blank, or you are inferring it, **STOP** and open a blocker (§15). Do not guess an org name. Do not guess a lane number. Do not guess a branch name.

| Fact | Variable | Example value | Where it comes from |
|---|---|---|---|
| GitHub organisation | `ORG` | `$ORG` | task card |
| Repository | `REPO` | `control-plane` | task card |
| Your lane number | `LANE` | `1` | task card |
| Phase slug | `PHASE` | `p1` | task card |
| Task slug | `TASK` | `registry-schema` | task card |
| Task card id | `TASK_ID` | `L1-P1-004` | task card |
| Machine identity name | `AGENT_NAME` | `lane1-bot` | task card |
| Machine identity email | `AGENT_EMAIL` | `lane1-bot@users.noreply.github.com` | task card |

Only two repositories are ever cloned by a lane agent:

| `REPO` value | Who may write it | Notes |
|---|---|---|
| `control-plane` | lanes 1, 2, 3, 4, 5 — each inside its own owned paths only | Full branch protection (spec §11.3). No machine bypass actor exists (spec §40.1, D89). |
| `control-plane-records` | **lane 4 only** | No review protection, but a no-bypass ruleset blocks force-push and branch/tag deletion (spec §40.1, D107). |

`product-template` and the eight live products are **never** cloned by a lane agent. If your task card names one of them as `REPO`, that card is wrong — STOP, open a blocker (§15).

---

## 1. Your lane's owned paths — the whole of the law

Copied verbatim from the FROZEN partition. This table is the answer to every "am I allowed to touch this file?" question. There is no other answer and there is no judgement call.

| Lane | Branch prefix | OWNS, exclusively, in `control-plane` |
|---|---|---|
| L1 | `lane/1/*` | `schemas/registry/**`, `schemas/product/**`, `registries/**`, `validators/registry/**` |
| L2 | `lane/2/*` | `.github/workflows/**`, `templates/workflows/**`, `tools/evidence/**` |
| L3 | `lane/3/*` | `reconciler/**`, `tools/provision/**`, `validators/drift/**` |
| L4 | `lane/4/*` | `schemas/records/**`, `metrics/**`, `tools/records/**` — **plus all of the separate `control-plane-records` repo** |
| L5 | `lane/5/*` | `access/**`, `infra/**`, `ops-vm/**`, `notify/**`, `assets/**` |
| L0 | `main`, `integration` | `contracts/**`, `CODEOWNERS`, `docs/**`, root files, `Makefile` — **you are not L0** |

Three consequences you must internalise:

1. `contracts/**` is frozen and belongs to L0. You read it. You never edit it. Needing a contract change is a blocker, not a task (`PARTITION.md`, rule 2).
2. Nothing outside your row is yours, **even if it is obviously broken**. Seeing an adjacent bug is not authorisation to fix it. File it (§15) and carry on with your own task.
3. If another lane already owns the thing you were about to build, you do not build it. Check this table before writing the first line of code.

---

## 2. Step 0 — Set the session variables

Paste this block, with your task card's values substituted into the first eight lines. Substitute nothing else.

```bash
set -euo pipefail
# ---- FROM YOUR TASK CARD — substitute these eight values ----
export ORG="$ORG"
export REPO="control-plane"
export LANE="1"
export PHASE="p1"
export TASK="registry-schema"
export TASK_ID="L1-P1-004"
export AGENT_NAME="lane1-bot"
export AGENT_EMAIL="lane1-bot@users.noreply.github.com"
# ---- DERIVED — do not edit these four lines ----
export BRANCH="lane/${LANE}/${PHASE}-${TASK}"
export REMOTE_URL="https://github.com/${ORG}/${REPO}.git"
export WORKDIR="${HOME}/work/${REPO}"
export BASE="origin/integration"
```

Verify what you just set. Read every line of the output and confirm it matches your card:

```bash
printf 'ORG=%s\nREPO=%s\nLANE=%s\nBRANCH=%s\nREMOTE_URL=%s\nWORKDIR=%s\nBASE=%s\n' \
  "$ORG" "$REPO" "$LANE" "$BRANCH" "$REMOTE_URL" "$WORKDIR" "$BASE"
```

Expected output:

```
ORG=$ORG
REPO=control-plane
LANE=1
BRANCH=lane/1/p1-registry-schema
REMOTE_URL=https://github.com/$ORG/control-plane.git
WORKDIR=/c/Users/you/work/control-plane
BASE=origin/integration
```

**STOP rule.** If any variable printed empty, or `BRANCH` does not start with `lane/<your lane number>/`, do not continue. Re-run §2. If it is still wrong, open a blocker (§15).

---

## 3. Step 1 — Load the scope guard

This is the local mirror of the CI `lane-guard` check. It is the single most important block on this page: it is what stops you from silently committing a file your lane does not own. Paste it verbatim into every shell session, before you touch anything.

```bash
set -euo pipefail
lane_owns() {
  case "$LANE" in
    1) printf '%s\n' 'schemas/registry/' 'schemas/product/' 'registries/' 'validators/registry/' ;;
    2) printf '%s\n' '.github/workflows/' 'templates/workflows/' 'tools/evidence/' ;;
    3) printf '%s\n' 'reconciler/' 'tools/provision/' 'validators/drift/' ;;
    4) printf '%s\n' 'schemas/records/' 'metrics/' 'tools/records/' ;;
    5) printf '%s\n' 'access/' 'infra/' 'ops-vm/' 'notify/' 'assets/' ;;
    *) echo "UNKNOWN LANE: $LANE" >&2 ; return 1 ;;
  esac
}

scope_check() {
  CMP="${1:-$BASE}"
  git rev-parse --verify "$CMP" > /dev/null 2>&1 || { echo "ERROR: base ref '$CMP' is not a valid ref"; exit 1; }
  BAD=0
  if [ "$REPO" = "control-plane-records" ]; then
    if [ "$LANE" != "4" ]; then
      echo "SCOPE FAIL: lane $LANE may not write control-plane-records"
      return 1
    fi
    echo "SCOPE OK: lane 4 owns all of control-plane-records"
    return 0
  fi
  for P in $(git diff --name-only "${CMP}...HEAD"); do
    HIT=0
    for OWN in $(lane_owns); do
      case "$P" in "$OWN"*) HIT=1 ;; esac
    done
    if [ "$HIT" -eq 0 ]; then echo "FOREIGN PATH: $P"; BAD=1; fi
  done
  if [ "$BAD" -eq 0 ]; then
    echo "SCOPE OK: every changed path is owned by lane $LANE"
  else
    echo "SCOPE FAIL: lane $LANE does not own the paths listed above"
  fi
  return "$BAD"
}
```

Confirm it loaded:

```bash
lane_owns
```

Expected output for `LANE=1`:

```
schemas/registry/
schemas/product/
registries/
validators/registry/
```

**Filename rule.** Never create a file or directory whose name contains a space. `scope_check` splits on whitespace and a spaced filename will slip past it. Use `kebab-case` only.

---

## 4. Step 2 — Clone

```bash
set -euo pipefail
mkdir -p "$(dirname "$WORKDIR")"
git clone "$REMOTE_URL" "$WORKDIR"
cd "$WORKDIR"
```

Expected output (numbers will differ; the shape will not):

```
Cloning into '/c/Users/you/work/control-plane'...
remote: Enumerating objects: 1284, done.
remote: Counting objects: 100% (1284/1284), done.
remote: Compressing objects: 100% (742/742), done.
remote: Total 1284 (delta 512), reused 1201 (delta 470), pack-reused 0
Receiving objects: 100% (1284/1284), 1.84 MiB | 6.30 MiB/s, done.
Resolving deltas: 100% (512/512), done.
```

If the directory already exists from a previous task, do **not** reuse it blindly. Reset it to a known-clean state:

```bash
set -euo pipefail
cd "$WORKDIR"
git fetch origin --prune
git switch integration
git reset --hard origin/integration
git clean -fdx
git status --porcelain
```

Expected output of the final command: **nothing at all** (zero lines). Any line of output means the tree is still dirty; run `git clean -fdx` again and re-check.

**STOP rule.** If `git clone` fails with `Repository not found` or `Authentication failed`, you do not have access and you cannot fix that yourself. Open a blocker (§15). Do not try alternative URLs, do not switch to SSH, do not create a token.

---

## 5. Step 3 — Configure identity

Local to this clone only. Never `--global` — a global identity leaks into every other repo on the machine.

```bash
set -euo pipefail
cd "$WORKDIR"
git config --local user.name  "$AGENT_NAME"
git config --local user.email "$AGENT_EMAIL"
git config --local pull.rebase true
git config --local rebase.autoStash false
git config --local push.default simple
git config --local advice.detachedHead false
```

Verify:

```bash
git config --local --get-regexp '^(user|pull|rebase|push)\.' | sort
```

Expected output:

```
pull.rebase true
push.default simple
rebase.autoStash false
user.email lane1-bot@users.noreply.github.com
user.name lane1-bot
```

`rebase.autoStash false` is deliberate. Auto-stashing hides uncommitted work during a rebase and is a leading cause of an agent reporting success over a half-finished tree. You will commit before you rebase, every time.

**Signing.** Do not configure commit signing. Signing is the records-writer credential's job on the default branch of `control-plane-records` (spec §40.1, D107); a lane agent signs nothing. If your task card supplies a signing key, that card is wrong — STOP, open a blocker (§15).

---

## 6. Step 4 — Create your lane branch from `integration`

Always from `integration`. Never from `main`. Never from another lane's branch.

```bash
set -euo pipefail
cd "$WORKDIR"
git fetch origin --prune
git switch --create "$BRANCH" origin/integration
```

Expected output:

```
From https://github.com/$ORG/control-plane
 * [new branch]      integration -> origin/integration
branch 'lane/1/p1-registry-schema' set up to track 'origin/integration'.
Switched to a new branch 'lane/1/p1-registry-schema'
```

Now break the accidental tracking link, so that a bare `git push` can never target `integration`:

```bash
set -euo pipefail
git branch --unset-upstream
git rev-parse --abbrev-ref HEAD
git log --oneline -1
```

Expected output:

```
lane/1/p1-registry-schema
9c3d1a2 L0 p0: freeze contracts v1
```

**Self-verify — run this before every single commit.** It is three checks in one: you are on a branch, that branch is yours, and it is not a protected branch.

```bash
set -euo pipefail
CUR="$(git rev-parse --abbrev-ref HEAD)"
case "$CUR" in
  "lane/${LANE}/"*) echo "BRANCH OK: $CUR" ;;
  *) echo "BRANCH FAIL: on '$CUR', expected lane/${LANE}/* — see section 11" ;;
esac
```

Expected output:

```
BRANCH OK: lane/1/p1-registry-schema
```

If it says `BRANCH FAIL`, go to [§11 Recovery A](#11-recovery-a--you-committed-to-the-wrong-branch) now. Do not commit first.

---

## 7. Step 5 — Stage and commit

### 7.1 Staging — explicit paths only

```bash
git add schemas/registry/product-record.schema.json
git add validators/registry/validate-product-record.py
```

**Never** run any of these. Each one is a direct route to committing a file your lane does not own:

```
git add .          # FORBIDDEN
git add -A         # FORBIDDEN
git add --all      # FORBIDDEN
git commit -a      # FORBIDDEN
git commit --all   # FORBIDDEN
```

Look at exactly what is staged before you commit:

```bash
git status --short
```

Expected output — every line is a file you named on purpose:

```
A  schemas/registry/product-record.schema.json
A  validators/registry/validate-product-record.py
```

A line beginning with `??` is an untracked file you have not staged. That is fine only if it is scratch output you intend to throw away. If it is part of the deliverable and you leave it unstaged, you will report a task complete that is not complete. Stage it or delete it — never leave it.

### 7.2 Commit message format — use `master/09`'s template (B4)

`master/09-glossary-and-conventions.md` §5.1 is the one canonical commit template: header
`<type>(<scope>): <subject>`, then a body, then the eight-trailer block (`Task-Id:`, `Lane:`,
`Phase:`, `Spec:`, `AT:`, `Invariant:`, `Agent-Authored:`, `Self-Verify:`) — read §5.1–§5.4
there for the exact shapes and the enumerated `<scope>` tokens. It supersedes the three-trailer
form previously shown here (`Task:` / `Lane:` / `Paths:`): that form omits `Phase`, `Spec`,
`AT`, `Invariant`, `Agent-Authored` and `Self-Verify`, all five of which spec §97.2 or `master/09`
requires on every lane commit.

### 7.3 Commit

```bash
set -euo pipefail
git commit -m "schema(schemas-registry): add product-record schema and validator" \
           -m "Adds the product-record schema and its validator for registry_version 1." \
           -m "Task-Id: ${TASK_ID}
Lane: L${LANE}
Phase: ${PHASE}
Spec: <citations — master/09 §2.1 format>
AT: <AT-ids, or none>
Invariant: <invariant numbers, or none>
Agent-Authored: true
Self-Verify: <the exact command from your task card>"
```

Expected output:

```
[lane/1/p1-registry-schema 4a81f30] schema(schemas-registry): add product-record schema and validator
 2 files changed, 118 insertions(+)
 create mode 100644 schemas/registry/product-record.schema.json
 create mode 100644 validators/registry/validate-product-record.py
```

### 7.4 Scope self-check — mandatory, every commit, no exceptions

```bash
git fetch origin --prune
scope_check
```

Expected output:

```
SCOPE OK: every changed path is owned by lane 1
```

If it prints `FOREIGN PATH:` for any file, go to [§12 Recovery B](#12-recovery-b--you-touched-a-foreign-path) immediately. Do not push. Do not open a PR. The CI `lane-guard` check will fail anyway; failing locally costs you one minute and failing in CI costs the whole merge train a cycle.

---

## 8. Step 6 — Rebase onto `integration`

Do this immediately before opening a PR, and again any time `integration` moves under you (branch protection requires branches to be up to date before merging — spec §11.3).

Pre-flight. The working tree must be clean; `rebase.autoStash` is off, so a dirty tree will abort the rebase and that is the intended behaviour:

```bash
git status --porcelain
```

Expected output: **nothing**. If there is output, commit it (§7) or `git restore` it. Do not stash — stashed work is work you will forget.

Rebase:

```bash
git fetch origin --prune
git rebase origin/integration
```

Expected output on success:

```
Successfully rebased and updated refs/heads/lane/1/p1-registry-schema.
```

Or, if nothing moved:

```
Current branch lane/1/p1-registry-schema is up to date.
```

Re-verify scope after the rebase — a rebase replays your commits onto new content and you must confirm the result is still inside your lane:

```bash
scope_check
```

Expected output:

```
SCOPE OK: every changed path is owned by lane 1
```

If the rebase stops with a conflict, go to §9. Do not improvise.

---

## 9. Step 7 — The only conflict class that can occur, and how to resolve it

### 9.1 Why there is only one

The partition makes cross-lane conflicts structurally impossible. One owner per path (`PARTITION.md` rule 1) means no other lane's commits can ever touch a file of yours. No shared mutable file (rule 3) means there is no index, list, or registry-of-everything that two branches append to. Additive-only (rule 5) means edits are rare and confined.

So exactly one conflict class remains:

> **Your lane's own earlier branch already merged into `integration` and changed the same owned file your branch changes.**

Same lane. Same owned path. Two additive edits to one file. That is it.

### 9.2 The decision, made for you

When the rebase stops, your **only** job is to answer one question: *is the conflicted path inside my lane's owned list?* You do not read the diff to decide whether the change is a good idea. You do not choose a "better" version.

```bash
git diff --name-only --diff-filter=U
```

Expected output:

```
schemas/registry/product-record.schema.json
```

Classify it:

```bash
set -euo pipefail
for P in $(git diff --name-only --diff-filter=U); do
  HIT=0
  for OWN in $(lane_owns); do
    case "$P" in "$OWN"*) HIT=1 ;; esac
  done
  if [ "$HIT" -eq 1 ]; then echo "IN-LANE CONFLICT: $P  -> resolve, section 9.3"
  else echo "FOREIGN CONFLICT: $P  -> STOP, section 9.4"; fi
done
```

Expected output for the resolvable case:

```
IN-LANE CONFLICT: schemas/registry/product-record.schema.json  -> resolve, section 9.3
```

### 9.3 Resolving an in-lane conflict — keep both sides

Because both sides are additive work from your own lane, the correct resolution is **union**: keep the content from `integration` **and** keep your content. Deleting either side destroys a colleague's merged work or your own task deliverable.

Open the conflicted file. You will see:

```
<<<<<<< HEAD
  "retention_class": { "type": "string" },
=======
  "record_origin": { "type": "string" },
>>>>>>> 4a81f30 (L1 p1-registry-schema: add product-record schema and validator)
```

`HEAD` is `integration` (the side already merged). The lower side is yours. Resolve to both, and delete all three marker lines:

```
  "retention_class": { "type": "string" },
  "record_origin": { "type": "string" },
```

Confirm no marker survived anywhere in the tree:

```bash
git grep -n -E '^(<<<<<<<|=======|>>>>>>>)' -- . ; echo "exit=$?"
```

Expected output:

```
exit=1
```

`exit=1` means `git grep` found nothing — correct. **`exit=0` means a conflict marker is still in a file and you must go back and remove it.** A committed conflict marker is the classic "reported success while broken" failure. Do not proceed on `exit=0`.

Then continue the rebase:

```bash
git add schemas/registry/product-record.schema.json
git rebase --continue
```

Expected output (an editor may open on the commit message — save and close it unchanged):

```
Successfully rebased and updated refs/heads/lane/1/p1-registry-schema.
```

Re-run the scope check and your task's own test command:

```bash
scope_check
```

Expected output:

```
SCOPE OK: every changed path is owned by lane 1
```

**STOP rule.** If the union resolution is not obviously correct — if the two sides contradict each other rather than sit beside each other, if the same key is defined twice with different types, if you find yourself deciding which definition is right — that is a design decision. You have no authority to make it. Run §9.4's abort, then open a blocker (§15).

### 9.4 A foreign-path conflict is not a conflict — it is a partition violation

If any conflicted path is **outside** your lane's list, something upstream is wrong: either your branch touched a foreign path (see §12) or the partition has been breached. Either way you resolve nothing. Abort and report:

```bash
set -euo pipefail
git rebase --abort
git status --porcelain
git rev-parse --abbrev-ref HEAD
```

Expected output:

```
lane/1/p1-registry-schema
```

(`git status --porcelain` prints nothing; the branch is back exactly as it was before the rebase.) Now open a blocker (§15). Do not retry the rebase. Do not `git checkout --theirs`. Do not delete the foreign file.

---

## 10. Step 8–11 — Amend, push, PR, review, cleanup

### 10.1 Step 8 — Amend

Amending rewrites your last commit. It is allowed in exactly one window: **before any human has reviewed the PR.** Once a review exists, amending destroys the diff the reviewer read, and branch protection dismisses stale approvals on new pushes (spec §11.3) — so an amend after review silently throws away an approval.

| Situation | Allowed action |
|---|---|
| Not yet pushed | `git commit --amend` freely |
| Pushed, PR still draft, no review submitted | `git commit --amend` then force-push with lease (§10.2) |
| Any review submitted, or PR marked ready | **Amend is forbidden.** Add a new commit (§10.4) |

Amend the message only:

```bash
set -euo pipefail
git commit --amend -m "L${LANE} ${PHASE}-${TASK}: add product-record schema and validator" \
                   -m "Task: ${TASK_ID}
Lane: L${LANE}
Paths: schemas/registry/, validators/registry/"
```

Amend to include a forgotten file:

```bash
git add schemas/registry/product-record.schema.json
git commit --amend --no-edit
```

Expected output:

```
[lane/1/p1-registry-schema 5b7e4f0] L1 p1-registry-schema: add product-record schema and validator
 Date: Thu Aug 27 21:04:11 2026 +0530
 2 files changed, 121 insertions(+)
```

Note the SHA changed (`4a81f30` → `5b7e4f0`). That is why the next push must be a force-push, and why it must be a *safe* one.

### 10.2 Step 9 — Force-push your OWN branch, safely

Three guards, in order. Run all three. Do not skip to the push.

**Guard 1 — the branch is yours.**

```bash
set -euo pipefail
CUR="$(git rev-parse --abbrev-ref HEAD)"
case "$CUR" in
  "lane/${LANE}/"*) echo "PUSH GUARD 1 OK: $CUR" ;;
  *) echo "PUSH GUARD 1 FAIL: refusing to push from '$CUR'" ;;
esac
```

Expected output:

```
PUSH GUARD 1 OK: lane/1/p1-registry-schema
```

**Guard 2 — you are not force-pushing a records repo.** The `control-plane-records` ruleset blocks force-push and deletion with no bypass actor (spec §40.1, D107); a rewrite there is Blocking drift, Level 5.

```bash
set -euo pipefail
if [ "$REPO" = "control-plane-records" ]; then
  echo "PUSH GUARD 2: force-push is FORBIDDEN in this repo — use a plain push only"
else
  echo "PUSH GUARD 2 OK: force-with-lease permitted on lane branches in $REPO"
fi
```

**Guard 3 — the remote is where you last left it.** `--force-with-lease` refuses the push if someone else moved the branch; `--force-if-includes` additionally refuses if your local ref did not actually incorporate what you fetched. Together they make a force-push safe. Plain `--force` has neither guard and is forbidden (§14).

First push of a branch (no force needed):

```bash
git push --set-upstream origin "$BRANCH"
```

Expected output:

```
Enumerating objects: 9, done.
Counting objects: 100% (9/9), done.
Delta compression using up to 8 threads
Compressing objects: 100% (6/6), done.
Writing objects: 100% (7/7), 2.41 KiB | 2.41 MiB/s, done.
Total 7 (delta 2), reused 0 (delta 0), pack-reused 0
remote: Resolving deltas: 100% (2/2), completed with 1 local object.
To https://github.com/$ORG/control-plane.git
 * [new branch]      lane/1/p1-registry-schema -> lane/1/p1-registry-schema
branch 'lane/1/p1-registry-schema' set up to track 'origin/lane/1/p1-registry-schema'.
```

Every later push after an amend or a rebase:

```bash
git fetch origin --prune
git push --force-with-lease --force-if-includes origin "$BRANCH"
```

Expected output — note `(forced update)`:

```
To https://github.com/$ORG/control-plane.git
 + 4a81f30...5b7e4f0 lane/1/p1-registry-schema -> lane/1/p1-registry-schema (forced update)
```

Expected output when the lease is **stale** — someone or something moved the remote branch:

```
To https://github.com/$ORG/control-plane.git
 ! [rejected]        lane/1/p1-registry-schema -> lane/1/p1-registry-schema (stale info)
error: failed to push some refs to 'https://github.com/$ORG/control-plane.git'
```

**STOP rule.** A stale-info rejection means the remote branch contains commits you have never seen. You must not overwrite them. Do not add `--force`. Run:

```bash
git fetch origin --prune
git log --oneline "$BRANCH..origin/$BRANCH"
```

If that prints any commits, they are not yours to discard — open a blocker (§15) quoting the output.

### 10.3 Step 10 — Open the pull request

Base is **always** `integration`. Never `main`. Open it as a **draft**: a machine identity opens draft pull requests and never merges, approves, or deploys (spec §11.3: Code Owner review is human-only and no machine approval can satisfy it). Marking a PR ready is L0's call, not yours.

**Title and body — use `master/09`'s template (B4).** `master/09-glossary-and-conventions.md` §6.1
fixes the title (`[<task-id>] <type>(<scope>): <subject>`, byte-identical to the first commit's
header) and §6.2 fixes the nine-section body. This supersedes the shorter body previously shown
here — that form had no `## Spec references` or `## Contract Change Request` section and no
`Agent-Authored:` trailer line, all of which the canonical template requires. The "Not done in
this PR" content stays mandatory; it goes inside `## Acceptance criteria` as the honesty rule
below still says.

```bash
set -euo pipefail
gh pr create \
  --repo "${ORG}/${REPO}" \
  --base integration \
  --head "$BRANCH" \
  --draft \
  --title "[${TASK_ID}] schema(schemas-registry): add product-record schema and validator" \
  --body "## Task
${TASK_ID} — add the product-record schema and validator

## Lane and paths
Lane: L${LANE}
Paths touched (every one owned by this lane per PARTITION.md):
- schemas/registry/
- validators/registry/

## Spec references
- <§section — what it requires>
- <AT-nnn — what it tests, or 'none'>

## What changed
Adds the product-record schema and its validator for registry_version 1.

## Acceptance criteria
- [x] <criterion, stated as an observable fact>
- [x] Not done in this PR: nothing; the task card's acceptance criteria are fully met

## Self-verify transcript
\`\`\`
\$ scope_check
SCOPE OK
\$ git grep -E '^(<<<<<<<|=======|>>>>>>>)'; echo exit=\$?
exit=1
<task self-verify command from the task card, and its pasted PASS output>
\`\`\`

## Agent-authored
Agent-Authored: true

## STOP conditions
None encountered.

## Contract Change Request
None.

Draft: awaiting L0 to mark ready. This PR does not merge itself."
```

Expected output — a single URL line:

```
https://github.com/$ORG/control-plane/pull/412
```

Capture it, you will need it:

```bash
export PR_URL="https://github.com/$ORG/control-plane/pull/412"
gh pr view "$PR_URL" --json number,isDraft,baseRefName,headRefName
```

Expected output:

```json
{"baseRefName":"integration","headRefName":"lane/1/p1-registry-schema","isDraft":true,"number":412}
```

**Check `"baseRefName":"integration"` with your own eyes.** If it says `main`, change the base — do not close the PR; GitHub does not let a reopen rewrite the base, so closing and reopening leaves the base wrong:

```bash
gh pr edit "$PR_URL" --base integration
```

**Honesty rule for the body.** The "Not done" line inside `## Acceptance criteria` is not optional. If you completed nine of ten acceptance criteria, you write the tenth one there and you say so in your report. A PR that claims completeness it does not have is the single worst outcome available to you — worse than an unfinished task, because it removes the reviewer's ability to catch it.

**Merge train.** Lanes merge to `integration` in the fixed order L1 → L4 → L2 → L3 → L5, once per cycle (`PARTITION.md`). You do not control when your PR merges and you never merge it yourself. After the PR URL is reported, your task is over until a reviewer responds.

### 10.4 Step 11 — Respond to a review

Read the review:

```bash
gh pr view "$PR_URL" --comments
```

Rules:

- **Append, never amend.** After a review exists, every change is a new commit. Amending or rebasing at this point dismisses the reviewer's approval and destroys the diff they read.
- **Never** `gh pr review`, `gh pr merge`, `gh pr ready`, or `gh pr edit --add-reviewer`. You cannot approve, cannot merge, cannot promote out of draft (spec §11.3: Code Owner review is human-only and no machine approval can satisfy it).
- A review comment asking for something **outside your owned paths** is not actionable by you. Reply saying so and open a blocker (§15). Do not comply.

Make the change, then:

```bash
set -euo pipefail
git add schemas/registry/product-record.schema.json
git commit -m "L${LANE} ${PHASE}-${TASK}: address review — tighten retention_class enum" \
           -m "Task: ${TASK_ID}
Lane: L${LANE}
Paths: schemas/registry/"
scope_check
git push origin "$BRANCH"
```

Expected output of the push — an ordinary fast-forward, **no** `(forced update)`:

```
To https://github.com/$ORG/control-plane.git
   5b7e4f0..8d20c61  lane/1/p1-registry-schema -> lane/1/p1-registry-schema
```

Reply in the PR:

```bash
gh pr comment "$PR_URL" --body "Addressed in 8d20c61: retention_class narrowed to the enum defined in this schema. scope_check: SCOPE OK. Self-verify command from ${TASK_ID}: PASS."
```

Expected output:

```
https://github.com/$ORG/control-plane/pull/412#issuecomment-2481003377
```

Never write "fixed" or "PASS" in that comment unless you actually ran the command and read its output in this session.

### 10.5 Step 12 — Clean up after merge

Confirm it really merged before deleting anything:

```bash
gh pr view "$PR_URL" --json state,mergedAt,mergeCommit
```

Expected output:

```json
{"mergeCommit":{"oid":"c71fa03e0b2d9d4c5a6e8f1b2c3d4e5f60718293"},"mergedAt":"2026-08-28T04:11:52Z","state":"MERGED"}
```

**STOP rule.** If `state` is anything other than `"MERGED"` — `OPEN`, `CLOSED` — delete nothing. A closed-unmerged PR means your work is not in `integration`; deleting the branch destroys it.

Clean up:

```bash
set -euo pipefail
cd "$WORKDIR"
git fetch origin --prune
git switch integration
git reset --hard origin/integration
git branch -D "$BRANCH"
git push origin --delete "$BRANCH"
git fetch origin --prune
git branch -a | grep -F "$BRANCH" ; echo "exit=$?"
```

Expected output:

```
Switched to branch 'integration'
HEAD is now at c71fa03 Merge pull request #412 from $ORG/lane/1/p1-registry-schema
Deleted branch lane/1/p1-registry-schema (was 8d20c61).
To https://github.com/$ORG/control-plane.git
 - [deleted]         lane/1/p1-registry-schema
exit=1
```

`exit=1` from the final `grep` means the branch is gone locally and remotely. `exit=0` means it still exists — re-run the delete.

**`control-plane-records` exception.** In that repo the ruleset blocks branch deletion (spec §40.1, D107). `git push origin --delete` will be rejected:

```
 ! [remote rejected] lane/4/p2-event-store (protected branch hook declined)
```

That is expected and correct. Delete the local branch, leave the remote branch in place, and say so in your report. Do not attempt to work around the ruleset.

---

## 11. Recovery A — You committed to the wrong branch

**Symptom.** `git rev-parse --abbrev-ref HEAD` printed something that is not `lane/<your lane>/...` — most often `integration`, or the previous task's branch.

**Do not panic-push.** Nothing is broken yet as long as you have not pushed.

### 11.1 Diagnose

```bash
set -euo pipefail
git fetch origin --prune
WRONG="$(git rev-parse --abbrev-ref HEAD)"
echo "Currently on: $WRONG"
git log --oneline "origin/${WRONG}..HEAD" 2>/dev/null || git log --oneline -5
```

Expected output — the commits listed are the ones sitting on the wrong branch:

```
Currently on: integration
4a81f30 L1 p1-registry-schema: add product-record schema and validator
```

Count them. You will move exactly this many.

### 11.2 Case 1 — Not yet pushed (the normal case)

Move the commits to the correct branch and restore the wrong branch to the remote's state.

```bash
set -euo pipefail
git branch "$BRANCH"                      # create the right branch at the current commit
git reset --hard "origin/${WRONG}"        # rewind the wrong branch to the remote
git switch "$BRANCH"                      # move onto the right branch
git branch --unset-upstream 2>/dev/null || true
```

Expected output:

```
HEAD is now at 9c3d1a2 L0 p0: freeze contracts v1
Switched to branch 'lane/1/p1-registry-schema'
```

Verify all four properties:

```bash
set -euo pipefail
git rev-parse --abbrev-ref HEAD
git log --oneline "origin/integration..HEAD"
git diff --stat "origin/${WRONG}" "$WRONG"
scope_check
```

Expected output:

```
lane/1/p1-registry-schema
4a81f30 L1 p1-registry-schema: add product-record schema and validator
SCOPE OK: every changed path is owned by lane 1
```

The `git diff --stat` line prints **nothing** — that is the proof that the wrong branch is now identical to the remote and you left no trace on it. If it prints anything, the wrong branch is still dirty; re-run the `git reset --hard` step.

If `$BRANCH` already existed, `git branch` fails with `fatal: a branch named '...' already exists`. In that case use a cherry-pick instead:

```bash
set -euo pipefail
SHA="$(git rev-parse HEAD)"
git reset --hard "origin/${WRONG}"
git switch "$BRANCH"
git cherry-pick "$SHA"
scope_check
```

Expected output of the cherry-pick:

```
[lane/1/p1-registry-schema 6e9a2d4] L1 p1-registry-schema: add product-record schema and validator
 Date: Thu Aug 27 21:04:11 2026 +0530
 2 files changed, 118 insertions(+)
```

### 11.3 Case 2 — Already pushed to `integration` or `main`

You cannot have. Branch protection blocks direct pushes to `main` and requires a PR for `integration` (spec §11.3), so the push was rejected with:

```
remote: error: GH006: Protected branch update failed for refs/heads/integration.
remote: error: Changes must be made through a pull request.
```

Nothing reached the remote. Use §11.2 Case 1.

### 11.4 Case 3 — Already pushed to another lane's branch

```bash
git log --oneline "origin/${WRONG}"
```

**STOP.** You have written to a branch you do not own. `PARTITION.md`: "A lane NEVER merges another lane's branch. A lane NEVER rebases another lane's branch." You may not force-push it back either — that would destroy that lane's work. Recover your own commits with §11.2 Case 1, then open a blocker (§15) naming the branch and the SHAs you pushed, so L0 can remove them. Do not attempt the removal yourself.

---

## 12. Recovery B — You touched a foreign path

**Symptom.** `scope_check` printed one or more `FOREIGN PATH:` lines, or the CI `lane-guard` check failed on your PR.

### 12.1 Identify

```bash
git fetch origin --prune
scope_check
```

Expected output:

```
FOREIGN PATH: contracts/product.contract.yaml
FOREIGN PATH: reconciler/drift-scan.py
SCOPE FAIL: lane 1 does not own the paths listed above
```

Look each one up in the §1 table so you can name its real owner in your report: `contracts/**` is L0; `reconciler/**` is L3.

### 12.2 Case 1 — Foreign file is only in the working tree (not committed)

```bash
set -euo pipefail
git restore --staged --worktree contracts/product.contract.yaml
git status --porcelain
scope_check
```

Expected output:

```
SCOPE OK: every changed path is owned by lane 1
```

If the foreign file is one you *created* (so `git restore` reports `pathspec ... did not match`), delete it:

```bash
rm -f contracts/product.contract.yaml
git status --porcelain
```

Expected output: nothing.

### 12.3 Case 2 — Foreign file is already committed on your branch

Strip the foreign paths out of your branch's history without disturbing your legitimate work. Rebuild the branch from `integration` and re-apply only your owned changes:

```bash
set -euo pipefail
git fetch origin --prune
git switch "$BRANCH"
git branch "${BRANCH}-backup"                 # safety net — do not delete until you are done
git reset --soft origin/integration           # keep all changes staged, drop the commits
git restore --staged .                        # unstage everything
git status --short
```

Expected output — every change from your branch, now unstaged:

```
 M contracts/product.contract.yaml
?? reconciler/drift-scan.py
?? schemas/registry/product-record.schema.json
?? validators/registry/validate-product-record.py
```

Discard the foreign ones, keep yours:

```bash
set -euo pipefail
git restore --worktree contracts/product.contract.yaml
rm -f reconciler/drift-scan.py
git add schemas/registry/product-record.schema.json
git add validators/registry/validate-product-record.py
git status --short
```

Expected output — only owned paths remain:

```
A  schemas/registry/product-record.schema.json
A  validators/registry/validate-product-record.py
```

Re-commit and verify:

```bash
set -euo pipefail
git commit -m "L${LANE} ${PHASE}-${TASK}: add product-record schema and validator" \
           -m "Task: ${TASK_ID}
Lane: L${LANE}
Paths: schemas/registry/, validators/registry/"
scope_check
```

Expected output:

```
SCOPE OK: every changed path is owned by lane 1
```

If the branch was already pushed, force-push it (§10.2 — all three guards, `--force-with-lease --force-if-includes`). Then remove the safety net:

```bash
git branch -D "${BRANCH}-backup"
```

### 12.4 The part you must not skip

Deleting the foreign file does not delete the fact that you thought it was yours. **Report it.** Two possibilities, and you cannot tell them apart yourself:

- Your task card asked for something the partition does not let your lane do. The card is defective and every other agent given that card will hit the same wall.
- You drifted out of scope because an adjacent problem was visible.

Either way, open a blocker (§15) naming the foreign path, its owning lane from §1, and which of the two you believe it was. This is not a confession, it is data L0 needs.

---

## 13. Recovery C — You pushed a broken commit

**Symptom.** CI is red on your PR, or you notice after pushing that the commit does not build, does not validate, or contains a conflict marker.

**Never** `git push --force` to "clean it up", and **never** silently re-push and hope. The fix is deterministic.

### 13.1 Read the actual failure before touching anything

```bash
gh pr checks "$PR_URL"
```

Expected output:

```
NAME                          DESCRIPTION  ELAPSED  URL
contract-validation           passed       31s      https://github.com/...
lane-guard                    passed       12s      https://github.com/...
registry-validation           failed       44s      https://github.com/...
tests                         passed       1m18s    https://github.com/...
```

```bash
gh run view --log-failed --repo "${ORG}/${REPO}" "$(gh pr checks "$PR_URL" --json name,link -q '.[] | select(.name=="registry-validation") | .link' | sed -E 's#.*/runs/([0-9]+)/job/[0-9]+$#\1#')"
```

Read the log. Do not guess the cause from the check name.

**Rule: you may not report a fix you have not verified locally.** Reproduce the failure on your machine first, using the self-verify command on your task card. If you cannot reproduce it, you cannot fix it — open a blocker (§15).

### 13.2 Case 1 — PR is still draft and nobody has reviewed it

Amend and force-push with lease. This keeps history clean.

```bash
set -euo pipefail
# fix the file, then:
git add schemas/registry/product-record.schema.json
git commit --amend --no-edit
scope_check
git grep -n -E '^(<<<<<<<|=======|>>>>>>>)' -- . ; echo "markers_exit=$?"
git fetch origin --prune
git push --force-with-lease --force-if-includes origin "$BRANCH"
```

Expected output:

```
SCOPE OK: every changed path is owned by lane 1
markers_exit=1
To https://github.com/$ORG/control-plane.git
 + 5b7e4f0...a3f8b21 lane/1/p1-registry-schema -> lane/1/p1-registry-schema (forced update)
```

### 13.3 Case 2 — Anyone has reviewed the PR

Amend is forbidden (§10.1). Add a fix commit:

```bash
set -euo pipefail
git add schemas/registry/product-record.schema.json
git commit -m "L${LANE} ${PHASE}-${TASK}: fix registry-validation failure on retention_class" \
           -m "Task: ${TASK_ID}
Lane: L${LANE}
Paths: schemas/registry/"
scope_check
git push origin "$BRANCH"
```

Expected output — a fast-forward, no `(forced update)`:

```
To https://github.com/$ORG/control-plane.git
   5b7e4f0..a3f8b21  lane/1/p1-registry-schema -> lane/1/p1-registry-schema
```

Then say what happened, in the PR:

```bash
gh pr comment "$PR_URL" --body "registry-validation was failing on retention_class. Reproduced locally with the ${TASK_ID} self-verify command, fixed in a3f8b21, re-ran locally: PASS. Re-requesting checks."
```

### 13.4 Case 3 — The broken commit already merged into `integration`

You do not fix `integration`. It is L0's branch (`PARTITION.md`). You may not revert it, may not push to it, may not open a PR that rewrites it.

Gather the facts and hand them over:

```bash
set -euo pipefail
git fetch origin --prune
git log --oneline -5 origin/integration
gh pr view "$PR_URL" --json number,mergeCommit,mergedAt
```

Then open a blocker (§15) with `severity: blocking`, quoting the merge commit SHA, the failing check name, and the exact reproduction command. The merge train is ordered L1 → L4 → L2 → L3 → L5 and a broken `integration` blocks every lane behind you — report it within the same session you discover it. Do not start your next task first.

### 13.5 What never fixes a broken push

```
git push --force                          # no lease: silently overwrites others' work
git reset --hard && git push --force      # same, with extra steps
git revert <sha> && push to integration   # you do not push to integration
git rebase -i origin/integration          # interactive rewrite; you will drop a commit
git filter-branch / git filter-repo       # never, on any branch, for any reason
git reflog expire --expire=now --all      # destroys the only recovery path you have
```

---

## 14. Forbidden commands

If you are about to type any of these, stop and re-read the section named in the right-hand column. There is no situation on this programme in which these are correct.

| Forbidden | Why | Instead |
|---|---|---|
| `git add .` / `git add -A` / `git commit -a` | Commits foreign paths | Name every path (§7.1) |
| `git push --force` | No lease; overwrites work you cannot see | `--force-with-lease --force-if-includes` (§10.2) |
| `git push origin main` / `... integration` | Protected; you are not L0 | Open a PR (§10.3) |
| `git push --force` on `control-plane-records` | Ruleset, no bypass actor; a rewrite is Blocking drift L5 (spec §40.1, D107) | Plain append push only (§10.2 guard 2) |
| Any push, rebase, or force-push on `lane/<other>/*` | "A lane NEVER rebases another lane's branch" (`PARTITION.md`) | §11.4 |
| `git merge` (any form, on a lane branch) | Lane branches rebase; merges are L0's | `git rebase origin/integration` (§8) |
| `gh pr merge` / `gh pr review` / `gh pr ready` | Machines never merge, approve, or promote (spec §11.3) | Report the PR URL to L0 (§10.3) |
| `git rebase -i` | Interactive rewrite; you will drop a commit and not notice | §13.2 or §13.3 |
| `git filter-branch` / `git filter-repo` | Rewrites history; breaks the anchored SHA chain (spec §40.1, D107) | Open a blocker (§15) |
| `git stash` | Hides work you will forget and report as complete | Commit it (§7) |
| `git checkout --ours` / `--theirs` during a rebase | Silently discards one side of an in-lane conflict | Union resolution (§9.3) |
| `git config --global ...` | Leaks identity into every repo on the machine | `--local` (§5) |
| `git reflog expire` / `git gc --prune=now` | Destroys your only recovery path | Never |
| Editing `contracts/**`, `CODEOWNERS`, `docs/**`, `Makefile`, root files | L0-owned (`PARTITION.md`) | Contract Change Request via blocker (§15) |

---

## 15. The blocker issue — copy-paste verbatim

Open a blocker the moment you hit any STOP rule on this page. A blocker costs L0 five minutes. A guess costs the merge train a cycle.

```bash
set -euo pipefail
gh issue create \
  --repo "${ORG}/control-plane" \
  --title "BLOCKER ${TASK_ID}: <one line, what is blocked>" \
  --label "blocker,lane-${LANE}" \
  --body "Task: ${TASK_ID}
Lane: L${LANE}
Branch: ${BRANCH}
Repo: ${ORG}/${REPO}
PR: ${PR_URL:-none opened}

## What I was doing
<the manual section number and the exact command I ran>

## What I expected
<the expected output printed in that section of 05-git-workflow.md>

## What actually happened
\`\`\`
<paste the command's real output, complete, unedited>
\`\`\`

## Why I stopped instead of continuing
<name the STOP rule: foreign path / ambiguous conflict / stale lease / missing task-card fact / contract change needed>

## What I did NOT do
<explicitly: did not force-push, did not resolve the conflict, did not touch the foreign path, did not merge>

## Decision needed from L0
<the one question you cannot answer yourself>"
```

Expected output:

```
https://github.com/$ORG/control-plane/issues/188
```

Then stop working on this task. Report the issue URL. Do not start an adjacent task to stay busy.

---

## 16. End-of-task checklist

Run this before you report anything. Every line must print `OK`, or you are not done.

```bash
set -euo pipefail
cd "$WORKDIR"
git fetch origin --prune

CUR="$(git rev-parse --abbrev-ref HEAD)"
case "$CUR" in "lane/${LANE}/"*) echo "OK  branch: $CUR" ;; *) echo "NOT OK  branch: $CUR" ;; esac

[ -z "$(git status --porcelain)" ] && echo "OK  tree clean" || echo "NOT OK  tree dirty"

scope_check >/dev/null 2>&1 && echo "OK  scope" || echo "NOT OK  scope — run scope_check and read it"

git grep -q -E '^(<<<<<<<|=======|>>>>>>>)' -- . && echo "NOT OK  conflict markers present" || echo "OK  no conflict markers"

git rev-parse --verify --quiet "origin/${BRANCH}" >/dev/null && echo "OK  branch pushed" || echo "NOT OK  branch not pushed"

[ -z "$(git log --oneline "origin/${BRANCH}..HEAD" 2>/dev/null)" ] && echo "OK  local == remote" || echo "NOT OK  unpushed commits"

git merge-base --is-ancestor origin/integration HEAD && echo "OK  rebased on integration" || echo "NOT OK  rebase onto integration (section 8)"
```

Expected output:

```
OK  branch: lane/1/p1-registry-schema
OK  tree clean
OK  scope
OK  no conflict markers
OK  branch pushed
OK  local == remote
OK  rebased on integration
```

Finally, run the self-verify command printed on your task card and **read its output**. Then report exactly three things and nothing else:

1. The PR URL from §10.3.
2. The literal output of this checklist and of your task card's self-verify command.
3. Anything on the task card's acceptance criteria that you did **not** complete.

If item 3 is non-empty, say so first, in the first sentence. Reporting a test as passing without running it, or a task as complete when it is partial, is the one failure this programme cannot absorb.
