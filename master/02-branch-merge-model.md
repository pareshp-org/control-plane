# 02 — Branch and Merge Model

**Status:** Binding for the whole build. Conforms to `implementation/PARTITION.md` (FROZEN).
**Governs:** the git topology, branch lifetimes, the ordered merge train, rebase discipline, merge authority, the daily cycle, behind-lane recovery, conflict authority, and the literal branch-protection and ruleset configuration for `main`, `integration` and the records repository.
**Does not govern:** task content, per-lane acceptance criteria, CI job implementation. Those live in your lane's task files (`implementation/lanes/L<N>-*.md`) and `implementation/protocol/`; resolve a task id to its file and line via `implementation/lanes/L<N>-CONCORDANCE.md` or `implementation/lanes/_ALIASES.tsv`.

**Precedence.** Where this file and `PARTITION.md` appear to differ, `PARTITION.md` wins and this file is defective — report it to L0. Where this file and `MultiProduct_MasterSpec_v4.0.md` appear to differ on a protection or ruleset rule, the spec wins.

**Shell note.** Every fenced block is POSIX shell (Git Bash on Windows, or any Linux shell). Single-line `git` / `gh` commands also run verbatim in PowerShell. Multi-line `for` loops do **not** run in PowerShell — run those in Git Bash. Only L0 runs loops.

**Placeholders.** Exactly three values are supplied by L0 once, at Phase 0, and are literal everywhere after that: `$ORG` (the GitHub organisation login), `$LANE` (your lane number, `1`–`5`), and the lane git identity from **DECISION D-BMM-01**. Everywhere else in this file, an angle-bracket token (`<pr-number>`, `<scratch>`, `<repo>`/`<file>`/`<id>`, `<merge-commit-sha>`, `<1..5>`, `<last-anchored-sha>`, and similar) is a per-invocation value you substitute at the point of use, not a fourth L0-supplied constant.

---

## 1. Repositories, branches and lifetimes

Repositories are fixed by `PARTITION.md`. This file adds branches and lifetimes only.

| Repo | Branch | Purpose | Protected | Lifetime | Who may push | Who may merge into it |
|---|---|---|---|---|---|---|
| `control-plane` | `main` | Releasable trunk. Default branch. | Yes — ruleset **CP-1** | Permanent | Nobody directly (PR only) | L0 only, from `integration` only |
| `control-plane` | `integration` | Daily merge target for all five lanes | Yes — ruleset **CP-2** | Build-time only; deleted at build close (§10.10) | Nobody directly (PR only) | L0 only, from `lane/N/*` only |
| `control-plane` | `lane/N/<phase>-<task>` | One task, one lane | **No** — deliberately unprotected so rebase + `--force-with-lease` works | < 1 working day | Lane N only | Nobody (it is merged *from*, never *into*) |
| `control-plane` | tags `workflows/*` | Pinned reusable-workflow releases (L2) | Yes — ruleset **CP-3**, immutable | Permanent | L0 only | — |
| `control-plane` | tags `contracts/*` | Frozen contract-freeze tags | Yes — ruleset **CP-4**, immutable | Permanent | L0 only | — |
| `control-plane` | tags `cycle/*` | One tag per completed merge cycle | No | Permanent | L0 only | — |
| `control-plane-records` | `main` (default) | `records/**`, `events/**` | Yes — ruleset **REC-1**: force-push/delete blocked, **no review rule** (D89) | Permanent | L4 (build) and later the records-writer credential — fast-forward appends only | L0 only, from `lane/4/*` |
| `control-plane-records` | `lane/4/<phase>-<task>` | L4 task branches | No | < 1 working day | L4 only | Nobody |
| `control-plane-records` | all tags | Export/anchor tags | Yes — ruleset **REC-2**, immutable | Permanent | L0 only | — |
| `product-template` | `main` | Scaffold consumed by `create-product` | Yes — ruleset **CP-1** shape | Permanent | Nobody directly | L0 only |

**Why `integration` exists at all.** Five AI lanes merging straight to `main` would make `main` un-releasable for most of every day, and would put the first bad lane merge of a cycle directly on the branch that Section 11.3 protection guards. `integration` absorbs the cycle; `main` moves once, when the full gate is green. `integration` is build-time scaffolding: the shipped operating system has one long-lived branch per repository, because the reconciler's comparison set (Section 53.1) reasons about the default branch and knows nothing about a second permanent branch.

**Why `main` is the default branch and `integration` is not.** Spec Section 98.2's Phase 1 completion check is stated against *the default branch* ("no direct human push to any default branch succeeds"). Making `integration` the default would move that check onto the throwaway branch.

---

## 2. Branch naming

**Rule (from `PARTITION.md`):** `lane/<N>/<phase>-<task>`

| Field | Allowed values | Notes |
|---|---|---|
| `<N>` | `1` `2` `3` `4` `5` | Your lane. Never another lane's number. |
| `<phase>` | `p0` `p1` `p2` `p3` `p4` `p5` `p6` `p7` | `p1`–`p7` are the Foundation phases of spec Section 98.2; `p0` is not a Spec §98 phase — it is the programme's own contract-freeze phase (`master/09-glossary-and-conventions.md` §3.2). Governance/People-tier work uses `g1`–`g8` / `pp1`–`pp8`. |
| `<task>` | `[a-z0-9-]{3,40}` | The task id from your lane file, lower-case, hyphens only. |

Valid: `lane/1/p1-schema-people` · `lane/4/p1-records-dirs` · `lane/2/p6-workflow-build`
Invalid: `lane/1/feature-x` (no phase) · `Lane/1/p1-x` (case) · `lane/01/p1-x` (zero-padded) · `lane/1/p1_schema_people` (underscores)

**REG-011: the branch naming regex is informational, not a hard gate.** Non-matching names are reported but do not cause `exit 1`; L0 uses the pattern to identify strays, not to reject pushes.

Check branch name (REG-011 advisory — rename recommended but not a push gate):

```bash
set -euo pipefail
B=$(git rev-parse --abbrev-ref HEAD)
echo "$B" | grep -Eq '^lane/[1-5]/(p[0-7]|g[1-8]|pp[1-8])-[a-z0-9-]{3,40}$' \
  && echo "PASS: branch name legal -> $B" \
  || echo "FAIL: branch name does not match the recommended pattern -> $B  (rename with: git branch -m <legal-name>)"
```

**One task per branch.** A branch carrying two task ids is rejected by L0 without review. Split it.

---

## 3. Who may merge what

| Actor | May merge | May never |
|---|---|---|
| **L0** (human/lead integrator) | `lane/N/*` → `integration`; `integration` → `main`; any revert | — |
| **Lane N developer** | Nothing. Ever. | Merge any branch anywhere; press "Merge pull request"; enable auto-merge; merge `integration` *into* a lane branch (§7) |
| **Renovate app** (from Phase 2) | Its own dependency PRs on `main`, under the split ruleset of §10.7 only | Touch any path outside the declared manifest/lockfile paths; carry a commit authored by any other identity (Section 33.2 — that is Blocking drift) |
| **records-writer credential** (post-build) | Nothing — it *pushes*, it approves nothing (Section 40.1, D89) | Reach `control-plane` at all; hold any bypass-actor slot (D107) |
| **reconciler credential** | Nothing | Merge, approve, or write outside its declared repair scope (Section 26.4) |

Spec anchor, Section 27: *"Merge → the change enters the default branch (mechanical, once protection rules are satisfied)… Merge is a mechanical consequence of protection rules being satisfied. It is not a decision."* L0 is not exercising judgment when merging a green lane PR in its train slot; L0 is executing the train. Judgment happens at review, and at the STOP rules.

**Absolute prohibitions from `PARTITION.md` (restated, non-negotiable):** a lane NEVER merges another lane's branch; a lane NEVER rebases another lane's branch.

---

## 4. The merge train

### 4.1 The order

```
   L1 ──▶ L4 ──▶ L2 ──▶ L3 ──▶ L5 ──▶ [full gate] ──▶ main
Registries  Records   Pipeline  Reconciler  Access
& Contracts Events &  &         &           Infra
(A,B)       Metrics   Evidence  Provision   & Ops
            (I,N)     (E,F)     (C,D)       (K,L,M,Q,R)
```

Fixed by `PARTITION.md`. **The train never reorders.** A lane with nothing ready is skipped, not swapped.

### 4.2 Why this order

The train orders by *what must already be on `integration` for the next lane's CI to validate* — not by runtime dependency. Runtime dependencies that would demand a different order are carried by `contracts/**` instead, which is exactly `PARTITION.md` anti-conflict rule 4 ("A lane consumes another lane's output only through `contracts/**` or a published artifact").

| Slot | Lane | Why here |
|---|---|---|
| 1 | **L1** | Subsystems A and B. Spec Section 99.2 dependency spine: *A (registries) → B (validation) → C (reconciliation) and D (provisioning)*. Everything else validates against L1's schemas, so L1's schema changes must be on `integration` before any lane's validator run means anything. |
| 2 | **L4** | Subsystems I and N, plus the whole records repository. `PARTITION.md`: *"L1 (schemas) and L4 (record schemas) produce what everything validates against."* Spec Section 99.6 risk 2 (evidence-plumbing gap) requires Section 97's record stores built before anything that reads from them. L2's evidence tooling and L3's drift records both *write into* shapes L4 defines. |
| 3 | **L2** | Subsystems E and F. `PARTITION.md`: *"L2 (workflows) consumes L1 schemas."* L2 also produces the `workflows/*` tags whose resolved commit SHAs sit in the reconciler's comparison set (Section 53.1, row `platform.yaml` workflow versions), so L2 must land before L3 can build that row against anything real. |
| 4 | **L3** | Subsystems C and D. Consumes L1 schemas (already in) and L2's workflow tags (already in). Its stated dependency on L5's access model (`PARTITION.md` dependency order) is satisfied through `contracts/**`, frozen by L0 in Phase 0 — which is *why* L3 can precede L5. |
| 5 | **L5** | Subsystems K, L, M, Q, R. `PARTITION.md`: *"L5 (access/infra) is independent at build time, integrates last."* Spec Section 99.2 lists M and R with no dependencies and L depending on A and D — both already merged by this slot. |

**The apparent contradiction, resolved once.** Spec Section 99.2 gives subsystem I (L4) a dependency on subsystem E (L2), which is the reverse of slots 2 and 3. That is a *runtime* dependency: the metrics pipeline ingests what the workflow library emits, at run time, through the event taxonomy. At *build* time L4 defines the taxonomy and L2 emits against it, so the schema must precede the emitter. The two are reconciled by anti-conflict rule 4: L2 never imports L4 source; it codes against `contracts/**` and against L4's published record schemas. If a lane ever needs the other lane's *source*, that is a partition violation — STOP and file a blocker.

### 4.3 Train rules

1. **One pass per cycle.** Each lane gets exactly one merge slot per cycle. A second PR from the same lane waits for the next cycle.
2. **A lane may merge at most 3 PRs in its slot.** More than 3 is a signal the lane is batching instead of shipping daily; L0 merges the first 3 in PR-number order and defers the rest.
3. **Green before advance.** After each slot, `integration` must be green before the next slot opens. If slot *k* breaks `integration`, the train **stops**; L0 reverts slot *k* (§9.4) and the remaining slots run in the same cycle.
4. **Skip, never swap.** An empty slot is skipped. The order is never permuted, even to "use the time".
5. **`integration` → `main` only after all five slots.** Never mid-train.
6. **Nothing merges outside the train window** (§5) except a P0 revert.

---

## 5. The daily cycle

All times are the operating day's local times; L0 fixes the actual clock times at Phase 0 and they do not change afterwards.

| Time | Actor | Action |
|---|---|---|
| 09:00 | L0 | **Cycle open.** Verify `main` and `integration` are green; publish the cycle id `cycle/YYYY-MM-DD`; post yesterday's train result. |
| 09:00–15:00 | Lanes 1–5 | Work: one task per branch, rebase, self-verify, push, open PR. |
| 15:00 | Lanes 1–5 | **PR cutoff.** A PR opened after 15:00 is next cycle's. |
| 15:00–17:30 | L0 | **Merge train**, in order L1 → L4 → L2 → L3 → L5, green between slots. |
| 17:30 | L0 | **Promotion.** Full gate on `integration`; if green, `integration` → `main`; tag `cycle/YYYY-MM-DD`. |
| 17:45 | L0 | **Cycle close.** Delete merged lane branches; write the bootstrap log entry (Section 95.4 — the weekly entry is a hard requirement with a Blocking staleness detector at 7 days). |

### 5.1 L0 cycle-open commands

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org
cd control-plane
git fetch origin --prune --tags
git log --oneline -1 origin/main
git log --oneline -1 origin/integration
gh run list --branch integration --limit 5
gh pr list --base integration --state open --json number,headRefName,isDraft,mergeable,statusCheckRollup \
  --jq '.[] | "\(.number) \(.headRefName) draft=\(.isDraft) mergeable=\(.mergeable)"'
```

### 5.2 L0 merge-train commands — run once per slot, in train order

Substitute `N` with the slot's lane number, in the order `1 4 2 3 5`.

```bash
set -euo pipefail
export N=1
gh pr list --base integration --state open --search "head:lane/$N/" \
  --json number,headRefName,mergeable,reviewDecision \
  --jq '.[] | "\(.number)\t\(.headRefName)\tmergeable=\(.mergeable)"'
```

For each PR number returned, in ascending PR number:

```bash
set -euo pipefail
export PR=<pr-number>
gh pr checks $PR                                  # every check must read "pass"
gh pr diff $PR --name-only                        # every path must belong to lane $N
gh pr merge $PR --merge --delete-branch           # merge commit, never squash, never rebase
```

Then, before opening the next slot:

```bash
set -euo pipefail
git fetch origin --prune
git switch integration 2>/dev/null || git switch -c integration origin/integration
git reset --hard origin/integration
gh run list --branch integration --limit 1 --json status,conclusion --jq '.[0] | "\(.status) \(.conclusion)"'
# STOP the train if this is not "completed success".
```

### 5.3 L0 promotion commands

```bash
set -euo pipefail
git fetch origin --prune
gh pr create --base main --head integration \
  --title "cycle $(date +%F): integration -> main" \
  --body "Promotion of cycle $(date +%F): full gate green on integration; promoting to main. Merge train order this cycle: L1 L4 L2 L3 L5."
export PR=<pr-number>
gh pr checks $PR
gh pr merge $PR --merge
git fetch origin --tags
git tag -a "cycle/$(date +%F)" origin/main -m "merge train L1 L4 L2 L3 L5 complete"
git push origin "cycle/$(date +%F)"
```

**`--merge`, not `--squash`, not `--rebase`.** Plan decision, not spec-derived, and changeable by L0: a merge commit makes one lane task revertible as a unit with `git revert -m 1 <merge-sha>`, which is the single most-used recovery move when one human is integrating five parallel AI lanes. Squash would destroy per-commit authorship, which spec Section 63.1 relies on ("git history in the control-plane repository as the durable record").

---

## 6. Lane developer command reference

Every operation a lane developer performs, in order. Run them exactly as written.

### O-0 — One-time setup (once per lane, at Phase 0)

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org
export LANE=<1..5>
git clone https://github.com/$ORG/control-plane.git
cd control-plane
git config user.name  "<from DECISION D-BMM-01>"
git config user.email "<from DECISION D-BMM-01>"
git config pull.rebase true
git config rebase.autoStash false
git config merge.conflictstyle zdiff3
git config push.default current
git remote set-head origin -a
git fetch origin --prune
```

PowerShell equivalent for the two exports only:

```powershell
# $env:ORG is read from contracts/project-config.sh (FD-068) — source that file in bash before running
$env:LANE="<1..5>"
```

L4 additionally clones the records repository and configures signing (see **O-11**).

### O-1 — Start a task

```bash
set -euo pipefail
git fetch origin --prune
git switch --no-track -c lane/$LANE/p1-schema-people origin/integration
git log --oneline -1
```

Replace `p1-schema-people` with your task's branch name (§2). `--no-track` is required: it stops `git push` from ever targeting `integration`.

### O-2 — Commit work

Stage explicit paths. Never `git add .`, never `git add -A`.

```bash
set -euo pipefail
git add schemas/registry/people.schema.json
git status --porcelain
git commit -m "L$LANE p1: add people registry schema" -m "Task: L1-P1-003"
```

### O-3 — Local lane-guard pre-check (run before every push)

Use the row for **your** lane. The `OWNS` patterns are transcribed from `PARTITION.md` and are not editable.

| Lane | Repo | Command |
|---|---|---|
| L1 | `control-plane` | `git diff --name-only origin/integration...HEAD | grep -Ev '^(schemas/registry/|schemas/product/|registries/|validators/registry/)'` |
| L2 | `control-plane` | `git diff --name-only origin/integration...HEAD | grep -Ev '^(\.github/workflows/|templates/workflows/|tools/evidence/)'` |
| L3 | `control-plane` | `git diff --name-only origin/integration...HEAD | grep -Ev '^(reconciler/|tools/provision/|validators/drift/)'` |
| L4 | `control-plane` | `git diff --name-only origin/integration...HEAD | grep -Ev '^(schemas/records/|metrics/|tools/records/)'` |
| L4 | `control-plane-records` | no filter — L4 owns the whole repository |
| L5 | `control-plane` | `git diff --name-only origin/integration...HEAD | grep -Ev '^(access/|infra/|ops-vm/|notify/|assets/)'` |

Wrapped so the output is unambiguous — L1 shown; swap in your row's pattern:

```bash
set -euo pipefail
git fetch origin --prune
git diff --name-only origin/integration...HEAD \
  | grep -Ev '^(schemas/registry/|schemas/product/|registries/|validators/registry/)' \
  && echo "STOP: foreign path above. Do not push. File a blocker (O-10)." \
  || echo "PASS: every changed path is owned by L$LANE"
```

`PASS` means zero foreign paths. Any file listed above the `STOP` line is a partition violation and the branch does not get pushed.

### O-4 — Rebase onto `integration` (mandatory immediately before every push that precedes a PR)

```bash
git fetch origin --prune
git rebase origin/integration
```

Clean rebase → continue to O-5. Conflict → go to **O-9**.

### O-5 — Self-verify

```bash
set -euo pipefail
git diff --check
git log --oneline origin/integration..HEAD
make -n validate >/dev/null 2>&1 && make validate \
  || echo "no validate target on integration yet - lane-guard in CI is the gate"
```

`git log --oneline origin/integration..HEAD` must list **only your own commits**, between 1 and 10 of them. If it lists a commit you did not author, your rebase went wrong: `git rebase --abort` was missed, or you branched off the wrong ref. Go to **O-10**.

Then run the task-level self-verify command named in your task card — find its file and line by looking your task id up in `implementation/lanes/L<N>-CONCORDANCE.md` or `implementation/lanes/_ALIASES.tsv` — and keep its output — the PR body requires it verbatim.

### O-6 — Push

First push of the branch:

```bash
git push -u origin HEAD
```

Every push after a rebase:

```bash
git push --force-with-lease origin HEAD
```

`--force-with-lease`, never bare `--force`. It is permitted **only** on `lane/$LANE/*` branches in the repository you own. On `main`, `integration` and the records default branch the ruleset rejects it (§10.8 negative tests N-2, N-5).

### O-7 — Open the pull request

Write `pr-body.md` in your scratch directory (not in the repo) with exactly these fields, then:

```bash
set -euo pipefail
gh pr create --base integration --head "$(git rev-parse --abbrev-ref HEAD)" \
  --title "L$LANE p1: add people registry schema" \
  --body-file <scratch>/pr-body.md
```

`pr-body.md` template — all seven fields required, no field omitted:

```
Lane: L<N>
Task id: <your task id — resolve its file/line via lanes/L<N>-CONCORDANCE.md or lanes/_ALIASES.tsv>
Rebased onto: <output of: git rev-parse --short origin/integration>
Paths touched: <output of: git diff --name-only origin/integration...HEAD>
Lane-guard pre-check: PASS
Self-verify command: <the exact command from the task card>
Self-verify output:
<paste verbatim>
```

Then stop. **Do not merge. Do not enable auto-merge. Do not request another lane's review.** L0 merges in the train slot.

### O-8 — After L0 merges your PR

```bash
set -euo pipefail
git fetch origin --prune
git switch --detach origin/integration
git branch -D lane/$LANE/p1-schema-people
git push origin --delete lane/$LANE/p1-schema-people 2>/dev/null || true
```

`gh pr merge --delete-branch` normally removes the remote branch already; the last line is a no-op when it did.

### O-9 — Rebase conflict

```bash
git status --short | grep -E '^(UU|AA|DU|UD|AU|UA|DD)'
```

Read the paths printed. Then apply §9's authority table:

* **Every conflicted path is owned by your lane** → resolve it yourself:

```bash
# edit each conflicted file, then:
git add <resolved-path>
git rebase --continue
```

* **Any conflicted path is not owned by your lane** → STOP:

```bash
git rebase --abort
git status
```

then file the blocker (O-10). Do not resolve. Do not `--skip`. Do not `--theirs`/`--ours` your way past it.

### O-10 — File a blocker and STOP

See `docs/escalation/BLOCKER.md` for the canonical blocker template.

After filing: do nothing further on that branch until L0 responds. Do not open a second branch for the same task.

### O-11 — L4 only: the records repository

```bash
set -euo pipefail
git clone https://github.com/$ORG/control-plane-records.git
cd control-plane-records
git config user.name  "<from DECISION D-BMM-01>"
git config user.email "<from DECISION D-BMM-01>"
git config gpg.format ssh
git config user.signingkey ~/.ssh/id_ed25519.pub
git config commit.gpgsign true
```

Every commit in this repository must be signed — ruleset **REC-1** carries `required_signatures`, and D107 makes an unsigned or foreign-signed commit on the default branch Blocking drift. Verify before pushing:

```bash
git log --show-signature -1
git verify-commit HEAD && echo "PASS: HEAD is signed" || echo "STOP: HEAD is unsigned - see D-BMM-02"
```

And after L0 merges, verify GitHub agrees:

```bash
gh api /repos/$ORG/control-plane-records/commits/main --jq '.commit.verification | "verified=\(.verified) reason=\(.reason)"'
# must print: verified=true reason=valid
```

Work in this repository still goes through `lane/4/*` branches and a PR merged by L0 in the L4 slot, even though **no ruleset requires a PR here** — requiring one would break the records-writer write path and violate D89. The discipline is procedural, backed by the signature rule and by L0's daily audit (§10.9).

### O-12 — Commands a lane developer must never run

```bash
set -euo pipefail
# NEVER — any of these is an immediate STOP and a blocker issue.
git push --force origin main
git push --force origin integration
git push --force origin lane/<other-lane>/<anything>
git push origin --delete main
git push origin --delete integration
git merge origin/integration          # merging integration INTO a lane branch - see §7
git merge lane/<other-lane>/<anything>
git rebase lane/<other-lane>/<anything>
git cherry-pick <sha-from-another-lane>
git tag -f <any-tag>
git push origin :refs/tags/<any-tag>
gh pr merge <any-pr>
gh pr merge --auto <any-pr>
git config --global user.email <anything other than D-BMM-01's value>
```

---

## 7. Rebase discipline

| Rule | Statement | Check |
|---|---|---|
| R-1 | A lane branch is **rebased** onto `integration`, never merged from it. | `git log --merges origin/integration..HEAD` must print nothing. |
| R-2 | Rebase immediately before opening the PR, and again if L0 asks after the branch falls behind. | `git rev-list --count HEAD..origin/integration` must be `0` at PR time. |
| R-3 | Force-push after rebase uses `--force-with-lease` and targets only `lane/$LANE/*`. | Any other target is rejected by the ruleset. |
| R-4 | A lane never rebases another lane's branch (`PARTITION.md`). | — |
| R-5 | `integration` and `main` are never rebased by anyone. Their history is append-only forward (Section 63.1, invariant 47). | Rulesets CP-1/CP-2 carry `non_fast_forward`. |
| R-6 | A branch that has been rebased more than 3 times in one day is stale work. Abandon it, re-cut from `integration` (O-1), and re-apply. | `git reflog show lane/$LANE/<branch> | grep -c rebase` |

**Why rebase and not merge into the lane branch.** With five lanes, merging `integration` into every lane branch daily produces a history in which no lane's diff is readable in isolation, and `git revert -m 1` on a lane merge stops being a clean undo. R-1 keeps every lane PR a linear, reviewable, revertible strip on top of `integration`. Check R-1 mechanically:

```bash
set -euo pipefail
MERGE_COUNT=0
while IFS= read -r line; do
  echo "$line"
  MERGE_COUNT=$((MERGE_COUNT+1))
done < <(git log --merges --oneline origin/integration..HEAD)
[ "$MERGE_COUNT" -eq 0 ] && echo "PASS: linear lane branch" || echo "STOP: merge commit on a lane branch - see rule R-1"
```

(A zero `MERGE_COUNT` means no merge commits were found — `PASS` fires. `git log` always exits 0 even with no output, so the old `&&`/`||` form was broken: STOP fired unconditionally.)

---

## 8. When a lane is behind

### 8.1 Measure it

```bash
git fetch origin --prune
echo "behind=$(git rev-list --count HEAD..origin/integration) ahead=$(git rev-list --count origin/integration..HEAD)"
```

### 8.2 Thresholds and required action

| `behind` | Meaning | Required action |
|---|---|---|
| `0` | Current | Proceed. This is the only state in which a PR may be opened. |
| `1`–`20` | Normal daily drift | Run **O-4** (rebase), then **O-3** again, then push with `--force-with-lease`. |
| `21`–`100` | One or more cycles missed | Rebase. If the rebase produces a conflict on a foreign path, **abandon the branch**: `git switch --detach origin/integration && git branch -D <branch>`, re-cut with O-1, re-apply the task. Re-applying is cheaper than untangling. |
| `> 100` or `> 2 cycles` | The lane has fallen off the train | **STOP.** File a blocker with title `BLOCKER L<N>: lane behind by <n>`. L0 issues a resync task. The lane opens **no feature PR** until the resync task merges. |

### 8.3 Missing your train slot

A lane whose PR is not green and not mergeable at its slot time is **skipped**. Consequences, binding:

1. The train continues to the next slot. It does not wait, and it does not reorder (§4.3 rule 4).
2. The PR merges in the **same slot position next cycle**, after a fresh rebase — `integration` has moved, so R-2 applies again.
3. Two consecutive missed slots is a blocker, filed by **L0**, not by the lane: the lane is either blocked on something it has not reported or is producing PRs that do not pass the gate.
4. A skipped lane never gets a "catch-up" merge outside the train window. §4.3 rule 6 admits exactly one exception, a P0 revert.

### 8.4 When `integration` is behind `main`

This should be impossible — `main` only ever advances by a merge *from* `integration`. If it happens, a change reached `main` outside the train, which is a protection failure. L0 procedure:

```bash
set -euo pipefail
git fetch origin --prune
git rev-list --count origin/integration..origin/main   # expected: 0
gh api /repos/$ORG/control-plane/commits/main --jq '.commit.author.name + " " + .sha'
```

Non-zero is Blocking drift under Section 53.1 (branch-protection row: *"Alert immediately; block deployment on the affected repository"*). Stop the train, re-run the §10.8 negative tests, and do not resume until N-1 through N-3 pass.

---

## 9. Conflict resolution authority

### 9.1 The structural claim

Under `PARTITION.md` anti-conflict rules 1 and 3 — one owner per path, and no shared mutable file ever — a *content* conflict between two lanes **cannot occur**. Two lanes never touch the same file. Therefore:

> Any content conflict involving a path your lane does not own is evidence of a partition violation, not a merge problem. It is resolved by L0, never by a lane.

### 9.2 Authority table

| Conflict location | Who resolves | How |
|---|---|---|
| Path owned by your lane, conflicting with your own earlier merged work | **You** | O-9 first branch. |
| Path owned by another lane | **L0 only** | Lane aborts the rebase and files a blocker (O-10). |
| `contracts/**` | **L0 only** | A lane needing a contract change files a Contract Change Request (`PARTITION.md` rule 2). A lane never edits `contracts/**`. |
| `CODEOWNERS`, `docs/**`, root files, `Makefile` | **L0 only** | L0-owned paths (`PARTITION.md`). |
| `.github/workflows/**` | **L2 only** for content; **L0 only** for conflict | A workflow-file change pushed by a machine identity is Blocking drift regardless of content (Section 53.1). |
| Records repository, `records/**` / `events/**` | **L4** for build-time scaffolding; **nobody** rewrites history | Rewriting is blocked by REC-1 (D107). If a conflict cannot be resolved by appending, it is Level 5 — escalate. |
| Anything on `integration` or `main` | **L0 only** | — |

### 9.3 The one lane-resolvable case, precisely

You may resolve a conflict only when **all** of these hold, checked by command:

```bash
set -euo pipefail
git status --short | grep -E '^(UU|AA|DU|UD|AU|UA|DD)' | awk '{print $2}' \
  | grep -Ev '^(schemas/registry/|schemas/product/|registries/|validators/registry/)' \
  && echo "STOP: conflict outside L1 paths - abort and file a blocker" \
  || echo "OK: conflict is entirely within L1-owned paths - resolve it"
```

(Substitute your lane's pattern from the O-3 table.)

### 9.4 L0 revert procedure

When a merged lane PR breaks `integration`:

```bash
set -euo pipefail
git fetch origin --prune
git switch integration && git reset --hard origin/integration
git log --merges --oneline -10
export M=<merge-commit-sha>
git revert -m 1 $M
git push origin HEAD:refs/heads/revert/$M
gh pr create --base integration --head "revert/$M" \
  --title "revert: $M (broke integration)" \
  --body "Reverts the L<N> merge $M. Train stopped at slot <k>. Lane re-opens the work on a fresh branch."
gh pr merge <pr-number> --merge --delete-branch
```

The reverted lane re-cuts a fresh branch (O-1) and re-applies. It does **not** revert the revert.

---

## 10. Branch protection and ruleset configuration

**Mechanism choice: repository rulesets, not classic branch protection.** Spec Section 11.4 permits either ("Branch protection or rulesets on private repositories — available on the Team plan"). Rulesets are chosen because Section 53.1's independent control verifier asserts that *"branch protection and ruleset JSON match the committed template"* and that *"the ruleset bypass-actor list is exactly the set Sections 40.1 and 33.2 declare"* — one JSON document per rule set, diffable in git, is the only shape that check can be written against.

**Where the JSON lives.** `docs/build/rulesets/` in `control-plane`. `docs/**` is L0-owned (`PARTITION.md`), which is correct: no lane may edit the configuration of the gate that governs it. The estate-wide branch-protection *template* that the shipped system applies to product repositories is a different artifact, is L5's deliverable under `access/**`, and is out of scope here.

**Materializing the JSON.** Of the seven files named below, only `cp-4-contract-tags.json` has an assigned creation task elsewhere (`C-DOC-CP4-RULES-1`, `lanes/L0-01-phase-0-contracts.md`). For the other six — `cp-1-main-unarmed.json`, `cp-1-main-armed.json`, `cp-2-integration.json`, `cp-3-workflow-tags.json`, `rec-1-append-only.json`, `rec-2-tags-immutable.json` — nothing else creates them: the JSON body given verbatim in the matching subsection (§10.1–10.6) *is* the file. L0 writes it to `docs/build/rulesets/<file>.json` before running the first `gh api` command against it.

**Applying any ruleset:**

```bash
gh api -X POST /repos/$ORG/<repo>/rulesets --input docs/build/rulesets/<file>.json
```

**Updating one in place:**

```bash
gh api /repos/$ORG/<repo>/rulesets --jq '.[] | "\(.id)\t\(.name)"'
gh api -X PUT /repos/$ORG/<repo>/rulesets/<id> --input docs/build/rulesets/<file>.json
```

### 10.1 CP-1 — `control-plane` default branch (`main`), **unarmed** build-time configuration

This is the *unarmed* configuration defined verbatim by spec Section 95.2: *"require-PR and direct-push blocking stay on; required approving reviews is set to 0."* It is legal only while an open bootstrap exception covers it (§11).

`docs/build/rulesets/cp-1-main-unarmed.json`:

```json
{
  "name": "control-plane-main",
  "target": "branch",
  "enforcement": "active",
  "bypass_actors": [],
  "conditions": { "ref_name": { "include": ["~DEFAULT_BRANCH"], "exclude": [] } },
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    { "type": "required_signatures" },
    { "type": "pull_request",
      "parameters": {
        "required_approving_review_count": 0,
        "dismiss_stale_reviews_on_push": true,
        "require_code_owner_review": false,
        "require_last_push_approval": false,
        "required_review_thread_resolution": true,
        "allowed_merge_methods": ["merge"]
      }
    },
    { "type": "required_status_checks",
      "parameters": {
        "strict_required_status_checks_policy": true,
        "required_status_checks": []
      }
    }
  ]
}
```

If your GitHub version rejects `allowed_merge_methods`, delete that key and set the restriction at repository level instead:

```bash
gh api -X PATCH /repos/$ORG/control-plane -F allow_merge_commit=true -F allow_squash_merge=false -F allow_rebase_merge=false
```

### 10.2 CP-1 — **armed** configuration (spec Section 11.3, in full)

Recorded beside the unarmed one from day one, per Section 95.2: *"the armed configuration is recorded beside the unarmed one, so arming a gate is a configuration flip, not a build project."*

`docs/build/rulesets/cp-1-main-armed.json`:

```json
{
  "name": "control-plane-main",
  "target": "branch",
  "enforcement": "active",
  "bypass_actors": [],
  "conditions": { "ref_name": { "include": ["~DEFAULT_BRANCH"], "exclude": [] } },
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    { "type": "required_signatures" },
    { "type": "pull_request",
      "parameters": {
        "required_approving_review_count": 1,
        "dismiss_stale_reviews_on_push": true,
        "require_code_owner_review": true,
        "require_last_push_approval": true,
        "required_review_thread_resolution": true,
        "allowed_merge_methods": ["merge"]
      }
    },
    { "type": "required_status_checks",
      "parameters": {
        "strict_required_status_checks_policy": true,
        "required_status_checks": [
          { "context": "lane-guard" },
          { "context": "control-plane/blocking-drift" }
        ]
      }
    }
  ]
}
```

Each rule maps to a Section 11.3 bullet:

| Section 11.3 bullet | Rule / parameter |
|---|---|
| Require a pull request before merging | `pull_request` rule present |
| Require at least 1 approving review | `required_approving_review_count: 1` |
| Require review from Code Owners (human identities only) | `require_code_owner_review: true` + generated CODEOWNERS |
| Require approval of the most recent reviewable push (invariant 9, no self-approval) | `require_last_push_approval: true` |
| Dismiss stale approvals when new commits are pushed | `dismiss_stale_reviews_on_push: true` |
| Require status checks to pass | `required_status_checks` rule |
| Require branches to be up to date before merging | `strict_required_status_checks_policy: true` |
| Block force pushes and deletions on the default branch | `non_fast_forward` + `deletion` |
| Apply rules to administrators | `bypass_actors: []` |

**The required-status-check list is populated, never guessed.** Spec Section 98.2 is explicit: *"The required-status-check list starts empty per repository and is populated as each check comes into existence… A required check no workflow emits blocks every pull request indefinitely."* Only two contexts are named literally by the sources: `lane-guard` (`PARTITION.md`) and `control-plane/blocking-drift` (Section 11.3), the latter added only at the phase that builds the reconciler (L3). Every other context in Section 11.3's list — tests, build, security scan, contract validation, reviewer-matrix validation, parity check, verification contract — is added by L0 **after** a run has reported it, using the exact string GitHub reports:

```bash
gh api /repos/$ORG/control-plane/commits/integration/check-runs --jq '.check_runs[].name' | sort -u
```

STOP rule for L0: never add a context string that has not appeared in that output.

### 10.3 CP-2 — `control-plane` `integration` branch

Build-time only. No spec section requires it; it exists so that `lane-guard` cannot be bypassed on the way into the cycle, and so `integration` history is as un-rewritable as `main`'s.

`docs/build/rulesets/cp-2-integration.json`:

```json
{
  "name": "control-plane-integration",
  "target": "branch",
  "enforcement": "active",
  "bypass_actors": [],
  "conditions": { "ref_name": { "include": ["refs/heads/integration"], "exclude": [] } },
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    { "type": "required_signatures" },
    { "type": "pull_request",
      "parameters": {
        "required_approving_review_count": 0,
        "dismiss_stale_reviews_on_push": true,
        "require_code_owner_review": false,
        "require_last_push_approval": false,
        "required_review_thread_resolution": false,
        "allowed_merge_methods": ["merge"]
      }
    },
    { "type": "required_status_checks",
      "parameters": {
        "strict_required_status_checks_policy": true,
        "required_status_checks": []
      }
    }
  ]
}
```

**Critical:** neither CP-1 nor CP-2 may ever include `refs/heads/lane/**` in its `conditions.ref_name.include`. Lane branches must stay unprotected or `--force-with-lease` after rebase (O-6) fails and the whole rebase discipline of §7 collapses. Negative test N-4 checks this every cycle.

### 10.4 CP-3 — `control-plane` `workflows/*` tag ruleset

Spec Section 33.2, P0: *"the control-plane repository carries a tag ruleset blocking updates and deletions on `workflows/*` with an empty bypass-actor list."* L2 produces these tags; only L0 pushes them.

`docs/build/rulesets/cp-3-workflow-tags.json`:

```json
{
  "name": "control-plane-workflow-tags",
  "target": "tag",
  "enforcement": "active",
  "bypass_actors": [],
  "conditions": { "ref_name": { "include": ["refs/tags/workflows/*"], "exclude": [] } },
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" }
  ]
}
```

A tag *move* is a non-fast-forward update, so `non_fast_forward` is what blocks it. Because that mapping is a platform behaviour rather than a documented rule name, it is verified by negative test **N-7** rather than assumed — the same discipline Section 11.1 applies to permission semantics.

### 10.5 CP-4 — `control-plane` `contracts/*` tag ruleset

Required by **FD-013** ("name one freeze mechanism as normative and protect it"). The contract-freeze tag was previously unprotected; this ruleset closes that gap (REG-007).

`docs/build/rulesets/cp-4-contract-tags.json`:

```json
{
  "name": "control-plane-contract-tags",
  "target": "tag",
  "enforcement": "active",
  "bypass_actors": [],
  "conditions": { "ref_name": { "include": ["refs/tags/contracts/*"], "exclude": [] } },
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" }
  ]
}
```

**Negative test N-9 — contract tag deletion blocked:**

```bash
set -euo pipefail
cd control-plane
git tag contracts/v1.0.0-probe origin/main
git push origin contracts/v1.0.0-probe >/dev/null 2>&1
git push --force origin :refs/tags/contracts/v1.0.0-probe 2>/dev/null \
  && echo "FAIL N-9: contracts tag deletion accepted — CP-4 not active" \
  || echo "PASS N-9: contracts tag deletion blocked"
git push origin --delete contracts/v1.0.0-probe >/dev/null 2>&1 || true
```

### 10.6 REC-1 and REC-2 — the records repository

Spec Section 40.1 as amended by **D89** and **D107**. Two facts, both binding and both counter-intuitive:

* **No review protection.** D89: *"No protection rules — the store is append-only by convention and by the write path, not by review."* Adding a `pull_request` rule here breaks the records-writer credential and is a spec violation, not a hardening.
* **Rewriting is blocked absolutely, with no bypass actor.** D107: *"A repository ruleset on the records repository's default branch blocks force pushes, branch deletion and tag deletion, with no bypass actor. Ordinary appends are unaffected — they are fast-forward commits, which the ruleset permits."*

`docs/build/rulesets/rec-1-append-only.json`:

```json
{
  "name": "records-append-only",
  "target": "branch",
  "enforcement": "active",
  "bypass_actors": [],
  "conditions": { "ref_name": { "include": ["~DEFAULT_BRANCH"], "exclude": [] } },
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    { "type": "required_signatures" }
  ]
}
```

`docs/build/rulesets/rec-2-tags-immutable.json`:

```json
{
  "name": "records-tags-immutable",
  "target": "tag",
  "enforcement": "active",
  "bypass_actors": [],
  "conditions": { "ref_name": { "include": ["~ALL"], "exclude": [] } },
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" }
  ]
}
```

`required_signatures` implements D107's second control (*"Commits are signed by the writing identity"*). The *foreign-signed-is-Blocking-drift* half is a reconciliation rule owned by L3, not a ruleset, and it needs the allowlist of legitimate signing identities settled by **DECISION D-BMM-02** before it can be written.

D107's third control — the reconciler anchoring the records head SHA and commit count into the protected control-plane repository each run, with a non-descendant head as **Blocking drift, Level 5** (Section 53.2) — is L3 build work, not a ruleset. Where the anchor file lives in `control-plane` was an open partition question; it is already ratified, not open here — see **DECISION D-BMM-03** (superseded by **REG-026**), §12.

Manual verification that the anchor property is even checkable, once both sides exist:

```bash
set -euo pipefail
cd control-plane-records && git fetch origin
git merge-base --is-ancestor <last-anchored-sha> origin/main \
  && echo "PASS: current head descends from the anchor" \
  || echo "LEVEL 5: records history was rewritten - escalate per Section 53.2"
```

### 10.7 The Renovate split (Phase 2 onward, `control-plane` `main` only)

Not applied during the five-lane build — Renovate is installed at Phase 2 (Section 98.2). Recorded here because it changes CP-1's shape and getting it wrong silently disarms `main`.

D89 / Section 33.2: *"a bypass actor is exempt from every rule in the ruleset it is listed on… so a compensator sitting inside the bypassed ruleset compensates for nothing."* Therefore, at Phase 2 CP-1 is **split in two**:

| Ruleset | Carries | `bypass_actors` |
|---|---|---|
| **CP-1A** `control-plane-main-pr-rules` | the `pull_request` rule only (approvals, Code Owner review, most-recent-push approval) | the Renovate app, and nothing else |
| **CP-1B** `control-plane-main-guards` | `deletion`, `non_fast_forward`, and `required_status_checks` including `renovate-path-guard` | **`[]` — empty, always** |

L0 STOP rule, permanent: **never add a bypass actor to a ruleset that carries a required status check, a `deletion` rule, or a `non_fast_forward` rule.** Section 53.1 makes a Renovate bypass ruleset that names any bypass actor on the compensating side **Blocking** drift.

### 10.8 Negative tests — executed, never assumed

Section 95.4 requires the checklist be *"executed for real — including the negative tests."* L0 runs all eight at Phase 0, after any ruleset change, and at every cycle open. Each prints exactly one of `PASS` / `FAIL`.

```bash
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org
cd control-plane && git fetch origin --prune
```

**N-1 — direct push to `main` rejected**

```bash
git switch --detach origin/main && git commit --allow-empty -m "N-1 probe" >/dev/null
git push origin HEAD:refs/heads/main 2>/dev/null && echo "FAIL N-1: direct push to main accepted" || echo "PASS N-1: direct push to main rejected"
```

**N-2 — force push to `main` rejected**

```bash
git push --force origin HEAD:refs/heads/main 2>/dev/null && echo "FAIL N-2" || echo "PASS N-2: force push to main rejected"
```

**N-3 — deletion of `main` rejected**

```bash
git push origin --delete main 2>/dev/null && echo "FAIL N-3" || echo "PASS N-3: main deletion rejected"
```

**N-4 — force push to a lane branch accepted** (the rebase discipline depends on this)

```bash
set -euo pipefail
git push origin HEAD:refs/heads/lane/1/p0-probe >/dev/null 2>&1
git commit --allow-empty -m "N-4 probe 2" >/dev/null
git push --force-with-lease origin HEAD:refs/heads/lane/1/p0-probe 2>/dev/null && echo "PASS N-4: lane branch is force-pushable" || echo "FAIL N-4: lane branches are protected - rebase discipline is broken"
git push origin --delete lane/1/p0-probe >/dev/null 2>&1
```

**N-5 — force push to the records default branch rejected**

```bash
set -euo pipefail
cd ../control-plane-records && git fetch origin
git switch --detach origin/main && git commit --allow-empty -S -m "N-5 probe" >/dev/null
git push --force origin HEAD:refs/heads/main 2>/dev/null && echo "FAIL N-5: records history is rewritable - D107 violated" || echo "PASS N-5: records force push rejected"
```

**N-6 — fast-forward append to the records default branch accepted** (D107: appending must remain unaffected)

```bash
git push origin HEAD:refs/heads/main 2>/dev/null && echo "PASS N-6: append accepted" || echo "FAIL N-6: appends are blocked - the records-writer path is broken"
```

**N-7 — moving a `workflows/*` tag rejected** (Section 33.2)

```bash
set -euo pipefail
cd ../control-plane
git tag -f workflows/v0.0.0-probe origin/main && git push origin workflows/v0.0.0-probe >/dev/null 2>&1
git tag -f workflows/v0.0.0-probe origin/main~1
git push --force origin workflows/v0.0.0-probe 2>/dev/null && echo "FAIL N-7: a workflows tag can be moved - invariant 72 exposure" || echo "PASS N-7: workflows tag is immutable"
git push origin --delete workflows/v0.0.0-probe >/dev/null 2>&1 || true
```

**N-8 — every ruleset that carries a guard has an empty bypass list** (D89, D107, Section 53.1)

```bash
set -euo pipefail
FAIL=0
for R in control-plane control-plane-records; do
  for ID in $(gh api /repos/$ORG/$R/rulesets --jq '.[].id'); do
    while IFS=$'\t' read -r NAME BYPASS RULES; do
      echo "$NAME	$BYPASS	$RULES"
      case "$RULES" in
        *deletion*|*non_fast_forward*|*required_status_checks*|*required_signatures*)
          if [ "$BYPASS" != "bypass=0" ] && [ "$NAME" != "control-plane-main-pr-rules" ]; then
            FAIL=1
          fi
          ;;
      esac
    done < <(gh api /repos/$ORG/$R/rulesets/$ID --jq \
      '"\(.name)\tbypass=\(.bypass_actors|length)\trules=\([.rules[].type]|join(","))"')
  done
done
[ "$FAIL" -eq 0 ] && echo "PASS N-8: every guard ruleset has an empty bypass list" || echo "FAIL N-8: a guard ruleset above carries a non-empty bypass list"
```

The rule enforced above: any row whose `rules` contains `deletion`, `non_fast_forward`, `required_status_checks` or `required_signatures` **must** show `bypass=0`. The only row permitted a non-zero bypass count, and only from Phase 2, is `control-plane-main-pr-rules` (§10.7). Anything else is Blocking drift.

### 10.9 L0 daily audit of the records repository

Because REC-1 deliberately carries no review rule, procedure is the only thing keeping build-time commits on the train. This runs at cycle close:

```bash
cd control-plane-records && git fetch origin
git log origin/main --since=1.day --format='%h %an <%ae> signed=%G? %s'
```

Every row must show a signing identity from the D-BMM-02 allowlist and `signed=G` (good signature). Any other value is Blocking drift under D107 and stops the next cycle.

### 10.10 Retiring `integration`

When the last lane's final PR merges and `integration` → `main` is green:

```bash
set -euo pipefail
gh api /repos/$ORG/control-plane/rulesets --jq '.[] | select(.name=="control-plane-integration") | .id'
gh api -X DELETE /repos/$ORG/control-plane/rulesets/<id>
git push origin --delete integration
git branch -D integration
```

Then re-run N-1, N-2, N-3, N-8. Leaving `integration` in place would leave a second long-lived branch the reconciler's comparison set (Section 53.1) does not know about, and an unowned branch is exactly the shape of drift the system exists to prevent.

---

## 11. The bootstrap exception this model requires

The unarmed CP-1 of §10.1 is legal **only** while an exception covering it is open in `exceptions.yaml`. Spec Section 95.2 supplies the schema and the first entry verbatim as `EXC-BOOT-001` (scope `gate-2-independent-review`, policy `no-self-approval`). L0 authors it in Phase 0 with `affected.repositories` naming `control-plane` and `product-template`, an expiry, an owner and the deactivation trigger *"second context-holding engineer with Write onboarded to the named repositories."*

Binding consequences for this model:

1. Phase 1 ships the minimal `exceptions.yaml` schema validator (expiry, owner, deactivation trigger present). An exception without an expiry is rejected by CI (Section 95.2).
2. The records repository needs **no** bootstrap exception: it carries no review gate by design (D89), so no gate is being relaxed.
3. Arming is a flip, not a project: `gh api -X PUT /repos/$ORG/control-plane/rulesets/<id> --input docs/build/rulesets/cp-1-main-armed.json`, followed by the Section 95.4 verifications at the "2 humans with Write" row, executed for real.
4. The weekly bootstrap log entry — written, during the build, to `docs/plan/bootstrap-log/` in `control-plane`; it moves to `records/bootstrap-log/` in the records repository only at L4's cutover (`lanes/L0-06-bootstrap-mode.md` §L0-06-07; `master/08-progress-tracking.md` §7.4) — records which gates are stubbed and which are armed. Control-plane CI raises **Blocking** drift when the newest entry is older than 7 days (Section 95.4).

**The registry-change lane still binds during the build.** Section 26.4, and Section 95.3 which keeps it binding in bootstrap: an **authority delta** — a diff that adds a capability, adds an assignment type conferring Write, or changes `access_status` — fails CI without a linked decision-record ID in the same commit. This lands mostly on L1 (`registries/**`) and L5 (`access/**`). A lane PR carrying an authority delta with no decision-record ID does not merge, in any cycle, in any slot.

---

## 12. L0 DECISIONS REQUIRED

One item is not determined by `PARTITION.md` or by the specification, and blocks a named Phase-0 step; it may not be resolved by a lane. Two further items were raised here but are already resolved elsewhere — see **D-BMM-01** and **D-BMM-03**, below.

### D-BMM-01 (ratified) — the git identity a lane developer commits under

**Blocks:** O-0, and every commit thereafter. **Why it was not determinable from spec text alone:** spec Section 11.3 requires CODEOWNERS to hold human identities only and Section 98.2's Phase 1 completion check verifies negatively that a machine-account approval cannot satisfy branch protection — but neither text says what identity an AI developer working under a human integrator commits as, because the specification does not contemplate five AI lanes.

This is not open. **Ratified as option A** — see **REG-062** (`lanes/L0-04-decisions-register.md`) for the decision record and the collision note against `lanes/L0-01-phase-0-contracts.md`'s unrelated `D-L0-01`. `manual/05-git-workflow.md` §5 already operationalises it: five machine accounts `lane-1`…`lane-5` (`AGENT_NAME=lane1-bot`, `AGENT_EMAIL=lane1-bot@users.noreply.github.com`, and so on per lane), each with Write on `control-plane`, never appearing in CODEOWNERS (Section 11.3), whose approvals never satisfy a gate. Mirror the five accounts into `people.yaml` under the machine-account class of Section 11.2 as part of Phase-0 bootstrap. The table below is kept for the discarded alternatives' record only:

| Option | Mechanism | Consequence |
|---|---|---|
| **A — ratified** | Five GitHub machine accounts, `lane-1`…`lane-5`, each with Write on `control-plane` | Clean per-lane attribution and per-lane revocation. These accounts must never appear in CODEOWNERS (Section 11.3), and their approvals must never satisfy a gate. Costs five org seats; each needs 2FA under the organisation-enforced rule (Section 11.2). |
| B (rejected) | All lanes commit as L0's human identity, with `Co-authored-by: lane-N` and a `Lane: N` trailer | No extra seats, no machine identity anywhere. Attribution lives in trailers, so `git log --author` stops distinguishing lanes and L0's identity authors work L0 did not write — which weakens the Section 63.1 history. |
| C (rejected) | One shared machine account `lane-bot`, lane distinguished only by branch prefix and trailer | One seat; loses per-lane revocation, which is the property that makes a compromised lane containable. |

### DECISION D-BMM-02 — the build-time signing-identity allowlist for the records repository

**Blocks:** O-11, ruleset REC-1's usefulness, and L3's foreign-signature detector. **Why it is not determinable here:** D107 says *"The records-writer signs every commit, and a commit on the default branch that is unsigned, or signed by any other identity, is Blocking drift."* During the build the records-writer credential does not exist yet — L4 and L0 are the writers. Read literally, every build-time commit is Blocking drift on the day the detector activates.

| Option | Mechanism | Consequence |
|---|---|---|
| **A** | Allowlist is `{records-writer, L0, lane-4}`, permanently | Simple; permanently widens D107's "one identity" property to three, which is the property D107 exists to buy. |
| **B** | Allowlist is `{records-writer}` only. Build-time commits are covered by a dated bootstrap exception naming `L0` and `lane-4`, with deactivation trigger "records-writer credential issued and first append succeeds" | Preserves D107 exactly. Requires the exception and its expiry. Consistent with Section 95.2's construction. |
| **C** | Detector activates only from the records-writer's first commit forward; earlier history is anchored once and exempted | Cheapest, but leaves an unverifiable prefix in the store whose immutability invariant 47 asserts. |

**Recommendation, for L0 to accept or reject:** **B**. It is the option that keeps D107's text true and puts the widening behind an expiry, which is what Section 95.2 exists for. Whichever is chosen, the allowlist is written down in one place and §10.9's audit reads it.

### D-BMM-03 (superseded) — where the records head-SHA anchor lives inside `control-plane`

This was raised here as an open, three-option choice for L0 to accept or reject. It is not open: the decision has already been ratified elsewhere. **REG-026** (`lanes/L0-04-decisions-register.md`) and `lanes/L3-03-canary-and-integrity.md` (line 6140) record the anchor destination as `derived/anchors/records-head.yaml`, write-scope allowlist `["derived/**"]`, with `derived/**` now owned by L0 — already built into `reconciler/config/anchoring.yaml` with a verified SHA-256. None of the three options this subsection originally listed (`reconciler/state/...`, `tools/records/anchor/...`, a new `state/...` root path) names that ratified path. Do not re-decide this here; read REG-026 for the credential and write-scope questions it also closes.

---

## 13. Acceptance criteria for this model

Checkable by L0 at Phase 0 close, and at every cycle open. Each line is a command whose output is unambiguous.

| # | Criterion | Command | Pass output |
|---|---|---|---|
| 1 | `main` is the default branch of `control-plane` | `gh api /repos/$ORG/control-plane --jq .default_branch` | `main` |
| 2 | `integration` exists and descends from `main` | `git merge-base --is-ancestor origin/main origin/integration && echo PASS` | `PASS` |
| 3 | All six rulesets exist | `gh api /repos/$ORG/control-plane/rulesets --jq '[.[].name]'` then the records repo | contains `control-plane-main`, `control-plane-integration`, `control-plane-workflow-tags`, `control-plane-contract-tags`; records repo contains `records-append-only`, `records-tags-immutable` |
| 4 | No guard ruleset has a bypass actor | N-8 (§10.8) | every guard row shows `bypass=0` |
| 5 | Negative tests pass | N-1 … N-7, N-9 (§10.8) | eight `PASS` lines |
| 6 | No lane branch is older than one working day | `git for-each-ref --sort=committerdate --format='%(committerdate:relative) %(refname:short)' refs/remotes/origin/lane` | no entry older than `1 day ago` |
| 7 | No merge commit exists on any open lane branch | `for B in $(git for-each-ref --format='%(refname:short)' refs/remotes/origin/lane); do echo "$B $(git log --merges --oneline origin/integration..$B | wc -l)"; done` | every count is `0` |
| 8 | `integration` is never behind `main` | `git rev-list --count origin/integration..origin/main` | `0` |
| 9 | The bootstrap exception covering unarmed CP-1 is open and unexpired | `grep -A3 'EXC-BOOT-001' registries/exceptions.yaml` (path per L1's lane file) | an `expiry` in the future |
| 10 | The bootstrap log is fresh | `git log -1 --format=%cr -- docs/plan/bootstrap-log/` in `control-plane` (or `records/bootstrap-log/` in the records repo, after L4's cutover — §11 item 4) | less than 7 days |
| 11 | Every commit on the records default branch is signed by an allowlisted identity | §10.9 | every row `signed=G` |
| 12 | The merge train ran in order last cycle | `git log origin/integration --merges --oneline -5` | the 5 lane merges appear newest-first, in the order L5, L3, L2, L4, L1 |

---

## 14. Source index

Every claim above traces to one of these. Nothing here is invented.

| Claim | Source |
|---|---|
| Repositories, lane path ownership, anti-conflict rules, merge-train order, dependency rationale, AI developer profile | `implementation/PARTITION.md` (FROZEN) |
| GitHub permission semantics; approval requires Write; Read approval does not satisfy protection | Spec §11.1 |
| Organisation base Read, Teams-derived Write, machine-account class, 2FA | Spec §11.2 |
| Branch protection checklist for main (the nine bullets of §10.2's mapping table); `control-plane/blocking-drift` | Spec §11.3 |
| Rulesets available on the Team plan; Enterprise features not depended on | Spec §11.4, D73 |
| Registry-change lane; authority-delta gate; reconciler declared repair scope | Spec §26.4 |
| Merge is mechanical, not a decision | Spec §27 |
| `workflows/*` tag ruleset with empty bypass-actor list | Spec §33.2 |
| Renovate bypass split across two rulesets | Spec §33.2, D74 as amended by D89 |
| Five secret tiers; records repository separate; no machine bypass actor on control-plane | Spec §40.1, D76 as superseded in part by D89 |
| Append-only enforced: no-bypass ruleset blocking force push and deletion, signed commits, head-SHA anchor, Level 5 on non-descendant head | Spec §40.1, D107 |
| Declared-vs-actual comparison rows; branch-protection drift blocks deployment; independent control verifier reads ruleset JSON and bypass lists | Spec §53.1 |
| Five reconciliation levels; Level 5 = escalate | Spec §53.2 |
| Immutable history; git history as the durable record; append-only for state, decisions, approvals, records | Spec §63.1, invariant 47 (§101.7) |
| Bootstrap Mode; unarmed vs armed configuration; `EXC-BOOT-001`; activation checklist; weekly bootstrap log with 7-day Blocking detector | Spec §95.1–95.4 |
| Phase 1 branch protection; required-status-check list starts empty and is populated per phase; default-branch completion check | Spec §98.2 |
| Subsystem-to-lane mapping and the dependency spine | Spec §99.2 |
| Design-open items must be logged, not invented | Spec §99.3 |
| Evidence-plumbing gap: Section 97 stores built before anything reads them | Spec §99.6 risk 2 |
| No self-approval, enforced by most-recent-push approval | Spec §101.2 invariant 9 |
| History is append-only for state, decisions, approvals and records | Spec §101.7 invariant 47 |
