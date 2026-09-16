# 08 — THE FAILURE PLAYBOOK

**Audience:** the AI developer executing one task on one lane branch.
**Authority:** this file tells you what to do when something goes wrong. It does not give you permission to decide anything.
**Governing document:** `PARTITION.md` (FROZEN). Where this file and `PARTITION.md` disagree, `PARTITION.md` wins and you open a blocker (§0.4).

---

## 0. READ THIS SECTION BEFORE ANY OTHER SECTION

### 0.1 The three laws of this playbook

1. **You do not fix what you do not own.** Path ownership is fixed by `PARTITION.md`. A file outside your lane's OWNS list is not yours to touch, even when it is broken, even when the fix is one line, even when fixing it would unblock you. Report it. Do not touch it.
2. **You do not guess.** If two readings of a spec, a task card, or an error message are both plausible, you are blocked. Blocked means STOP and open a blocker issue (§0.4). It does not mean pick one.
3. **You do not report anything you did not run.** Every claim of "passing", "green", "fixed", or "done" must be accompanied by the exact command you ran and the final line of its output. No output, no claim.

### 0.2 Orient yourself — run this first, every time, before diagnosing anything

Do not skip this because you "already know" where you are. You have no memory between tasks.

```bash
set -euo pipefail
set +e
echo "=== ORIENTATION ==="
echo "cwd:         $(pwd)"
echo "repo:        $(git rev-parse --show-toplevel 2>/dev/null || echo 'NOT-A-GIT-REPO')"
echo "remote:      $(git remote get-url origin 2>/dev/null || echo 'NO-ORIGIN')"
echo "branch:      $(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'NO-BRANCH')"
echo "head:        $(git rev-parse --short HEAD 2>/dev/null || echo 'NO-HEAD')"
echo "dirty files: $(git status --porcelain 2>/dev/null | wc -l)"
echo "gh auth:     $(gh auth status >/dev/null 2>&1 && echo OK || echo NOT-AUTHENTICATED)"
echo "=== END ORIENTATION ==="
```

**Read the output literally.**

- `NOT-A-GIT-REPO` → you are in the wrong directory. STOP. Do not `git init`. Report: `ORIENTATION FAILED: not a git repo at <pwd>`.
- `NO-BRANCH`, or branch is `main` or `integration` → you must never work on those. STOP (§10).
- `NOT-AUTHENTICATED` → you cannot open issues or read CI. STOP. Report: `ORIENTATION FAILED: gh not authenticated`. Do not attempt to log in, create tokens, or store credentials.

### 0.3 Establish your lane number — never assume it

Your lane number is the first path segment after `lane/` on your branch. Derive it; do not recall it.

```bash
set -euo pipefail
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
LANE="$(printf '%s\n' "$BRANCH" | sed -n 's|^lane/\([1-5]\)/.*$|\1|p')"
if [ -z "$LANE" ]; then
  echo "LANE: UNRESOLVED (branch '$BRANCH' is not lane/<1-5>/<phase>-<task>) — STOP, see section 11"
else
  echo "LANE: $LANE"
fi
```

Then read your lane's OWNS list from the frozen partition — from the file, not from memory:

```bash
set -euo pipefail
PARTITION="$(git rev-parse --show-toplevel)/implementation/PARTITION.md"
[ -f "$PARTITION" ] || PARTITION="$(find "${CONTROL_PLANE_ROOT:?CONTROL_PLANE_ROOT is not set}" -name PARTITION.md -maxdepth 5 2>/dev/null | head -1)"
if [ -f "$PARTITION" ]; then sed -n '/^| Lane |/,/^## Non-negotiable/p' "$PARTITION"; else echo "PARTITION.md NOT FOUND — STOP, see section 10"; fi
```

If `PARTITION.md` is not found, you are in the wrong repository or the wrong checkout. STOP. Do not reconstruct the ownership table from memory or from this file's copy in §2.2 — that copy is a convenience for the guard script only.

### 0.4 The blocker issue — the single escalation mechanism

Every STOP in this playbook ends in exactly one action: **open a blocker issue, then stop working.** There is no other escalation channel available to you. You do not message people, you do not decide, you do not work around.

Set up the target repository (issues for all lanes live in `control-plane`):

```bash
set -euo pipefail
OWNER="$(gh repo view --json owner -q .owner.login)"
CP_REPO="$OWNER/control-plane"
gh repo view "$CP_REPO" >/dev/null 2>&1 && echo "CP_REPO: $CP_REPO OK" || echo "CP_REPO: $CP_REPO NOT-FOUND — STOP"
```

Write the body to a scratch file **outside the repository** (writing a helper file inside the repo is itself a lane-guard violation — see §0.6):

`````bash
TMP="${TMPDIR:-/tmp}/lanework"; mkdir -p "$TMP"
cat > "$TMP/blocker.md" <<'EOF'
## What I was asked to do
<<FILL: the task card id and one sentence, copied from the task card>>

## Where I stopped
<<FILL: playbook section number, e.g. "08-failure-playbook §4">>

## Symptom (verbatim)
```
<<FILL: paste the exact command and the exact output, unedited>>
```

## Diagnosis I ran and what it returned
```
<<FILL: paste the diagnosis command from the playbook section and its output>>
```

## What I did NOT do
<<FILL: state plainly what you left untouched, e.g. "I did not edit contracts/, I did not touch validators/drift/ (L3-owned)">>

## Decision required from L0
<<FILL: one question, answerable yes/no or by naming a path or a value. Do not propose two options and ask which. Do not propose a design.>>

## Branch and commit
branch: <<FILL: output of `git rev-parse --abbrev-ref HEAD`>>
head:   <<FILL: output of `git rev-parse HEAD`>>
EOF
`````

Before submitting, prove you filled it in. This command must print nothing:

```bash
grep -n '<<FILL' "$TMP/blocker.md" && echo "BLOCKER BODY INCOMPLETE — do not submit" || echo "BLOCKER BODY COMPLETE"
```

Submit:

```bash
set -euo pipefail
gh issue create --repo "$CP_REPO" \
  --title "BLOCKER lane/$LANE: <<FILL: one-line symptom, no more than 80 characters>>" \
  --label "blocker" --label "lane/$LANE" \
  --body-file "$TMP/blocker.md"
```

If a `--label` value does not exist in the repository, `gh` fails with `could not add label`. Do **not** create labels. Re-run without the failing label and say so in your report:

```bash
gh issue create --repo "$CP_REPO" --title "BLOCKER lane/$LANE: <<FILL: one-line symptom>>" --body-file "$TMP/blocker.md"
```

Then **stop**. Do not start another task. Do not attempt a partial delivery. Report the issue URL.

### 0.5 The escalation ladder — who "escalate to" means

| Target | Who / what it is | You reach it by |
| --- | --- | --- |
| **SELF** | No escalation. The playbook section tells you exactly what to do and you do it. | Following the section |
| **L0 INTEGRATOR** | The human lead who owns `main`, `integration`, `contracts/**`, `CODEOWNERS`, `docs/**`, root files, `Makefile` (`PARTITION.md`, lane table) | Blocker issue, label `blocker` |
| **L0 + OWNING LANE** | L0, with the owning lane named in the issue title so L0 can route it. You never contact another lane directly and never open a branch in another lane's prefix. | Blocker issue, labels `blocker`, `cross-lane`, and the owning lane's label if it exists |
| **L0 → escalation role** | The escalation role of the Master Spec, resolved through `topology.yaml`, never named as a person (Spec §66; §17.1). Reached only by L0, never by you. | You never do this. You escalate to L0 and stop. |

**A single blocker issue is the correct output of a failed task.** It is not a failure of your work. Silently delivering half a task is.

### 0.6 Things you are never permitted to do, in any failure

These are absolute. They hold even when a failure appears to require them.

- Edit `contracts/**`, `CODEOWNERS`, `docs/**`, root files, or `Makefile` — L0 owns these (`PARTITION.md`, lane table).
- Edit any path in another lane's OWNS list, for any reason (`PARTITION.md`, rule 1).
- Push to `main` or `integration`, or open a PR from `main`/`integration`.
- Merge or rebase another lane's branch (`PARTITION.md`, branch & merge model).
- Force-push anything other than your own `lane/N/*` branch, and then only with `--force-with-lease`.
- Delete, skip, `xfail`, `@skip`, comment out, or weaken any test or assertion so that a check turns green. Verification is fail-closed by design (Spec §64.2: *"Verification and required status checks — Fail closed — no merge, no promotion"*).
- Use `--no-verify`, `--no-gpg-sign`, or any flag that bypasses a hook or a gate.
- Add a `if:` condition or a path filter to a job that emits a required status check — a `skipped` conclusion on a required context is Blocking drift (Spec §33.2, §53.2 Level 4).
- Create a file or directory anywhere outside your lane's OWNS list, including helper scripts, notes, logs, and scratch files. Scratch goes in `${TMPDIR:-/tmp}/lanework`.
- Invent a file path. If you have not confirmed a path exists with `ls`/`test -f`, you may not reference it as if it does.
- Create a stub, mock, fixture, or placeholder implementation of a contract, schema, or interface you did not find. Absence of a contract is a STOP (§5), not an invitation.

---

## 1. THE SYMPTOM INDEX

Find your symptom. Go to that section. Do not improvise from the table alone — each section carries the exact commands and the STOP rules.

| # | Symptom | First diagnosis command | Action, in one line | Escalate to |
| --- | --- | --- | --- | --- |
| 2 | **Lane-guard check failed** on your PR | `gh pr checks --watch=false` then §2.2 local guard | Revert every out-of-lane file to `origin/integration`; re-push | SELF; **L0** if the file is genuinely required by your task |
| 3 | **Rebase conflict** | `git status --short \| grep '^\(UU\|AA\|DU\|UD\|AU\|UA\)'` | Conflicts inside your OWNS list: resolve, keeping both intents. Any conflict outside it: `git rebase --abort` and STOP | SELF inside your paths; **L0** for any foreign-path conflict |
| 4 | **A test fails that you did not touch** | Re-run the same test at the merge-base in a worktree (§4.2) | Fails at merge-base too → pre-existing, not yours: report, do not fix. Passes at merge-base → yours: fix inside your paths | **L0 + OWNING LANE** if pre-existing |
| 5 | **The contract you need does not exist** | `ls contracts/` and `git log --oneline -- contracts/` | Do not create it, do not stub it. File a Contract Change Request and STOP | **L0 INTEGRATOR** |
| 6 | **Your branch is far behind** | `git rev-list --left-right --count origin/integration...HEAD` | Rebase onto `origin/integration`, re-run acceptance, `--force-with-lease` push | SELF; **L0** if the rebase produces foreign-path conflicts |
| 7 | **You finished but the acceptance command disagrees** | Re-run the acceptance command verbatim from the repo root | The acceptance command is right and you are wrong. Two fix attempts maximum, then STOP | **L0 INTEGRATOR** after two failed attempts |
| 8 | **You realise mid-task you misread the spec** | `git diff --stat $(git merge-base origin/integration HEAD)` | Snapshot the work to a `wip/` branch, reset to the branch point, re-read the task card, restart or STOP | SELF if the correct reading is unambiguous; **L0** otherwise |
| 9 | **Another lane broke your build** | `git log -1 --format='%h %an %s' -- <failing-path>` and map the path to its owner | Do not fix it. Confirm the path is foreign, name the owning lane, STOP | **L0 + OWNING LANE** |
| 10 | **The whole integration branch is red** | `gh run list --branch integration --limit 10` | You never repair `integration`. Establish whether your branch is implicated; hold your PR; report | **L0 INTEGRATOR** |
| 11 | **You cannot tell which lane or task you are on** | §0.2 and §0.3 | STOP immediately. Guessing a lane is the single most expensive error available to you | **L0 INTEGRATOR** |
| 12 | **A required check never reports (PR pending forever)** | `gh pr checks --watch=false` and §12.1 | Do not add a shim job, do not re-run blindly. Report the check name that never reported | **L0 + L2** (workflows are L2-owned) |
| 13 | **You already pushed something out of lane** | `git log --name-only origin/integration..HEAD` | Revert on your own branch with a new commit; never rewrite a branch someone else may have pulled | SELF, then **L0** in your report |

---

## 2. LANE-GUARD CHECK FAILED

### 2.1 What the check means

`PARTITION.md` rule 1: *"One owner per path. No path appears in two lanes. A lane PR touching a foreign path FAILS the lane-guard check. No exceptions."* The check is not advisory and it is not a lint. It has caught a real ownership violation. Your job is to remove the violation, not to argue with it.

### 2.2 Diagnose — reproduce the guard locally

```bash
set -euo pipefail
set +e
git fetch origin integration --quiet
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
LANE="$(printf '%s\n' "$BRANCH" | sed -n 's|^lane/\([1-5]\)/.*$|\1|p')"
case "$LANE" in
  1) ALLOW='^(schemas/registry/|schemas/product/|registries/|validators/registry/)' ;;
  2) ALLOW='^(\.github/workflows/|templates/workflows/|tools/evidence/)' ;;
  3) ALLOW='^(reconciler/|tools/provision/|validators/drift/)' ;;
  4) ALLOW='^(schemas/records/|metrics/|tools/records/)' ;;
  5) ALLOW='^(access/|infra/|ops-vm/|notify/|assets/)' ;;
  *) echo "LANE-GUARD LOCAL: FAIL — lane unresolved from branch '$BRANCH'"; ALLOW='' ;;
esac
if [ -n "$ALLOW" ]; then
  VIOL="$(git diff --name-only origin/integration...HEAD | grep -Ev "$ALLOW")"
  if [ -z "$VIOL" ]; then
    echo "LANE-GUARD LOCAL: PASS"
  else
    echo "LANE-GUARD LOCAL: FAIL — out-of-lane files:"; printf '%s\n' "$VIOL"
  fi
fi
```

Two things about this snippet you must not get wrong:

- The allow-lists above are transcribed from the frozen lane table. **Confirm them against `PARTITION.md` (§0.3) before trusting them.** If they differ, `PARTITION.md` is correct and this file is stale — open a blocker.
- In the `control-plane-records` repository, lane 4 owns **all** of it (`PARTITION.md`, lane table). The lane-4 pattern above applies to `control-plane` only. If `git remote get-url origin` ends in `control-plane-records` and you are lane 4, the local guard does not apply; every path is yours.

Also read what CI itself said, so you use the real check name rather than an assumed one:

```bash
gh pr checks --watch=false
gh pr checks --watch=false | grep -i 'lane' || echo "no check with 'lane' in the name — read the full list above"
```

### 2.3 Act

For each out-of-lane file, restore it to `origin/integration`'s version and commit the restoration:

```bash
set -euo pipefail
git checkout origin/integration -- "<<FILL: exact path from the FAIL list, one per invocation>>"
git status --short
git commit -m "revert out-of-lane change to <<FILL: same path>>"
```

If the file was **created** by you and does not exist on `integration`, `git checkout` fails with `pathspec did not match`. Delete it instead:

```bash
git rm -f "<<FILL: exact path>>"
git commit -m "remove out-of-lane file <<FILL: same path>>"
```

Re-run §2.2. It must print `LANE-GUARD LOCAL: PASS` before you push:

```bash
git push --force-with-lease origin "$(git rev-parse --abbrev-ref HEAD)"
gh pr checks --watch=false
```

### 2.4 STOP rule

If the out-of-lane file is one your task **genuinely requires** — the task cannot be completed without changing it — then the task card is wrong, not the guard. Revert the file anyway (so your branch is clean), then STOP and open a blocker (§0.4) whose *Decision required* is exactly: `Task <id> requires a change to <path>, which lane <N> owns. Which lane should carry this, or should the task be re-scoped?`

**Escalate to:** SELF for the revert. **L0 INTEGRATOR** for the re-scope decision.

---

## 3. REBASE CONFLICT

### 3.1 Diagnose

```bash
git status --short | grep -E '^(UU|AA|DU|UD|AU|UA)' || echo "NO CONFLICTED FILES"
git diff --name-only --diff-filter=U
```

Then classify every conflicted path against your OWNS list, using the same allow-list as §2.2:

```bash
set -euo pipefail
ALLOW="${ALLOW:?ERROR: ALLOW must be set to the allowed-paths pattern}"
if [ -n "$ALLOW" ]; then
  git diff --name-only --diff-filter=U | grep -Ev "$ALLOW" && echo "FOREIGN-PATH CONFLICT — abort, see 3.4" || echo "ALL CONFLICTS ARE IN YOUR OWNED PATHS"
else
  git diff --name-only --diff-filter=U | grep -Ev "^$" && echo "FOREIGN-PATH CONFLICT — abort, see 3.4" || echo "ALL CONFLICTS ARE IN YOUR OWNED PATHS"
fi
```

### 3.2 Which side is which — read this before resolving

During a **rebase**, the sides are inverted relative to a merge, and getting this backwards silently discards your work:

- `--ours` = the branch you are rebasing **onto** (`integration`). It is *not* yours.
- `--theirs` = **your** commit being replayed.

Never use `git checkout --ours`/`--theirs` reflexively. In a lane build, a conflict inside your own paths almost always means both intents must survive — open the file, keep both, delete the `<<<<<<<`, `=======`, `>>>>>>>` markers by hand.

Prove no markers survive before continuing. This must print nothing:

```bash
git diff --name-only --diff-filter=U | xargs -r grep -nE '^(<<<<<<<|=======|>>>>>>>)' && echo "MARKERS REMAIN — do not continue" || echo "NO CONFLICT MARKERS"
```

### 3.3 Act (conflicts inside your owned paths only)

```bash
git add "<<FILL: each resolved path>>"
git rebase --continue
```

Then re-run your task's acceptance command **in full** (§7). A rebase that compiles is not a rebase that is correct.

### 3.4 STOP rule — any foreign-path conflict

A conflict in a path your lane does not own means one of: you edited a foreign path (§2), you are rebasing onto the wrong ref, or two lanes have been given the same path — which `PARTITION.md` rule 1 forbids and which only L0 can resolve.

```bash
set -euo pipefail
git rebase --abort
git status --short
git rev-parse --abbrev-ref HEAD
```

Then open a blocker (§0.4). *Decision required:* `Rebase of <branch> onto origin/integration conflicts in <path>, owned by lane <N>. Which lane's version stands?`

**Escalate to:** SELF inside your paths. **L0 INTEGRATOR** for any foreign-path conflict.

---

## 4. A TEST FAILS THAT YOU DID NOT TOUCH

### 4.1 The only question that matters

Did this test already fail before your branch existed? Answer it with a command, not with reasoning about your diff.

### 4.2 Diagnose — run the same test at the merge-base, in a throwaway worktree

A worktree leaves your working directory untouched. Do not use `git stash` for this; a lost stash is a lost task.

```bash
set -euo pipefail
set +e
git fetch origin integration --quiet
BASE="$(git merge-base origin/integration HEAD)"
TMP="${TMPDIR:-/tmp}/lanework"; mkdir -p "$TMP"
rm -rf "$TMP/basecheck"
git worktree add --detach "$TMP/basecheck" "$BASE" && echo "BASE WORKTREE AT $TMP/basecheck ($BASE)"
```

```bash
cd "$TMP/basecheck" && <<FILL: the exact failing test command, copied character-for-character from your task card or from the CI log>> ; echo "BASE EXIT CODE: $?"
```

Clean up when you are done — always, even on failure:

```bash
git worktree remove --force "${TMPDIR:-/tmp}/lanework/basecheck"
git worktree list
```

### 4.3 Act — decide from the exit code, not from the message

| `BASE EXIT CODE` | Meaning | Action |
| --- | --- | --- |
| non-zero (fails at base too) | **Pre-existing failure. Not caused by you.** | Do not fix it. Do not touch the test. Continue your own task only if your acceptance command is unaffected; otherwise STOP. Report the failure with both exit codes. |
| zero (passes at base, fails on your branch) | **You caused it**, even if the failing file is not one you edited. | Fix it — but only by changing files inside your OWNS list. If the only possible fix is outside your paths, STOP (§9). |

### 4.4 STOP rule

If the pre-existing failure blocks your acceptance command, you cannot complete the task and you must not "route around" it. Open a blocker with both exit codes and the owning lane of the failing file (derive it with §9.2).

**Escalate to:** **L0 + OWNING LANE** when pre-existing. SELF when your branch caused it and the fix is inside your paths.

---

## 5. THE CONTRACT YOU NEED DOES NOT EXIST

### 5.1 Confirm the absence — do not conclude it from a failed import

```bash
set -euo pipefail
git rev-parse --show-toplevel
ls -la contracts/ 2>/dev/null || echo "contracts/ DOES NOT EXIST IN THIS REPO"
find contracts -type f 2>/dev/null | sort
git log --oneline -n 20 -- contracts/ 2>/dev/null || echo "no history for contracts/"
```

Search by name before declaring anything missing — a plausible-looking path you invented is the most common way this failure is misdiagnosed:

```bash
git ls-files | grep -iE '<<FILL: the contract name or symbol you need, e.g. "record-envelope" or "ProductContract">>' || echo "NO MATCH IN TRACKED FILES"
git fetch origin integration --quiet && git ls-tree -r --name-only origin/integration | grep -iE '<<FILL: same search term>>' || echo "NO MATCH ON origin/integration"
```

If `NO MATCH` on both, the contract genuinely does not exist yet.

### 5.2 Act — file a Contract Change Request, then stop

`PARTITION.md` rule 2 is explicit: *"`contracts/**` is written by L0 in Phase 0 and FROZEN. Lanes code against it and against generated stubs/fixtures. A lane needing a contract change files a Contract Change Request; it never edits `contracts/**`."*

**You may not:** create the contract, stub it in your own paths, define the shape "temporarily", infer the shape from another lane's source (rule 4 forbids cross-lane imports), or proceed with a placeholder and a `TODO`.

```bash
set -euo pipefail
TMP="${TMPDIR:-/tmp}/lanework"; mkdir -p "$TMP"
cat > "$TMP/ccr.md" <<'EOF'
## Contract requested
path: contracts/<<FILL: the exact path you expect, as your task card names it>>

## Task that is blocked
<<FILL: task card id, and the one sentence of the task that needs this contract>>

## Why an existing contract does not serve
<<FILL: paste the output of the two `git ls-files | grep` searches from §5.1>>

## Fields/behaviour the blocked task reads
<<FILL: list only what your task consumes. Do NOT propose a schema, a file format, or a design. List the questions your code must be able to answer.>>

## Consumers I know of
lane <<FILL: your lane number>> only, as far as I can see. I have not inspected other lanes' source (PARTITION rule 4).

## Branch
<<FILL: output of `git rev-parse --abbrev-ref HEAD`>>
EOF
grep -n '<<FILL' "$TMP/ccr.md" && echo "CCR INCOMPLETE — do not submit" || echo "CCR COMPLETE"
```

```bash
set -euo pipefail
OWNER="$(gh repo view --json owner -q .owner.login)"
gh issue create --repo "$OWNER/control-plane" \
  --title "CCR lane/$LANE: contracts/<<FILL: path>> does not exist" \
  --label "contract-change-request" --label "blocker" --label "lane/$LANE" \
  --body-file "${TMPDIR:-/tmp}/lanework/ccr.md"
```

Then stop. Do not start the next task on your own initiative.

**Escalate to:** **L0 INTEGRATOR**.

---

## 6. YOUR BRANCH IS FAR BEHIND

### 6.1 Diagnose — measure it

```bash
git fetch origin integration --quiet
git rev-list --left-right --count origin/integration...HEAD
```

Output is two numbers, tab-separated: **behind** (commits on `integration` you do not have) then **ahead** (your own commits). Read them in that order — reversing them is a classic silent error.

```bash
set -euo pipefail
git fetch origin integration --quiet
BEHIND="$(git rev-list --count HEAD..origin/integration)"
AHEAD="$(git rev-list --count origin/integration..HEAD)"
echo "BEHIND: $BEHIND   AHEAD: $AHEAD"
git log --oneline HEAD..origin/integration | head -n 20
```

### 6.2 Act — rebase, never merge

`PARTITION.md` branch model: lane branches are *"short-lived (< 1 day), rebased on `integration` before PR"*. Do not `git merge origin/integration` into your lane branch; it produces a merge commit the merge train does not expect.

```bash
set -euo pipefail
if git status --porcelain | grep -q .; then
  echo "WORKING TREE DIRTY — commit first, do not rebase"
else
  echo "CLEAN — safe to rebase"
  git rebase origin/integration
fi
```

Conflicts → §3. Then, mandatory, in this order:

```bash
# 1. lane guard still passes
# (re-run the §2.2 block; it must print LANE-GUARD LOCAL: PASS)
# 2. acceptance command still passes
<<FILL: your task's exact acceptance command>> ; echo "ACCEPTANCE EXIT CODE: $?"
# 3. only then push
git push --force-with-lease origin "$(git rev-parse --abbrev-ref HEAD)"
```

`--force-with-lease`, never `--force`. If it is rejected with `stale info`, someone else has written to your branch — STOP and report; do not retry with `--force`.

### 6.3 STOP rule

If `AHEAD` is 0 and `BEHIND` is large, you have no work on this branch — you are probably on the wrong branch (§11). If the rebase replays more than a handful of commits and conflicts repeatedly, abort and report rather than resolving the same file five times:

```bash
git rebase --abort
echo "REBASE ABORTED — branch left unchanged at $(git rev-parse --short HEAD)"
```

**Escalate to:** SELF for a clean rebase. **L0 INTEGRATOR** if the rebase cannot be completed without touching foreign paths.

---

## 7. YOU FINISHED BUT THE ACCEPTANCE COMMAND DISAGREES

### 7.1 The rule

**The acceptance command defines "done". Your belief does not.** If the command fails, the task is not done — regardless of how complete the code looks, how sensible the diff is, or how confident you are.

You may not: edit the acceptance command, edit the test it runs, relax an assertion, add a skip, change an expected value to the observed value, wrap it in `|| true`, or report "passes locally with a minor adjustment".

### 7.2 Diagnose — run it verbatim, from the repo root, with the exit code visible

```bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
<<FILL: the acceptance command, copied character-for-character from the task card — no added flags, no changed paths>>
echo "ACCEPTANCE EXIT CODE: $?"
```

Before doing anything else, rule out the three cheap causes:

```bash
set -euo pipefail
# a) uncommitted or untracked work the command cannot see
git status --short
# b) stale build/test artefacts
git clean -nd            # DRY RUN: lists what would be removed. Read it. Never run `git clean -fdx` blindly.
# c) you are not at the repo root
pwd; git rev-parse --show-toplevel
```

### 7.3 Act — the two-attempt limit

1. **Attempt 1.** Read the failure output and fix the cause inside your OWNS list. Re-run §7.2 in full. Do not re-run a narrowed subset and infer the rest.
2. **Attempt 2.** Same. Only if the second failure has a *different* cause than the first.
3. **STOP.** After two failed attempts, or immediately if the second failure is identical to the first, you stop. Continuing past this point is how a scoped task becomes an unreviewable diff.

Before stopping, capture the evidence:

```bash
set -euo pipefail
TMP="${TMPDIR:-/tmp}/lanework"; mkdir -p "$TMP"
{ cd "$(git rev-parse --show-toplevel)"; <<FILL: the acceptance command>> ; echo "EXIT: $?"; } > "$TMP/acceptance.log" 2>&1
tail -n 40 "$TMP/acceptance.log"
```

Attach the tail to the blocker (§0.4). *Decision required:* `Task <id>'s acceptance command <cmd> fails with <one-line cause> after two fix attempts. Is the acceptance command correct, or is the task under-specified?`

### 7.4 The reverse case — it passes and you did not finish

If the acceptance command passes but you know you left part of the task undone, **say so explicitly in your report and do not mark the task complete.** A passing check on an incomplete task is a false green, and a false green is worse than a red (Spec §64.2: a stale signal presented as current is worse than an absent one).

**Escalate to:** **L0 INTEGRATOR** after two attempts.

---

## 8. YOU REALISE MID-TASK YOU MISREAD THE SPEC

### 8.1 Act immediately — do not "finish this bit first"

The moment you notice, stop editing. Work built on a misreading gets more expensive with every commit.

### 8.2 Preserve what you have — snapshot before you reset anything

```bash
set -euo pipefail
SNAP="wip/misread-$(date +%Y%m%d-%H%M%S)"
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
LANE="$(printf '%s\n' "$BRANCH" | sed -n 's|^lane/\([1-5]\)/.*$|\1|p')"
# Stage only paths inside your lane's OWNS list (PARTITION.md rule 5: additive-only
# within a lane). Never `git add -A` here — it stages foreign paths too, and if the
# misreading caused any out-of-lane writes this would bake them into the snapshot
# branch's history before §8.5 ever gets to reverting them via §2.3.
case "$LANE" in
  1) git add -A -- schemas/registry/ schemas/product/ registries/ validators/registry/ ;;
  2) git add -A -- .github/workflows/ templates/workflows/ tools/evidence/ ;;
  3) git add -A -- reconciler/ tools/provision/ validators/drift/ ;;
  4) git add -A -- schemas/records/ metrics/ tools/records/ ;;
  5) git add -A -- access/ infra/ ops-vm/ notify/ assets/ ;;
  *) echo "LANE UNRESOLVED — do not add or commit, STOP (see section 11)"; exit 1 ;;
esac
git commit -m "WIP snapshot before misread reset" || echo "nothing to commit"
git branch "$SNAP"
echo "SNAPSHOT BRANCH: $SNAP  at $(git rev-parse --short "$SNAP")"
```

Never delete this branch, and never `git reset --hard` before it exists.

### 8.3 Diagnose — see exactly what the misreading produced

```bash
set -euo pipefail
git fetch origin integration --quiet
BASE="$(git merge-base origin/integration HEAD)"
echo "BRANCH POINT: $BASE"
git diff --stat "$BASE"
git diff --name-only "$BASE"
```

### 8.4 Act

**If the correct reading is unambiguous** — the task card or the frozen spec says one thing plainly and you did another:

```bash
set -euo pipefail
git reset --hard "$(git merge-base origin/integration HEAD)"
git status --short
git log --oneline -n 3
```

Re-read the task card and the cited spec section **in full** before writing a line. Then redo the task. Your snapshot branch still holds the discarded work if any of it is reusable.

**If the correct reading is not unambiguous** — you can construct two readings and the task card does not settle it — this is `PARTITION.md`'s AI-developer rule: *"No task may require designing, choosing, or interpreting. If a task needs judgment, it belongs to L0."* Do not reset, do not continue. Open a blocker (§0.4) with both readings stated in one sentence each and *Decision required:* `Task <id>, line "<quoted text>": reading A is <...>, reading B is <...>. Which applies?`

### 8.5 STOP rule

If the misreading caused you to write files **outside your OWNS list**, handle that first via §2.3 (revert them), then apply this section.

**Escalate to:** SELF when the correct reading is unambiguous. **L0 INTEGRATOR** whenever two readings survive.

---

## 9. ANOTHER LANE BROKE YOUR BUILD

### 9.1 Confirm the breakage is not yours (do this before accusing anything)

Run §4.2. If the failure reproduces at the merge-base, it arrived from `integration`, not from you.

### 9.2 Diagnose — identify the owning lane of the failing path

```bash
set -euo pipefail
FAILPATH="<<FILL: the exact path from the failure output — a file that exists; confirm with `test -f`>>"
test -f "$FAILPATH" && echo "PATH EXISTS" || echo "PATH DOES NOT EXIST — you have the wrong path, re-read the failure output"
git log -n 3 --format='%h %an %ad %s' --date=short -- "$FAILPATH"
git log -n 5 --format='%h %d %s' origin/integration -- "$FAILPATH"
```

Map the path to its lane using the table you printed in §0.3. State the mapping explicitly in your report — for example: *"`validators/drift/x.py` is under `validators/drift/**`, owned by L3."*

### 9.3 Act — you do not fix it

`PARTITION.md` rule 1 admits no exception, and rule 4 forbids reaching into another lane's source tree. A one-line fix in a foreign path is still a lane-guard failure, still bypasses that lane's owner, and still risks re-implementing work that lane already has in flight.

- Do **not** patch the file.
- Do **not** work around it by copying its logic into your own paths — that is the "re-implementing something another lane already owns" failure, and it survives review far too often.
- Do **not** pin, vendor, or shim the other lane's output.

Open a blocker (§0.4) with labels `blocker` and `cross-lane`, title `BLOCKER lane/<yours>: build broken by lane/<theirs> change in <path>`, and *Decision required:* `<path> (lane <theirs>) breaks lane <yours>'s build at <commit>. Should lane <theirs> revert, or should lane <yours> hold?`

Then stop, and leave your branch exactly as it is so L0 can reproduce.

**Escalate to:** **L0 + OWNING LANE**.

---

## 10. THE WHOLE INTEGRATION BRANCH IS RED

### 10.1 The rule

`integration` is L0's branch (`PARTITION.md`, lane table: L0 owns `main`, `integration`). **You never push to it, never revert on it, never re-run its jobs as a fix, and never merge into it outside the merge train.** Your entire role in this failure is to find out whether your branch is implicated and to say so accurately.

### 10.2 Diagnose

```bash
gh run list --branch integration --limit 10
gh run view "$(gh run list --branch integration --limit 1 --json databaseId -q '.[0].databaseId')" --log-failed | tail -n 60
```

Find the last known-good commit on `integration`:

```bash
gh run list --branch integration --limit 30 --json conclusion,headSha,createdAt,workflowName \
  -q '.[] | select(.conclusion=="success") | "\(.createdAt) \(.headSha[0:8]) \(.workflowName)"' | head -n 5
```

Establish whether your own work is in the red commit range:

```bash
set -euo pipefail
git fetch origin integration --quiet
git log --oneline "$(git rev-parse HEAD)..origin/integration" | head -n 20
git branch --contains "$(git rev-parse HEAD)" -r | grep -x '  origin/integration' && echo "YOUR HEAD IS MERGED INTO integration" || echo "YOUR HEAD IS NOT IN integration"
```

### 10.3 Act

| Finding | Action |
| --- | --- |
| Your head is **not** in `integration` | You did not cause it. Hold your PR — do not merge into a red `integration`, do not rebase onto a red commit hoping it clears. Report and wait. |
| Your head **is** in `integration` and the failure is in a path you own | Do not fix it on `integration`. Open a **new** `lane/<N>/fix-<short-name>` branch off the last green commit, fix it there, and tell L0 the branch name in your report. Do not merge it yourself. |
| Your head **is** in `integration` and the failure is in a foreign path | §9. Report only. |

```bash
# Only for the middle row. Replace <GREEN_SHA> with a sha printed by the §10.2 "last known-good" command.
git fetch origin integration --quiet
git checkout -b "lane/$LANE/fix-<<FILL: 2-4 word slug>>" "<<FILL: GREEN_SHA>>"
```

### 10.4 STOP rule

If more than one lane's paths appear in the failure, or if the failure is in `contracts/**`, `CODEOWNERS`, `Makefile`, or a root file, stop at diagnosis. That is L0's to unwind, and a second agent poking at it makes the unwinding harder.

**Escalate to:** **L0 INTEGRATOR**, always, for anything on `integration`.

---

## 11. YOU CANNOT TELL WHICH LANE OR TASK YOU ARE ON

This is the highest-severity condition in this playbook, because every other action becomes an ownership violation.

### 11.1 Diagnose

Run §0.2 and §0.3. Then:

```bash
set -euo pipefail
git rev-parse --abbrev-ref HEAD
git log --oneline -n 5
git remote -v
```

### 11.2 Act

- Branch matches `lane/[1-5]/<phase>-<task>` → your lane is that digit. Proceed.
- Branch is `main`, `integration`, `HEAD` (detached), or anything else → **STOP.** Do not create a lane branch by guessing a number. Do not infer your lane from the files that happen to be modified. Do not infer it from the task's subject matter.

Open a blocker (§0.4) titled `BLOCKER: lane unresolved on branch <branch>` with *Decision required:* `Which lane and which task card does this working copy belong to?` Use label `blocker` only (you cannot know which `lane/N` label applies).

**Escalate to:** **L0 INTEGRATOR**.

---

## 12. A REQUIRED CHECK NEVER REPORTS (PR PENDING FOREVER)

### 12.1 Diagnose

```bash
gh pr checks --watch=false
gh pr view --json statusCheckRollup -q '.statusCheckRollup[] | "\(.name)\t\(.status)\t\(.conclusion)"'
```

A check listed as required but showing an empty or `null` conclusion never ran. A check showing `SKIPPED` or `NEUTRAL` on a required context is **Blocking drift** under Spec §33.2 and §53.2 Level 4 — *"A `skipped` or `neutral` conclusion on a required context of a merged pull request is Blocking drift."*

### 12.2 Act

- Do **not** add a shim job, an `if:` condition, or a path filter to make it report. Spec §33.2 forbids exactly this: *"Every required check name is therefore emitted by a job carrying no `if:` and no path filter."*
- Do **not** ask for the check to be removed from branch protection.
- Do **not** merge, and do not report the PR as green.
- Workflows live in `.github/workflows/**`, owned by **L2**. If you are not L2, you may not touch them at all.

Re-run once, in case of an infrastructure blip, and record the result:

```bash
gh run rerun "$(gh run list --branch "$(git rev-parse --abbrev-ref HEAD)" --limit 1 --json databaseId -q '.[0].databaseId')" --failed
gh pr checks --watch=false
```

If it still does not report, open a blocker with labels `blocker` and `cross-lane`, naming the exact check name string.

**Escalate to:** **L0 + L2**.

---

## 13. YOU ALREADY PUSHED SOMETHING OUT OF LANE

### 13.1 Diagnose

```bash
git fetch origin integration --quiet
git log --name-only --format='--- %h %s' origin/integration..HEAD
```

Run the §2.2 guard block to get the definitive violation list.

### 13.2 Act

Your branch is `lane/N/*` and short-lived, so history rewriting is normally safe — **but only if no one else has pulled it.** You cannot know that. Prefer a forward revert:

```bash
set -euo pipefail
git checkout origin/integration -- "<<FILL: exact out-of-lane path>>"   # or `git rm -f` if it is a file you created
git commit -m "revert out-of-lane change to <<FILL: same path>>"
git push origin "$(git rev-parse --abbrev-ref HEAD)"
```

Re-verify, then report the violation in your final report even though you fixed it — an ownership violation that reached a remote is information L0 needs, not a private embarrassment to clean up quietly:

```bash
# re-run §2.2 — must print LANE-GUARD LOCAL: PASS
gh pr checks --watch=false
```

### 13.3 STOP rule

If the out-of-lane commit reached `integration` or `main`, you do not touch it. §10, report only.

**Escalate to:** SELF for the revert on your own branch; **L0 INTEGRATOR** in the report.

---

## 14. WHAT YOUR FINAL REPORT MUST CONTAIN

Every task ends with a report, whether it succeeded or stopped. Copy this template verbatim and fill it. An empty section is a lie by omission; write `none` explicitly.

```text
TASK:            <task card id>
BRANCH:          <output of `git rev-parse --abbrev-ref HEAD`>
HEAD:            <output of `git rev-parse HEAD`>
OUTCOME:         COMPLETE | STOPPED-BLOCKED | PARTIAL-REVERTED

LANE GUARD:      <the literal line printed by §2.2 — "LANE-GUARD LOCAL: PASS" or the FAIL list>
ACCEPTANCE CMD:  <the exact command, character-for-character>
ACCEPTANCE EXIT: <the integer exit code you observed>
ACCEPTANCE TAIL: <the last line of its output, verbatim>

FILES CHANGED:   <output of `git diff --name-only origin/integration...HEAD`>
FILES I DID NOT TOUCH BUT NOTICED WERE BROKEN: <paths + owning lane, or "none">

BLOCKER ISSUE:   <url, or "none">
SNAPSHOT BRANCH: <wip/... name if §8 was used, or "none">
ASSUMPTIONS I MADE: <must be "none". If it is not "none", you should have opened a blocker instead.>
```

**`OUTCOME: COMPLETE` is only permitted when all three are true:** the lane guard printed `PASS`, the acceptance command exited `0` and you pasted its tail, and `ASSUMPTIONS I MADE` is `none`. If any one of those fails, the outcome is `STOPPED-BLOCKED`.

---

## 15. THE FOUR SENTENCES TO REMEMBER

1. A path you do not own is not yours to fix, however small the fix.
2. An ambiguity is a STOP, never a choice.
3. A test you did not run is a test that failed.
4. One well-written blocker issue is a successful outcome; a quiet partial delivery is not.

---

### Citations

- `implementation/PARTITION.md` — lane table and OWNS lists; non-negotiable anti-conflict rules 1–5; branch & merge model; merge train order L1 → L4 → L2 → L3 → L5; AI developer profile.
- Master Spec v4.0 §26.1 — Gate 1 / Gate 2; approval is not a verification activity.
- Master Spec v4.0 §26.2 — automated verification in CI is a verification activity: failure blocks progress.
- Master Spec v4.0 §30.2 — plan-checker hard rejects, including tasks lacking an automated verify command and references to symbols that do not exist in source.
- Master Spec v4.0 §33.2 — every required check name is emitted by a job carrying no `if:` and no path filter; a `skipped` or `neutral` conclusion on a required context is Blocking drift.
- Master Spec v4.0 §53.2 — reconciliation Level 4 (Block) and Level 5 (Escalate).
- Master Spec v4.0 §64.1 — safe defaults: where a value is missing or malformed, the resolution is denial, not a default that permits.
- Master Spec v4.0 §64.2 — fail-closed classification: verification and required status checks fail closed, no merge, no promotion.
- Master Spec v4.0 §17.1, §66 — the escalation role is declared as a role and resolved through `topology.yaml`, never named as a person.
