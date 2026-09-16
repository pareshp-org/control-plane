# 07 — Rollback and Recovery

**Scope: the build, not the product.** This file governs recovery of the five-lane parallel build itself — the `lane/N/*` branches, `integration`, and `main` in `control-plane` and `control-plane-records`. It does not govern production rollback of a live product; that is Section 28.1, Section 42.3 and `restore-production.yml` (AT-103).

**Who executes this file.** L0 Integrator executes every procedure that touches `integration` or `main`. A lane developer executes only §R3 (recovering their own lane branch) and §R5.3 (re-landing their own reverted work). A lane developer who believes `integration` needs a revert does not perform one — they raise the STOP in §9 and hand it to L0. Per PARTITION line 36: *a lane NEVER merges another lane's branch, a lane NEVER rebases another lane's branch.*

**Why this file exists.** Five low-cost AI developers build in parallel and none of them holds full context. The recovery path is the only thing standing between one lane's wrong build and four other lanes rebasing onto it. Invariant 82 binds this file explicitly: changes to this specification *and its enforcing tooling* follow the platform-change process — versioned, canaried, reversible. The build pipeline is enforcing tooling. It gets a tested rollback like everything else (AT-026: "per-stage verification at each step and a working, tested rollback").

**The principle this file is built on.** A check that can only pass is not a check. Section 53.1's seeded canary makes a zero-finding reconciliation run a FAILED run; AT-102 makes that a test; EC-109 names the failure mode. The same rule applies to every gate below: a revert that was never proven to fix a red gate is not a proven revert, and a rollback procedure that has never been executed is a hypothesis (§8 is where this is discharged). Invariant 3 states the general form — an untested backup is treated as no backup.

---

## 0. The sixty-second version

Read this table. Then read the one section it points at. Do not read the whole file during an incident.

| Symptom | Section | First command |
|---|---|---|
| `integration` gate went red after a lane merge | §R1 | `git log --first-parent --oneline integration -10` |
| `main` gate went red after promotion from `integration` | §R2 | `git log --first-parent --oneline main -5` |
| A lane branch will not rebase; hundreds of commits behind | §R3 | `git rev-list --left-right --count integration...lane/N/<task>` |
| Three or more lanes failed in the same cycle | §R4 | `git log --oneline -10 -- contracts/` |
| You reverted something and now need it back | §R5 | `git log --grep='^Revert' --oneline integration -20` |
| You want to force-push, reset, or rewrite history | §7 | **Stop. You do not.** |
| You want to roll back `control-plane-records` | §7.2 | **Stop. You append a correction.** |
| Nothing here matches | §9 | Open a blocker issue. Freeze the train. |

---

## 1. Standing preconditions

Run this block before **every** procedure in this file. It costs four seconds and it is the difference between reverting the right commit and reverting yesterday's.

```bash
set -euo pipefail
export CP="$HOME/src/control-plane"
export CPR="$HOME/src/control-plane-records"
# The seeded reconciliation canary (Section 53.1). REG-028 resolved this to a
# labelled row in the L1-owned canary registry (FD-106; lanes/L3-03-canary-and-integrity.md:426).
export CANARY_PATH="contracts/registry/canary.v1.yaml"

cd "$CP"
git fetch --all --prune --tags
git status --porcelain
```

**Expected output** — an empty line after `git status --porcelain`. Nothing else.

(`git fetch --all --prune --tags` above prints its own progress to stderr, e.g. `Fetching origin` — that is normal fetch chatter, not the output this check is asking about.)

If `git status --porcelain` prints anything, you have uncommitted work in the recovery clone. **STOP.** Stash it (`git stash push -m "pre-recovery $(date -u +%FT%TZ)"`) or use a clean clone. Recovering with a dirty tree is how a lane's half-finished file ends up on `integration`.

### 1.1 Three rules that never bend

1. **Never `git push --force` or `--force-with-lease` to `integration` or `main`.** Both are protected; the push will be rejected (Section 11.3: *block force pushes and deletions on the default branch*), and if it somehow succeeds you have destroyed history that invariant 47 and Section 63.1 require to be append-only. Recovery is always a **new commit that undoes** — `git revert` — never a rewrite. **The one named carve-out** is the §8.2 force-push-rejection drill, whose entire purpose is to attempt exactly this — it runs only under §8.2's own safety contract (saved-SHA capture before the attempt, and an immediate restore-and-verify after), never as a bare `git push --force`.
2. **Never rewrite `control-plane-records`.** Its ruleset blocks force push, branch deletion and tag deletion with **no bypass actor** (D107, PARTITION line 8). The reconciler anchors the records head SHA into the protected control-plane repository on every run; a head that does not descend from the last anchor is proof of rewriting and is Level 5 — an incident, not a mistake (Section 53.2). See §7.2.
3. **Never revert on behalf of a lane you do not own without telling that lane.** The lane will keep building on a branch whose base has changed underneath it. Notification is a step in every procedure below, not a courtesy.

### 1.2 Lane-of-path lookup

Under pressure you will need to know which lane owns a changed path. This is the PARTITION table as a command. Save it; do not re-derive it.

```bash
set -euo pipefail
lane_of() {
  case "$1" in
    schemas/registry/*|schemas/product/*|registries/*|validators/registry/*) echo "L1" ;;
    .github/workflows/*|templates/workflows/*|tools/evidence/*)              echo "L2" ;;
    reconciler/*|tools/provision/*|validators/drift/*)                       echo "L3" ;;
    schemas/records/*|metrics/*|tools/records/*|records/*|events/*)         echo "L4" ;;
    access/*|infra/*|ops-vm/*|notify/*|assets/*)                             echo "L5" ;;
    contracts/*|CODEOWNERS|docs/*|Makefile)                                  echo "L0" ;;
    */*) echo "UNOWNED" ;;
    *)   echo "L0" ;;   # PARTITION line 22: L0 owns root files (no path prefix)
  esac
}

: "${SHA:?export SHA=<the merge commit to inspect> before running this}"
CHANGED="$(git diff --name-only "$SHA^1" "$SHA")"
[ -n "$CHANGED" ] || { echo "EMPTY DIFF -- STOP: cannot determine lane for $SHA"; exit 1; }
echo "$CHANGED" | while read -r f; do
  [ -n "$f" ] && printf '%-6s %s\n' "$(lane_of "$f")" "$f"
done
```

**Expected output** — every line prefixed with exactly one lane, all the same lane for a well-formed lane merge:

```
L1     schemas/registry/people.schema.json
L1     schemas/registry/roles.schema.json
L1     validators/registry/validate_people.py
```

Any line reading `UNOWNED` or a second lane prefix on a lane merge means the lane-guard check did not run or did not fail when it should have. That is a §8.3 finding, not a merge problem. Record it and continue the revert.

**Why `git diff --name-only "$SHA^1" "$SHA"` instead of `git show --stat`:** on a merge commit, `git show --stat` defaults to combined diff (`--cc`) which produces empty output for a clean merge (no conflicts), exit code 0. The `EMPTY DIFF` guard above catches this; `git diff` against the first parent always lists the files the merge brought in, regardless of whether there were conflicts. (DF-0189)

**SELF-VERIFY §1.2 (negative test — DF-0189).** Confirm the empty-diff guard fires on a merge commit that has no first-parent diff. Seed a synthetic merge commit where `$SHA^1` and `$SHA` have identical trees:

```bash
# Create a merge commit with an empty first-parent diff
git switch -c drill/empty-merge-$(date -u +%Y%m%d) origin/integration
EMPTY_SHA=$(git commit-tree HEAD^{tree} -p HEAD -p HEAD -m "DRILL: empty merge for §1.2 guard test")
# Run the lookup against the drill SHA — must exit 1 with "EMPTY DIFF"
CHANGED="$(git diff --name-only "$EMPTY_SHA^1" "$EMPTY_SHA")"
[ -n "$CHANGED" ] \
  || { echo "NEGATIVE TEST PASS: empty diff detected — guard would fire with 'EMPTY DIFF -- STOP'"; }
[ -z "$CHANGED" ] \
  && echo "(confirmed: guard exits 1 on empty first-parent diff)" \
  || echo "NEGATIVE TEST FAIL: diff was non-empty — drill setup is wrong"
git switch -
git branch -D "drill/empty-merge-$(date -u +%Y%m%d)"
```

**Asserts:** `$CHANGED` must be empty for the drill SHA, confirming the guard exits 1 with "EMPTY DIFF -- STOP: cannot determine lane for \$SHA". A non-empty diff means the drill commit was not constructed correctly.

---

## 2. The decision rule: revert or fix forward

Invariant 27: **rollback is preferred to hotfix.** That is the default and the burden of proof sits on fixing forward, not on reverting. But "prefer" is not "always", and the build has a case production does not: a revert on `integration` moves the base under four other lanes.

### 2.1 The two questions, in order

Ask them in this order. Do not skip to the second.

**Q1 — Is the gate red right now, or merely dirty?**
Red means a required check on `integration` or `main` is failing. Dirty means a check is amber, a lane self-reported a problem, or someone has a bad feeling. **Only red starts a revert.** Reverting on a hunch spends four lanes' rebase budget on a guess.

**Q2 — Do you know, from a failing CI run, which merge caused it?**
"Known" means you can name the run URL that was green on commit X and red on commit Y, and Y is a specific merge. If you cannot, you do not have a revert target. Go to §R1.1 (bisect) before §R1.2 (revert).

### 2.2 The rule

| Condition | Action | Why |
|---|---|---|
| Bad merge is the newest merge on `integration`, gate red | **Revert** | Cheapest possible. Nothing is built on top yet |
| Bad merge has 1–2 merges on top, no dependency on it | **Revert just the bad merge** | Test with `git revert --no-commit` first (§R1.3) |
| Bad merge has dependents on top (L4/L2/L3 merged after L1 and consume L1's schemas) | **Revert the stack, reverse train order** | §R1.4. Reverting L1 alone leaves L2 validating against schemas that no longer exist |
| Fix is a single-line, single-file, single-lane change and the owning lane has already produced it and it is green on a branch | **Fix forward** | A revert plus a re-land is two base changes for four lanes; one green commit is one |
| Cause is unknown | **Revert to last green, then diagnose** | You cannot fix what you have not diagnosed, and you must not diagnose on a red trunk |
| Cause is in `contracts/**` and ≥2 lanes are red | **Revert the contract, never the lanes** | §R4. The lanes are correct; the contract broke its own freeze |
| Change is `non-reversible` in the Section 28.1 sense — a records write, a published tag other consumers already pinned, an executed provisioning action | **Neither. Recovery strategy, not rollback** | Invariant 28: a non-reversible change is **never described as rollback-able**. §7 |
| `main` is red and a customer-facing or production-gating path is affected | **Revert immediately, notify after** | Invariant 27: rollback requires no prior approval during a SEV-1 |

### 2.3 The three tie-breakers

When the table above leaves you genuinely balanced:

1. **Time-to-green.** Whichever path puts `integration` green in less wall-clock time wins. A revert is minutes; a fix-forward that depends on a lane developer waking up is hours. Measure, do not estimate.
2. **Number of lanes disturbed.** A revert that changes the base for one lane beats a fix-forward that changes it for five.
3. **Reversibility of the recovery itself.** A revert is itself revertible (§R5). A fix-forward that lands a schema migration is not. When in doubt, choose the move you can undo.

### 2.4 What is never a reason to fix forward

* "The revert will look bad on the lane's record." Reverting is correct behaviour. Section 63.2 is binding here: *changing a decision when evidence changes is correct behaviour and must never be discouraged.*
* "We're close." You are not; you are red.
* "The lane says it's a flake." A lane developer with no repo context cannot classify a flake. If the check is genuinely flaky, that is a §8.4 finding about the check, and the revert still happens.

---

## R1. Revert a bad merge to `integration`

Run §1 first.

### R1.1 Identify the bad merge

```bash
set -euo pipefail
cd "$CP"
git switch integration
git pull --ff-only origin integration
git log --first-parent --oneline -15 integration
```

**Expected output** — one line per merge into `integration`, newest first:

```
9c41ab7 Merge pull request #218 from lane/5/p3-access-model
3f0d19e Merge pull request #217 from lane/3/p3-reconciler-core
b7e2c40 Merge pull request #215 from lane/2/p3-evidence-tool
5a19d83 Merge pull request #212 from lane/4/p3-record-schemas
2d6f8b1 Merge pull request #211 from lane/1/p3-product-schema
0e4c7aa Merge pull request #204 from lane/5/p2-infra-base
```

`--first-parent` is not optional. Without it you see every commit from inside every lane branch and you will revert a lane's internal commit instead of its merge, which produces a branch that is half-landed.

If you cannot name the bad merge from the CI history, bisect over merges only:

```bash
set -euo pipefail
git bisect start --first-parent
git bisect bad integration
git bisect good <LAST_KNOWN_GREEN_SHA>
# for each step:  run the integration gate, then:
git bisect bad     # or: git bisect good
# when finished:
git bisect reset
```

**Expected output** at the end of bisect:

```
3f0d19e2b8c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8 is the first bad commit
```

**STOP rule.** If bisect converges on a commit that is *not* a merge (parent count 2, see §R1.2), the breakage came from something L0 pushed directly to `integration`, not from a lane. Do not revert a lane. Go to §R4.

### R1.2 Classify the commit: merge or squash

The revert command differs and getting it wrong wastes a cycle.

```bash
export BAD=3f0d19e
git rev-list --parents -n 1 "$BAD" | awk '{print "parents:", NF-1}'
```

**Expected output**, one of:

```
parents: 2
```
→ It is a true merge commit. You **must** pass `-m 1` (revert relative to the first parent, i.e. `integration`).

```
parents: 1
```
→ It was squash-merged or is an ordinary commit. You **must not** pass `-m`.

Passing `-m 1` to a non-merge produces `error: mainline was specified but commit 3f0d19e is not a merge`. Omitting it on a merge produces `error: commit 3f0d19e is a merge but no -m option was given`. Both are safe failures — nothing is written — so if you guess wrong, read the error and use the other form.

### R1.3 Dry-run the revert

Never revert straight onto a shared branch. Prove it applies cleanly first.

```bash
set -euo pipefail
git switch -c revert/int-$BAD integration
git revert -m 1 --no-commit "$BAD"
git status --short
```

**Expected output** — deletions of exactly the reverted lane's owned paths, and nothing else:

```
D  schemas/registry/people.schema.json
D  schemas/registry/roles.schema.json
D  validators/registry/validate_people.py
```

Verify the blast radius is one lane before you commit:

```bash
git diff --cached --name-only | while read -r f; do lane_of "$f"; done | sort -u
```

**Expected output** — exactly one line:

```
L1
```

Two or more lines means later merges have entangled with this one and a single revert is not clean. Abort and go to §R1.4.

```bash
set -euo pipefail
# if entangled:
git revert --abort
git switch integration
git branch -D revert/int-$BAD
```

If the revert conflicts:

```
error: could not revert 3f0d19e... Merge pull request #211 from lane/1/p3-product-schema
hint: After resolving the conflicts, mark them with
hint: "git add/rm <pathspec>", then run "git revert --continue".
```

**STOP rule.** Do not resolve a revert conflict by hand on `integration`. A hand-resolved revert is a new, unreviewed, untested state that looks like a revert and is not one. Abort (`git revert --abort`) and go to §R1.4.

### R1.4 Revert a stack, in reverse train order

When later merges depend on the bad one, revert them all — newest first. `git revert` accepts multiple commits and applies them in the order given, so **list newest first**.

The merge train is L1 → L4 → L2 → L3 → L5 (PARTITION line 35). Reverse train order is therefore L5 → L3 → L2 → L4 → L1.

```bash
set -euo pipefail
export STACK_SHAS="9c41ab7 3f0d19e b7e2c40 5a19d83 2d6f8b1"   # newest first — classify EACH with §R1.2 first
export STACK_BRANCH="revert/int-stack-$(date -u +%Y%m%dT%H%M%SZ)"
git switch -c "$STACK_BRANCH" integration
git revert -m 1 --no-edit $STACK_SHAS
```

**Expected output** — one commit per revert, in the order listed:

```
[revert/int-stack-20260827T140155Z a1b2c3d] Revert "Merge pull request #218 from lane/5/p3-access-model"
 4 files changed, 0 insertions(+), 187 deletions(-)
[revert/int-stack-20260827T140155Z e4f5a6b] Revert "Merge pull request #217 from lane/3/p3-reconciler-core"
 9 files changed, 0 insertions(+), 612 deletions(-)
...
```

Confirm you have arrived exactly at the last-green tree — this is the assertion that the stack revert was complete:

```bash
git diff --stat <LAST_KNOWN_GREEN_SHA> HEAD
```

**Expected output** — empty. Any output means a revert did not fully undo its merge; treat as §9.

**If the sequence fails partway** — `-m 1` given to a single-parent entry, or a conflict — some reverts in the stack are already committed and `git revert` may be mid-sequence. Recover with:

```bash
git revert --abort || true      # if a conflict left one in progress
git reset --hard integration    # discard the partially-reverted stack
git switch integration
git branch -D "$STACK_BRANCH"
```

Then run §R1.2 against **each** SHA in `$STACK_SHAS` individually to confirm its parent count before retrying, and drop `-m 1` for any single-parent (squash-merged) entry.

### R1.5 The two-sided proof (mandatory — this is the gate that can fail)

A revert that was never shown to turn a red gate green has proven nothing. Both runs are recorded on the revert PR body.

```bash
set -euo pipefail
# BEFORE: confirm the gate is red specifically on the pre-revert head —
# the tip of integration you are reverting from, captured before you push anything.
export PRE_REVERT_HEAD="$(git rev-parse origin/integration)"
gh run list --branch integration --limit 3 \
  --json conclusion,headSha,workflowName,url \
  --jq --arg sha "$PRE_REVERT_HEAD" \
  '.[] | select(.headSha == $sha) | "\(.conclusion)\t\(.workflowName)\t\(.url)"'
```

**Expected output** — at least one `failure` on the pre-revert head:

```
failure	integration-gate	https://github.com/<org>/control-plane/actions/runs/1948201773
```

```bash
set -euo pipefail
# AFTER: push the revert branch and confirm the same gate goes green
git push -u origin HEAD
gh pr create --base integration --title "Revert: #211 (integration gate red)" \
  --body "Before (red): <URL from above>
After (green): filled in on completion
Reverted: $BAD
Lane affected: L1
Cause: <one line>
Re-land plan: §R5, tracked as <issue>"
gh pr checks --watch
```

**Expected output**:

```
All checks were successful
0 failing, 6 successful, 0 skipped, and 0 pending checks
```

**STOP rule — the negative condition.** If the "before" query returns **no failing run** on the pre-revert head, you do not have a proven cause. You are reverting something that may be innocent while the real cause stays on the branch. Abort the revert, delete the branch, and go back to §2.2 row "Cause is unknown". A revert justified by a gate that was never red is exactly the check that can only pass.

### R1.6 Post-revert assertions

Run all four. All four must pass before the merge train restarts.

```bash
# 1. The seeded reconciliation canary survived the revert (Section 53.1, AT-102)
test -f "$CANARY_PATH" && echo "CANARY PRESENT" || echo "CANARY MISSING"
```
**Expected:** `CANARY PRESENT`. If the revert deleted the canary seed, reconciliation will now report zero findings and be recorded as clean — a silently-vacuous run (EC-109). Restore the seed in the same PR. A reverted canary is a disarmed reconciler.

```bash
# 2. No foreign paths were touched by the revert itself
git diff --name-only integration...HEAD | while read -r f; do lane_of "$f"; done | sort -u
```
**Expected:** the lane(s) you intended, and `L0` only if you deliberately reverted an L0 commit.

```bash
# 3. contracts/** is untouched (PARTITION rule 2 — contracts are FROZEN)
git diff --name-only integration...HEAD -- contracts/ | wc -l
```
**Expected:** `0`. Anything else means you are in §R4, not §R1.

```bash
# 4. History is append-only — the revert added commits, removed none.
# Count only the revert commits themselves (by subject), not every commit the
# range re-spans — <LAST_KNOWN_GREEN_SHA>..HEAD also contains every lane-internal
# commit inside the reverted merge(s), which is not what this assertion is checking.
git rev-list --count --grep='^Revert' <LAST_KNOWN_GREEN_SHA>..HEAD
```
**Expected:** a positive integer equal to the number of reverts you made. If it is `0`, no revert commit exists in that range — you reset instead of reverting. That is a §7 violation.

### R1.7 Notify

The base has moved for every lane. This is a step, not a courtesy.

```bash
set -euo pipefail
gh issue create --title "integration reverted at $(date -u +%FT%TZ) — rebase required" \
  --label "blocker" \
  --body "Reverted: $BAD (PR #211, lane L1)
integration head is now: $(git rev-parse --short origin/integration)
ACTION for every lane with an open branch:
  git fetch origin && git rebase origin/integration
L1: your work is NOT lost. Re-land per protocol/07-rollback.md §R5.
Merge train is FROZEN until this issue is closed by L0."
```

**STOP rule for lanes.** A lane that sees this issue does not merge, does not open a PR, and does not rebase another lane's branch. It rebases its own branch and waits.

---

## R2. Revert a bad promotion to `main`

`main` is protected, releasable, and only `integration` merges into it (PARTITION line 32). It has **full branch protection with no machine bypass actor** (D89, PARTITION line 7). Three consequences you must know *before* the incident, not during it:

1. You cannot push a revert directly to `main`. It goes through a PR.
2. That PR needs a human approval, and invariant 9 (no self-approval, enforced by requiring approval of the most recent reviewable push) means **the person executing the revert cannot approve it**.
3. Therefore the rollback rota is two humans, always. If you are alone at 02:00 and `main` is red, your first action is to page the second approver, in parallel with §R2.1 — not after it.

### R2.1 Identify and prepare

```bash
set -euo pipefail
cd "$CP"
git switch main
git pull --ff-only origin main
git log --first-parent --oneline -5 main
```

**Expected output**:

```
d80f1c5 Merge pull request #221 from integration
44b0e97 Merge pull request #209 from integration
```

```bash
set -euo pipefail
export BADMAIN=d80f1c5
git rev-list --parents -n 1 "$BADMAIN" | awk '{print "parents:", NF-1}'
git switch -c revert/main-$BADMAIN main
git revert -m 1 --no-edit "$BADMAIN"
```

**Expected output**:

```
parents: 2
[revert/main-d80f1c5 8ae3f02] Revert "Merge pull request #221 from integration"
 23 files changed, 4 insertions(+), 1841 deletions(-)
```

Confirm you have landed exactly on the previous release tree:

```bash
git diff --stat 44b0e97 HEAD
```

**Expected output** — empty.

### R2.2 Record the authority before you push

Section 61.2 is explicit: *the branch that stops a failing rollout cannot be the one branch of this flow with no recorded basis to act.* Platform rollback is initiated by a holder of `platform-change-approval` or of `escalation`, whichever is reachable first, and is filed as a `platform_rollback` exception (Sections 26.3, 54.3).

```bash
set -euo pipefail
# Fields per the canonical exceptions schema (schemas/registry/exceptions/v1/exceptions.schema.json).
# Every one of these must be exported first — under set -u an unset var aborts the block
# rather than letting a literal placeholder get committed.
: "${EXC_ID:?export EXC_ID=EXC-<YYYY>-<NNN> (next free id in exceptions.yaml) before running this}"
: "${CHECK_NAME:?export CHECK_NAME=<the failing check on main> before running this}"
: "${RUN_URL:?export RUN_URL=<the failing run URL> before running this}"
: "${APPROVER:?export APPROVER=<holder of platform-change-approval or escalation> before running this}"
export START="$(date -u +%F)"
export EXPIRY="$(date -u -d '+14 days' +%F)"   # invariant 77: an exception without an expiry is invalid and fails CI
cat >> exceptions.yaml <<YAML
  - id: $EXC_ID
    type: platform_rollback
    reason: "main gate red on $CHECK_NAME; see run $RUN_URL"
    requester: $(git config user.email)
    authority: $APPROVER
    affected:
      products: []
      repositories: ["control-plane"]
    scope: "control-plane main — revert of promotion $BADMAIN"
    start: $START
    expiry: $EXPIRY
    compensating_control: "gh pr checks --watch on the revert PR before merge"
    compensating_control_record: "records/exceptions/${EXC_ID}-review.yaml"
    compensating_control_cadence: per-push
    owner: $APPROVER
    review_date: $EXPIRY
    renewals: 0
    became_permanent: false
    closure: null
    deactivation_trigger: "integration re-promoted green, or cause recorded as fixed forward"
YAML
git add exceptions.yaml && git commit -m "Open platform_rollback exception $EXC_ID for main revert $BADMAIN"
```

**STOP rule.** An exception entry with no `expiry` fails control-plane CI by invariant 77. If you are tempted to omit it because "this is temporary", that is precisely the case invariant 77 exists for.

### R2.3 Push, approve, merge

```bash
set -euo pipefail
git push -u origin HEAD
gh pr create --base main --title "REVERT main: promotion #221 — gate red" \
  --body "Before (red): $RUN_URL
Reverting: d80f1c5
Restores main to tree of: 44b0e97
Exception: $EXC_ID (platform_rollback)
Approver required: NOT the author (invariant 9)"
gh pr checks --watch
```

**Expected output** once the second human approves and checks pass:

```
All checks were successful
✓ Checks passing and 1 approving review
```

Merge, then verify:

```bash
set -euo pipefail
gh pr merge --merge --delete-branch
git switch main && git pull --ff-only origin main
git diff --stat 44b0e97 main
```

**Expected output** — empty.

### R2.4 Re-converge `integration` with `main`

This is the step people forget and it is the one that causes the *second* incident. `main` has been reverted; `integration` has not. The next promotion will re-introduce the exact commit you just reverted.

```bash
set -euo pipefail
git switch integration
git pull --ff-only origin integration
git merge-base --is-ancestor main integration && echo "integration contains main" || echo "DIVERGED"
```

**Expected output**: `DIVERGED` — because `main` now carries a revert commit `integration` does not have.

Resolve by reverting the same content on `integration` (§R1), **not** by merging `main` back into `integration`. Merging `main` back drags the revert commit into `integration` where §R5's revert-of-revert trap then applies to every lane at once.

First enumerate which of `integration`'s own merges this promotion carried — a promotion merge commit's second parent is the `integration` tip at the time it was promoted, so the merges carried are the range between the previous promotion's second parent and this one's:

```bash
set -euo pipefail
git log --first-parent --oneline "44b0e97^2..$BADMAIN^2"
```

**Expected output** — newest first, one line per lane merge this promotion carried (up to five, PARTITION line 35):

```
3f0d19e Merge pull request #217 from lane/3/p3-reconciler-core
2d6f8b1 Merge pull request #211 from lane/1/p3-product-schema
```

```bash
set -euo pipefail
# on integration, revert the same underlying merge(s) that #221 promoted (newest first, from the list above)
git switch -c revert/int-align-main integration
git revert -m 1 --no-edit 3f0d19e 2d6f8b1
git push -u origin HEAD
gh pr create --base integration --title "Align integration with reverted main (#221)" --body "Follows R2 revert of d80f1c5."
```

**Assertion after both land:**

```bash
git fetch origin
git diff --stat origin/main origin/integration -- contracts/ schemas/ validators/
```

**Expected output** — empty, or only paths deliberately still in flight on `integration`. Any difference in `contracts/` is a §R4 condition.

---

## R3. A lane branch has diverged badly

Owned by the lane developer. L0 does not do this for them.

### R3.1 Measure the divergence — do not guess

```bash
set -euo pipefail
cd "$CP"
git fetch origin
export LB=lane/1/p3-product-schema
git rev-list --left-right --count origin/integration...$LB
```

**Expected output** — two numbers, tab-separated: commits on `integration` not in the lane, then commits on the lane not in `integration`.

```
84	11
```

### R3.2 The threshold

| Measurement | Verdict | Go to |
|---|---|---|
| Behind < 50, and `git rebase` completes with 0 conflicts | Not diverged | Just rebase. `git rebase origin/integration` |
| Behind < 50, conflicts in ≤ 2 files, all inside the lane's owned paths | Recoverable by rebase | Rebase and resolve |
| Behind ≥ 50, **or** conflicts in > 2 files, **or** any conflict in a path the lane does not own, **or** rebase aborted twice | **Diverged badly** | §R3.3 |
| The branch contains commits touching foreign paths (§R3.4 returns non-empty) | **Diverged badly, and the lane-guard failed** | §R3.3, then §8.3 |

The threshold is deliberately low. A lane branch is specified as short-lived — *less than one day* (PARTITION line 34). A lane branch 84 commits behind `integration` is not a rebase problem; it is a branch that outlived its design, and rebasing it hides that.

### R3.3 The rebuild — the only safe recovery

Do not fight the rebase. Build a fresh branch off current `integration` and take back **only the paths this lane owns**. This procedure is structurally incapable of importing another lane's work, because you name the owned paths explicitly. That property is the whole point.

```bash
set -euo pipefail
cd "$CP"
git fetch origin
git switch -c ${LB}-v2 origin/integration

# Take back ONLY L1's owned paths (PARTITION line 17). Change this list for your lane; never widen it.
git checkout $LB -- \
  schemas/registry \
  schemas/product \
  registries \
  validators/registry

git status --short
```

**Expected output** — only owned paths, staged:

```
M  schemas/registry/people.schema.json
A  schemas/product/product.schema.json
M  validators/registry/validate_people.py
```

Lane path lists, verbatim from PARTITION:

| Lane | `git checkout $LB --` arguments |
|---|---|
| L1 | `schemas/registry schemas/product registries validators/registry` |
| L2 | `.github/workflows templates/workflows tools/evidence` |
| L3 | `reconciler tools/provision validators/drift` |
| L4 | `schemas/records metrics tools/records` |
| L5 | `access infra ops-vm notify assets` |

If one of those directories does not exist on `$LB` yet, `git checkout` prints `error: pathspec '...' did not match any file(s) known to git`. That is harmless — drop that argument and re-run. Do **not** substitute `.` for the missing path.

### R3.4 Prove the rebuild is clean

```bash
# Assertion 1: no foreign paths, no contracts/
git diff --cached --name-only | while read -r f; do lane_of "$f"; done | sort -u
```
**Expected:** exactly one line, your lane. `L0`, `UNOWNED`, or any other lane in that output means the rebuild is contaminated — reset (`git reset --hard origin/integration` then `git clean -fd` to remove any untracked foreign file `git checkout $LB --` brought in) and redo §R3.3 with a narrower path list.

```bash
# Assertion 2: contracts/** untouched
git diff --cached --name-only -- contracts/ | wc -l
```
**Expected:** `0`.

```bash
# Assertion 3: nothing was silently lost. Compare owned paths old-branch vs new-branch.
git commit -m "Rebuild ${LB} onto integration (diverged; see protocol 07 R3)"
git diff --stat $LB HEAD -- schemas/registry schemas/product registries validators/registry
```
**Expected:** empty. Non-empty means a file inside your owned paths differs between the old branch and the rebuild — read every line before proceeding. This assertion is the one that catches a mistyped path in §R3.3.

```bash
# Assertion 4: the negative test — the lane-guard still bites on the rebuilt branch (§8.3)
```
Run §8.3 against `${LB}-v2` before opening the PR. A rebuilt branch that the lane-guard no longer inspects is worse than the diverged branch you replaced.

### R3.5 Retire the old branch — without deleting it

```bash
set -euo pipefail
git push -u origin ${LB}-v2
git tag archive/${LB}-$(date -u +%Y%m%d) $LB
git push origin archive/${LB}-$(date -u +%Y%m%d)
```

**Expected output**:

```
 * [new tag]         archive/lane/1/p3-product-schema-20260827 -> archive/lane/1/p3-product-schema-20260827
```

Tag before you stop using the branch. Invariant 47 and Section 63.1: history is append-only and is not deleted. The tag is what makes "what was on the branch we abandoned?" answerable in three months. Only after the tag is pushed and `${LB}-v2` has merged may the old branch be deleted from the remote.

**STOP rule.** If `git checkout $LB -- <paths>` produces a tree that fails the lane's own self-verify command, do not open a PR and do not "fix it while you're in there". Open a blocker issue naming the failing verify command and its output, and stop. A lane developer improvising during a recovery is how a recovery becomes an outage.

---

## R4. A contract change broke three lanes

### R4.1 Recognise it in one command

Three or more lanes failing in the same cycle is not three lane failures. The common cause is upstream of all three.

```bash
cd "$CP"
git log --oneline -10 -- contracts/
```

**Expected output** if this is a contract break:

```
c0ffee1 Update event envelope: rename event_type -> type
```

**The rule you must apply immediately: stop debugging the lanes.** Three AI developers with no repo context, each independently debugging the same upstream break, produce three different wrong fixes, all of which land. Freeze the merge train (§R1.7 broadcast) before anything else.

### R4.2 The diagnosis is already written down

PARTITION rule 2: `contracts/**` is written by L0 in Phase 0 and **FROZEN**; a lane needing a contract change files a Contract Change Request and never edits `contracts/**`.

Section 60.2 and invariant 73: contract schemas are versioned, and **simultaneous fleet migration is never required**. The migration flow is *write the v2 schema alongside v1 — do not replace*; the validator supports **both**; consumers migrate on their own schedule.

A contract change that broke three lanes is, by construction, a **replacement rather than an addition**. That is the defect. The lanes are correct.

```bash
# Confirm: was v1 replaced, or was v2 added alongside?
git show --stat c0ffee1 -- contracts/
```

**Expected output for the defect** — modifications, no additions:

```
 contracts/event-envelope.schema.json | 14 +++++-------
 1 file changed, 6 insertions(+), 8 deletions(-)
```

**Expected output for a correct, additive contract change** — an addition:

```
 contracts/event-envelope.v2.schema.json | 96 ++++++++++++++++++++
 1 file changed, 96 insertions(+)
```

If you see the second shape, the contract is not your problem. Go back to §R1 and revert per-lane.

### R4.3 Restore the frozen contract

Two routes. Prefer the first.

**Route A — revert the L0 commit** (use when `contracts/` has one offending commit):

```bash
set -euo pipefail
git switch -c revert/contracts-c0ffee1 integration
git revert --no-edit c0ffee1
git diff --stat integration HEAD -- contracts/
```

**Expected output**:

```
 contracts/event-envelope.schema.json | 14 +++++-------
 1 file changed, 8 insertions(+), 6 deletions(-)
```

**Route B — restore from the freeze tag** (use when `contracts/` has been touched by several commits and Route A conflicts):

```bash
git tag -l 'contracts/v*'
```

**Expected output** — one entry per freeze / re-freeze CCR, oldest first:

```
contracts/v1.0.0
contracts/v1.1.0
```

```bash
set -euo pipefail
: "${FREEZE_TAG:?export FREEZE_TAG=<the most recent contracts/vX.Y.Z tag whose commit predates the offending change> before running this}"
git switch -c restore/contracts-frozen integration
git checkout "$FREEZE_TAG" -- contracts/
git status --short
git commit -m "Restore contracts/ to $FREEZE_TAG (PARTITION rule 2; Section 60.2)"
```

**STOP rule.** If `git tag -l 'contracts/v*'` returns nothing, the Phase 0 freeze was never tagged and you have no authoritative "before". Do not reconstruct it from memory or from a lane's copy. Open a blocker issue, use Route A, and record the missing tag as a §8 finding — an unrecoverable freeze point is a defect in the build protocol itself.

### R4.4 Verify against all three broken lanes before merging

The contract restore is only correct if it makes the lanes green. Prove it on each, on the restore branch, before it lands:

```bash
set -euo pipefail
for LANE in lane/1/p3-product-schema lane/2/p3-evidence-tool lane/4/p3-record-schemas; do
  git switch -c verify-$(basename $LANE) restore/contracts-frozen
  git checkout $LANE -- .           # take the lane's tree over the restored contract
  echo "=== $LANE ==="
  make validate 2>&1 | tail -5
  git switch -f restore/contracts-frozen           # force-discard staged/modified files from this iteration
  git reset --hard restore/contracts-frozen        # belt-and-suspenders: reset index to branch tip
  git clean -fd                                    # remove any untracked files left by git checkout
  git branch -D verify-$(basename $LANE)
done
# Post-loop assertion: staging area must be clean before the restore branch is merged
if [ -n "$(git status --porcelain)" ]; then
  echo "STOP: staging area is not clean after verification loop — abort and investigate" >&2
  exit 1
fi
```

**Expected output** — for each of the three lanes:

```
=== lane/1/p3-product-schema ===
validate: 41 schemas checked, 0 errors
```

These are throwaway local branches for measurement only; they are never pushed. `git checkout $LANE -- .` is permitted here **only** because the branch is deleted three lines later and never leaves the machine. Do not copy this line into any other procedure — everywhere else it violates PARTITION rule 1.

**STOP rule.** If restoring the contract makes two lanes green and one still red, the third lane has a genuine defect **as well**. Land the contract restore anyway (it unblocks two lanes and is correct on its own terms), then handle the third under §R1 or §R3. Do not hold the contract restore hostage to the third lane.

### R4.5 Re-land the contract change correctly

The contract change may well have been *needed*. It was executed wrongly, not conceived wrongly.

1. L0 opens a Contract Change Request using the template at `docs/escalation/CCR.md` (PARTITION rule 2). No lane opens it.
2. Write `contracts/event-envelope.v2.schema.json` **alongside** v1. Do not touch v1 (Section 60.2).
3. Validators accept **both** v1 and v2.
4. Canary first: one lane migrates and its gate passes before any other lane is asked to (invariant 72 — never fleet without canary; invariant 71 — platform changes are versioned, impact-analysed, canaried, verified and reversible; AT-025 — both versions supported simultaneously).
5. Remaining lanes migrate on their own schedule. Set a published deprecation deadline for v1 and record it; a lane still on v1 past the deadline is `transitional` with a named owner and a deadline, and feeds SIG-10 (Section 60.3).
6. Remove v1 only after every lane has migrated.

**Assertion that step 2 was done right:**

```bash
git diff --name-status integration...HEAD -- contracts/
```

**Expected output** — additions only:

```
A	contracts/event-envelope.v2.schema.json
```

An `M` on any existing contract file means you have repeated the defect. Do not merge.

---

## R5. Re-landing what you reverted

### R5.1 The trap

This is the single most common way a build loses work silently, and it produces no error message.

Once you revert merge `M` on `integration`, the *content* of `M` is still an ancestor of `integration` — git considers those commits already merged. If the lane re-opens a PR from the same branch, git computes an empty diff, the PR shows "no changes", or worse it merges cleanly and lands **nothing**. The lane's work appears to have shipped and has not.

### R5.2 Detect it before it bites

```bash
set -euo pipefail
git fetch origin
git log --grep='^Revert' --oneline origin/integration -20
git diff --stat origin/integration...$LB
```

**Expected output if you are in the trap** — the second command is empty despite the branch having commits:

```
9f0c2e1 Revert "Merge pull request #211 from lane/1/p3-product-schema"
```
```
(no output)
```

### R5.3 The fix: revert the revert

```bash
set -euo pipefail
export REVERT_SHA=9f0c2e1
git switch -c lane/1/p3-product-schema-reland origin/integration
git revert --no-edit "$REVERT_SHA"
```

**Expected output** (git ≥ 2.36 — check with `git --version`):

```
[lane/1/p3-product-schema-reland 6d2a710] Reapply "Merge pull request #211 from lane/1/p3-product-schema"
 3 files changed, 214 insertions(+)
 create mode 100644 schemas/registry/people.schema.json
```

On git < 2.36 the same successful reapply instead prints `Revert "Revert \"Merge pull request #211...\"\""` — this is not a failure, just an older git's label for the identical operation. Either subject line, with the files and insertion count shown, is success.

Then commit the actual fix on top of that, in the same branch and the same PR, so the reapply and the fix land atomically:

```bash
set -euo pipefail
# ... make the fix that caused the original revert ...
git add schemas/registry/people.schema.json
git commit -m "Fix: <the defect that caused the revert of #211>"
git diff --stat origin/integration...HEAD
```

**Expected output** — non-empty, showing both the restored files and the fix:

```
 schemas/registry/people.schema.json  | 216 ++++++++++++++++++++
 validators/registry/validate_people.py |  12 +-
 2 files changed, 226 insertions(+), 2 deletions(-)
```

**STOP rule.** If `git diff --stat origin/integration...HEAD` is empty at this point, the reapply did not take. Do not open the PR — a PR with an empty diff that reports success is the failure mode this whole section exists to prevent. Re-check `$REVERT_SHA` names the revert commit and not the original merge.

### R5.4 The re-land must clear the same gate that was red

The re-land PR body carries three URLs: the original red run, the revert's green run, and the re-land's green run. Two greens with no red in between is not evidence — it is the check that can only pass, in PR form.

---

## 6. Recovery when the recovery tooling is down

Section 46.1 (Degraded Engineering Mode) and AT-028: GitHub unavailable does not stop local work; state is reconciled on recovery, never assumed. (AT-029 proves the analogous claim for **production** rollback with the control plane switched off — out of this file's scope per line 3 above — not the build-branch manual path below; the two are parallel, not the same test.)

For this build the manual path is:

```bash
set -euo pipefail
# Every recovery clone holds the full history. Nothing above needs a server except push.
cd "$CP"
git log --first-parent --oneline integration -20     # works offline
git revert -m 1 --no-edit "$BAD"                     # works offline
# When the remote returns:
git fetch origin
git log --oneline origin/integration -5              # confirm nobody else moved it
git push -u origin HEAD                              # then PR as normal
```

**STOP rule.** When the remote returns, **re-read `origin/integration` before pushing**. Do not assume the branch is where you left it. State is reconciled on recovery, never assumed.

---

## 7. What you may never roll back

### 7.1 Non-reversible in the Section 28.1 sense

Invariant 28: non-reversible changes require an explicit recovery strategy and **never claim rollback capability**. Section 28.1 classifies them; Section 30.2 makes the plan-checker reject a `partially-reversible` or `non-reversible` plan that states no recovery strategy.

In the build, these are non-reversible:

| Action | Why revert does not work | Recovery strategy |
|---|---|---|
| A commit written to `control-plane-records` | Ruleset blocks rewriting; append-only by design (D107) | §7.2 — append a correction record |
| A published tag another lane has already pinned (invariant 85: reusable workflows are consumed by pinned tag) | Moving a tag reaches every consumer with no reviewable diff — Blocking drift by Section 53.1 | Publish a **new** tag; never move the old one |
| A provisioning action already executed against GitHub (Teams, branch protection, environments) | The side effect is outside git | Reconciliation Level 3 auto-repair back to declared state — and only toward the stricter state (invariant 81) |
| A rotated credential | The old value is gone | Re-rotate forward; never restore an old secret |

### 7.2 `control-plane-records` is append-only, always

```bash
cd "$CPR"
git push --force origin main
```

**Expected output — and this failure is the correct outcome:**

```
remote: error: GH013: Repository rule violations found for refs/heads/main.
remote: - Cannot force-push to this branch
 ! [remote rejected] main -> main (push declined due to repository rule violations)
error: failed to push some refs
```

Correcting a bad record is an **append**, not a rewrite:

```bash
set -euo pipefail
# Every one of these must be exported first — under set -u an unset var aborts the block
# rather than letting a literal placeholder get committed into the append-only records repo.
: "${BAD_RECORD:?export BAD_RECORD=records/<store>/<the-bad-record-file>.yaml before running this}"
: "${CORRECTION_REASON:?export CORRECTION_REASON=<what was wrong> before running this}"
: "${CORRECTED_BY:?export CORRECTED_BY=<person> before running this}"
cd "$CPR"
git switch main && git pull --ff-only
mkdir -p records/corrections
CORRECTION_FILE="records/corrections/$(date -u +%Y%m%dT%H%M%SZ)-correction.yaml"
cat > "$CORRECTION_FILE" <<YAML
record_schema_version: 1
type: correction
corrects: $BAD_RECORD
reason: "$CORRECTION_REASON"
superseded_at: $(date -u +%FT%TZ)
corrected_by: $CORRECTED_BY
YAML
git add records/corrections && git commit -m "Correct $BAD_RECORD: $CORRECTION_REASON"
git push origin main
```

**Expected output**:

```
To github.com:<org>/control-plane-records.git
   4a1b9c2..7e0d3f8  main -> main
```

Section 63.1: state changes are **recorded, not overwritten**. Invariant 48: existing verified content is never silently downgraded (AT-088).

**STOP rule.** If a records rewrite has already happened — the reconciler reports a records head that does not descend from its last anchor — that is Level 5 (Section 53.2): an incident, escalated to the escalation role, not a git problem you fix quietly.

---

## 8. Proving these procedures can fail

A rollback procedure that has never been executed is a hypothesis (Section 44.4 makes this explicit for restores; invariant 3 states it as a rule; AT-026 requires *a working, tested rollback*). Every gate below is executed for real, on the schedule stated, in the manner of the Section 95.4 activation checklist — *executed for real, including the negative tests, not assumed*.

Results are recorded under `records/build-drills/`. A drill with no record did not happen.

| # | Drill | Cadence | Passes only if the check **FAILS** |
|---|---|---|---|
| 8.1 | Seeded bad merge | Before the first real cycle, then weekly | The integration gate goes **red** |
| 8.2 | Force-push rejection | Before the first real cycle, then on every ruleset change | The push is **rejected** |
| 8.3 | Lane-guard bite | On every rebuilt branch (§R3.4) and weekly | The lane-guard check **fails** |
| 8.4 | Revert-of-revert detection | Weekly | The empty-diff PR is **blocked** |
| 8.5 | Canary survives a revert | After every §R1 execution | The canary is **found** by the next reconciliation run |

### 8.1 Seeded bad merge — prove the integration gate can go red

```bash
set -euo pipefail
cd "$CP"
git switch -c lane/1/drill-foreign-$(date -u +%Y%m%d) origin/integration
# Plant a defect inside ONE lane's owned paths — a schema that cannot validate.
printf '{ "$schema": "http://json-schema.org/draft-07/schema#", "type": "nonsense-type" }\n' \
  > schemas/registry/DRILL-BROKEN.schema.json
git add schemas/registry/DRILL-BROKEN.schema.json
git commit -m "DRILL: seeded invalid schema — expect integration gate RED"
git push -u origin HEAD
gh pr create --base integration --draft \
  --title "DRILL: seeded bad merge — expect RED" --body "protocol/07-rollback.md §8.1. Do not merge."
gh pr checks --watch
```

**Expected output — failure is the pass condition:**

```
Some checks were not successful
1 failing, 5 successful, 0 skipped, and 0 pending checks

X  integration-gate   https://github.com/<org>/control-plane/actions/runs/1948233901
```

Now execute §R1 against the drill branch end to end, timing it. Then:

```bash
gh pr close --delete-branch
```

**If the gate goes green with `DRILL-BROKEN.schema.json` present, the integration gate is not checking schemas.** That is a Blocking finding: the gate is a check that can only pass. Freeze the merge train, open a blocker issue, and do not restart the train until the gate has been shown to bite. This drill's only valuable outcome is the red.

**SELF-VERIFY §8.1 (negative test — DF-0190).** The branch name `drill/bad-merge-<date>` (original form) was a non-lane name. The lane-guard would have fired with an "unattributable branch" error rather than passing through to the integration gate, producing a different error class than the drill intends to prove. The fix (`lane/1/drill-foreign-<date>`) is an L1-format name: the lane guard passes because the drill commits only touch `schemas/registry/` (an L1 path), and the integration gate — not the lane guard — delivers the expected red. If the drill produces both `lane-guard` and `integration-gate` failures, check that the commit touches only L1-owned paths; a dual failure indicates the branch or paths are wrong, not that the integration gate is working correctly.

### 8.2 Force-push rejection — prove the immutability wall is real

Run §7.2 verbatim against `control-plane-records`, and again against `integration` and `main` in `control-plane`.

**Safety contract (B-16).** This drill deliberately attempts the one action §1.1 rule 1 bans. If branch protection is not in fact armed — the exact condition the drill exists to catch — the push **succeeds**, and `integration` or `main` is rewritten for every lane mid-cycle. The drill therefore never runs against the live `integration`/`main` tip without first capturing the SHA it can restore to, and it verifies that restore before declaring the drill complete either way.

```bash
set -euo pipefail
cd "$CP"
git fetch origin integration main
SHA_INTEGRATION_BEFORE="$(git rev-parse origin/integration)"
SHA_MAIN_BEFORE="$(git rev-parse origin/main)"
echo "saved-SHA: integration=${SHA_INTEGRATION_BEFORE} main=${SHA_MAIN_BEFORE}"

git push --force origin origin/integration~1:integration
```

**Expected output — rejection is the pass condition:**

```
remote: error: GH006: Protected branch update failed for refs/heads/integration.
remote: - Cannot force-push to a protected branch
 ! [remote rejected] origin/integration~1 -> integration (protected branch hook declined)
```

**If this push instead succeeds:** `integration` now points at `origin/integration~1`. Restore immediately and verify the restore before doing anything else:

```bash
git push origin "${SHA_INTEGRATION_BEFORE}:integration"
[ "$(git rev-parse origin/integration)" = "$SHA_INTEGRATION_BEFORE" ] \
  || { echo "STOP-05: integration did not restore to the saved SHA"; exit 1; }
echo "integration restored to ${SHA_INTEGRATION_BEFORE}"
```

```bash
cd "$CP"
git push --force origin origin/main~1:main
```

**Expected output — rejection is the pass condition:**

```
remote: error: GH006: Protected branch update failed for refs/heads/main.
remote: - Cannot force-push to a protected branch
 ! [remote rejected] origin/main~1 -> main (protected branch hook declined)
```

**If this push instead succeeds:** restore `main` the same way, against `$SHA_MAIN_BEFORE`, and verify it before continuing:

```bash
git push origin "${SHA_MAIN_BEFORE}:main"
[ "$(git rev-parse origin/main)" = "$SHA_MAIN_BEFORE" ] \
  || { echo "STOP-05: main did not restore to the saved SHA"; exit 1; }
echo "main restored to ${SHA_MAIN_BEFORE}"
```

**If any of the three force-pushes succeeds, stop the build** — after the matching restore above has been run and verified. Invariant 47, Section 63.1 and D107 all rest on this rejection. An append-only guarantee that has never been tested against an actual force-push is an assertion, and Section 53.1 is explicit that no control which can be rewritten by the credential checking it is a control. A drill that rewrites a shared branch and leaves it rewritten because "the push wasn't supposed to succeed" is not a smaller incident than the defect it was proving absent.

### 8.3 Lane-guard bite — prove path ownership is enforced

Run on every rebuilt branch from §R3, and weekly on a throwaway branch.

```bash
set -euo pipefail
git switch -c lane/3/drill-foreign-$(date -u +%Y%m%d) origin/integration
# From an L3 branch, touch an L5-owned path (PARTITION line 21).
echo "# DRILL — expect lane-guard FAIL" >> access/DRILL.md
git add access/DRILL.md && git commit -m "DRILL: L3 branch touching L5 path — expect FAIL"
git push -u origin HEAD
gh pr create --base integration --draft \
  --title "DRILL: foreign path — expect lane-guard FAIL" --body "protocol/07-rollback.md §8.3. Do not merge."
gh pr checks --watch
```

**Expected output — failure is the pass condition:**

```
Some checks were not successful
X  lane-guard   https://github.com/<org>/control-plane/actions/runs/1948241188

branch lane/3/drill-foreign-<date> -> lane L3 FOREIGN: access/DRILL.md is owned by L5
```

```bash
gh pr close --delete-branch
```

**If lane-guard passes, PARTITION rule 1 is unenforced** and the entire no-conflict argument of the partition collapses. Blocking. This is exactly the case invariant 87 covers — every architecture policy is enforced by the platform wherever the platform can enforce it.

**SELF-VERIFY §8.3 (negative test — DF-0190).** The original branch name `drill/foreign-path-<date>` was a non-lane name. The lane-guard cannot derive a lane from it, so it emits an "unattributable branch" error — a different error class from the foreign-path refusal the drill is supposed to prove. The drill then appeared to pass (the lane-guard ran and fired) but was proving the wrong thing. With the fixed name `lane/3/drill-foreign-<date>`, the guard derives lane L3 from the branch prefix, detects that `access/DRILL.md` belongs to L5, and emits the `branch lane/3/... -> lane L3 FOREIGN` refusal. If the output shows "unattributable branch" rather than the FOREIGN refusal, the branch name does not follow the `lane/<N>/` prefix convention required by the guard.

### 8.4 Revert-of-revert detection — prove an empty PR cannot merge

```bash
set -euo pipefail
# After any §R1 revert, from the same lane branch that was reverted:
: "${LB:?export LB=<the lane branch that was reverted> before running this drill}"
git switch -c drill/empty-reland origin/integration
git merge --no-commit --no-ff $LB
git diff --cached --stat
```

**Expected output — empty is the finding, and the gate must catch it:**

```
(no output)
```

Push it and confirm the gate blocks a zero-change PR:

```bash
set -euo pipefail
git commit --allow-empty -m "DRILL: empty re-land — expect BLOCK"
git push -u origin HEAD
gh pr create --base integration --draft --title "DRILL: empty re-land — expect BLOCK" --body "protocol/07-rollback.md §8.4"
gh pr checks --watch
```

**A PR with no diff that reports all checks green is a passing check with nothing to check.** If it goes green, add the empty-diff guard to the integration gate before the next cycle.

### 8.5 Canary survives a revert

Run after every §R1 execution, not on a cadence.

```bash
set -euo pipefail
test -f "$CANARY_PATH" && echo "CANARY PRESENT" || echo "CANARY MISSING"
# Then the authoritative test — the run must FIND it:
make reconcile 2>&1 | tee /tmp/reconcile.out
grep -c 'seeded-canary' /tmp/reconcile.out
```

**Expected output**:

```
CANARY PRESENT
1
```

A count of `0` — a reconciliation run reporting zero findings, canary included — is a **FAILED run**, not a clean one (Section 53.1, AT-102). It raises SIG-13 and triggers the control-loop gap procedure (Section 53.7). EC-109 names the underlying case: a run that completes "clean" while actually checking nothing. Silence is never taken as health.

---

## 9. STOP rules and escalation

Stop and open a blocker issue — do not improvise — when any of these is true:

| Condition | Why you stop |
|---|---|
| A revert conflicts and you are tempted to hand-resolve it on a shared branch | A hand-resolved revert is a new untested state wearing a revert's name (§R1.3) |
| The "before" CI run on the pre-revert head was never red | You have no proven cause; you are about to revert something innocent (§R1.5) |
| `git tag -l 'contracts-frozen*'` returns nothing during §R4 | You have no authoritative "before" for the frozen contract (§R4.3) |
| A drill in §8 **passes when it should fail** | The gate is a check that can only pass. Freeze the train |
| A force-push to any protected branch succeeds | The immutability wall is not there (§8.2) |
| The reconciler reports a records head not descending from its last anchor | Proof of rewriting. Level 5 incident (D107, Section 53.2) |
| More than two lanes are red and `contracts/` is clean | Not a contract break and not a lane break. Cause is unknown; escalate rather than guess |
| You are alone and `main` needs a revert | Invariant 9 means you cannot approve your own revert. Page the second approver first (§R2) |
| Any procedure here requires a judgment call the file does not make for you | PARTITION line 47: *if a task needs judgment, it belongs to L0* |

Blocker issue template:

```bash
set -euo pipefail
gh issue create --label "blocker" \
  --title "BLOCKER: <one line> — merge train frozen" \
  --body "Procedure attempted: protocol/07-rollback.md §<section>
Command run: <exact command>
Expected output: <from this file>
Actual output:
<paste>
integration head: $(git rev-parse --short origin/integration)
main head: $(git rev-parse --short origin/main)
Lanes affected: <list>
Merge train state: FROZEN
Requires: L0 decision"
```

---

## 10. Records this file requires

Every execution writes evidence. A recovery with no record cannot be learned from, and Section 58.1 detects failure patterns by counting occurrences — which requires them to have been recorded.

| Event | Record | Store |
|---|---|---|
| Any §R1 revert on `integration` | Revert PR with before-red and after-green run URLs | The PR itself |
| Any §R2 revert on `main` | `platform_rollback` exception with a mandatory expiry (invariant 77) | `exceptions.yaml` |
| Any §R3 rebuild | `archive/<branch>-<date>` tag pushed before the old branch is retired | `control-plane` tags |
| Any §R4 contract restore | Contract Change Request (`docs/escalation/CCR.md`) + the additive v2 re-land plan | Change manifest (Section 25) |
| Every §8 drill | Result, including which check failed and its run URL | `records/build-drills/` |
| A drill that passed when it should have failed | Blocker issue **and** a drill record marked `FAILED-OPEN` | `records/build-drills/` |

Three or more recoveries of the same class in the build is a pattern candidate under Section 58.3's third-occurrence question — the answer to which is a change to the protocol, not a fourth recovery.
