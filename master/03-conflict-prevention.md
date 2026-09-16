# 03 — Conflict Prevention

**The mechanical guarantees that five parallel agents cannot collide.**

Scope of this file: the repository-level machinery that makes five simultaneous lane branches
structurally unable to produce a merge conflict, a lost write, or a silent cross-lane edit.
It implements the five "Non-negotiable anti-conflict rules" of
`C:/D_Drive/PS/MultiProduct/Code/implementation/PARTITION.md` and nothing else. The lane
partition itself is frozen and is never redesigned here.

Read this file before you open your first branch. Every command below is copy-pasteable.
Every rule below is enforced by a check whose output is a pass/fail line, not a judgment.

---

## 0. The five guarantees, and what enforces each

| # | PARTITION rule | Mechanism in this file | Enforcing check | Fails how |
|---|---|---|---|---|
| 1 | One owner per path | `lane-paths.tsv` + longest-match resolution | `lane-guard` rule R1 | Required status check red; merge button disabled |
| 2 | Contract-first, `contracts/**` frozen | `contracts/CONTRACTS.lock` + Contract Change Request | `lane-guard` rule R2 | Red, with the CCR link in the error |
| 3 | No shared mutable file | `.github/lane-append-only.map` + directory-per-item | `lane-guard` rule R3 | Red on any modify/delete under an add-only prefix |
| 4 | No cross-lane imports | Generated artifacts are build outputs, never committed | `lane-guard` rule R5 | Red on any committed generated path |
| 5 | Additive-only within a lane | Lanes may not delete or rename base-branch files | `lane-guard` rule R4 | Red; removal goes to L0 |

All five run in **one** workflow, produce **one** required status check named `lane-guard`, and
collect **all** violations before failing, so a lane sees its whole problem in one run.

**Classification: fail-closed** (invariant 80 — "Every control is explicitly classified
fail-closed or fail-open"). A path that matches no ownership rule is a violation, not a pass. A
missing control file is a violation, not a pass. A runner without `gh` or `jq` is a violation,
not a pass. There is no configuration of this guard in which an unrecognised situation merges.

**Where this sits in the spec.** Section 99.3 enumerates the seven design-open items the
implementer must invent; build-time repository partitioning is not among them, because the
specification does not address it at all — it specifies the *product* of the build, not the
concurrency model of the build. Every open point in this file is therefore an implementation-plan
decision belonging to L0 (collected in Section 8), never a spec gap and never something a lane
agent decides.

---

## 1. Rule 1 — One owner per path

### 1.1 The statement

A lane may write only to paths its lane owns. Not "should not" — cannot: the PR fails and the
merge button is disabled. There is no reviewer discretion, no "small fix in someone else's
directory", no exception label. The single legitimate route into another lane's tree is a
request to L0 (Section 4).

This is the rule that does the actual work. Merge conflicts require two writers on one file.
Remove the second writer and the conflict class ceases to exist — not is detected, ceases to exist.

### 1.2 The ownership map — `lane-paths.tsv`

Transcribed directly from the PARTITION table. This file is written by L0 in Phase 0 and is
never edited by a lane (it lives under `.github/`, which resolves to L0; see 1.3).

```
# lane-paths.tsv
# Authoritative machine-readable form of the PARTITION path table.
# Format:  <lane> <whitespace> <rule>
#   rule ending in "/"  -> directory prefix rule (matches that path and everything under it)
#   rule ":root:"       -> any file at the repository root (no "/" in the path)
#   any other rule      -> exact file path
# Resolution: the LONGEST matching rule wins; an exact-file rule always beats a prefix rule.
# Unmatched path -> UNOWNED -> violation. Fail-closed by construction.
# Owner of this file: L0. A lane that edits it fails R1 against itself.

# ---- L0  integrator -------------------------------------------------------
L0    :root:
L0    contracts/
L0    docs/
L0    CODEOWNERS
L0    .github/
L0    tools/lane-guard/
L0    .github/workflows/lane-guard.yml

# ---- L1  Registries & Contracts (subsystems A, B) -------------------------
L1    schemas/registry/
L1    schemas/product/
L1    registries/
L1    validators/registry/

# ---- L2  Pipeline & Evidence (subsystems E, F) ----------------------------
L2    .github/workflows/
L2    templates/workflows/
L2    tools/evidence/

# ---- L3  Reconciler & Provisioning (subsystems C, D) ----------------------
L3    reconciler/
L3    tools/provision/
L3    validators/drift/

# ---- L4  Records, Events & Metrics (subsystems I, N) ----------------------
L4    schemas/records/
L4    metrics/
L4    tools/records/

# ---- L5  Access, Infra & Ops (subsystems K, L, M, Q, R) -------------------
L5    access/
L5    infra/
L5    ops-vm/
L5    notify/
L5    assets/
```

Notes that matter for a reader with no repo context:

* `Makefile` and every other root file resolve to L0 through `:root:`. PARTITION lists
  "root files" for L0; `:root:` is that clause, mechanised.
* `.github/` resolves to L0 and `.github/workflows/` resolves to L2, because the longer rule
  wins. That is exactly the PARTITION split: L2 owns `.github/workflows/**` and nothing else
  inside `.github/`. Issue templates, the ownership maps and CODEOWNERS are L0's.
* `.github/workflows/lane-guard.yml` is the one exact-file exception inside L2's prefix: the
  exact rule beats the prefix rule, so this one file resolves to L0 while every other workflow
  stays L2's (D-REQ-3, closed — REG-002 / FD-003, Option A).
* `validators/` has no rule of its own. `validators/registry/` is L1 and `validators/drift/` is
  L3; a new `validators/anything-else/` is UNOWNED and fails. That is intended.
* `schemas/` has no rule of its own for the same reason: `schemas/registry/` and
  `schemas/product/` are L1, `schemas/records/` is L4, anything else fails closed.

No lane guard on `control-plane-records` — `L0D-LG-6` ratified (REG-055). The records repository has its own no-bypass ruleset (D107).

### 1.3 The lane-guard workflow — complete and runnable

Path: `.github/workflows/lane-guard.yml`.

Two design points you must not "simplify" away:

1. **`pull_request_target`, not `pull_request`.** On `pull_request_target` GitHub runs the
   workflow file *as it exists on the base branch*. A lane cannot weaken its own guard by editing
   `lane-guard.yml` on its branch — the edit has no effect until L0 merges it. This is the
   mechanical answer to "who guards the guard", and it holds regardless of what CODEOWNERS says.
2. **The PR head is never checked out.** The usual `pull_request_target` hazard is executing
   untrusted head code with the base token. This workflow checks out nothing and executes nothing
   from the PR; it reads the changed-file list and three control files from the base SHA over the
   API. Token permissions are read-only.

There is also no third-party action used anywhere in it, so invariant 85 ("third-party GitHub
Actions are pinned to full commit SHAs") has nothing to bind to here — there is no action SHA to
pin, and therefore no pin to go stale. `gh`, `jq`, `awk`, `sed` and `base64` are preinstalled on
GitHub-hosted `ubuntu-latest`.

```yaml
# .github/workflows/lane-guard.yml
# Owner: L0. Enforces PARTITION.md rules 1-5. Fail-closed (invariant 80).
name: lane-guard

on:
  pull_request_target:
    types: [opened, synchronize, reopened, ready_for_review]
    branches:
      - integration
      - main

permissions:
  contents: read
  pull-requests: read

concurrency:
  group: lane-guard-${{ github.event.pull_request.number }}
  cancel-in-progress: true

defaults:
  run:
    shell: bash

jobs:
  lane-guard:
    name: lane-guard
    runs-on: ubuntu-latest
    timeout-minutes: 10
    env:
      GH_TOKEN: ${{ github.token }}
      REPO: ${{ github.repository }}
      PR_NUMBER: ${{ github.event.pull_request.number }}
      HEAD_REF: ${{ github.event.pull_request.head.ref }}
      BASE_REF: ${{ github.event.pull_request.base.ref }}
      BASE_SHA: ${{ github.event.pull_request.base.sha }}
      CHANGED_FILES: ${{ github.event.pull_request.changed_files }}

    steps:
      - name: R0a preflight - runner has the tools this guard needs
        run: |
          set -euo pipefail
          for t in gh jq base64 awk sed sort wc; do
            command -v "$t" >/dev/null 2>&1 || {
              echo "::error::lane-guard: required tool '$t' is not on PATH on this runner."
              echo "STOP. Do not merge. Open a blocker issue labelled 'lane-guard' naming the runner label."
              exit 1; }
          done
          if [ "${CHANGED_FILES:-0}" -gt 2000 ]; then
            echo "::error::lane-guard: this pull request changes ${CHANGED_FILES} files. The GitHub pull-request files API truncates at 3000 and this guard refuses to run on a file set it cannot see in full."
            echo "STOP. Split the pull request into task-sized branches (PARTITION: one branch per task, short-lived, < 1 day)."
            exit 1
          fi

      - name: R0b fetch the control files from the BASE branch
        run: |
          set -euo pipefail
          fetch() {
            local path="$1" out="$2" raw
            raw="$(gh api "repos/${REPO}/contents/${path}?ref=${BASE_SHA}" --jq '.content')" || {
              echo "::error::lane-guard: cannot read '${path}' from base sha ${BASE_SHA}. Fail-closed."
              echo "STOP. Open a blocker issue labelled 'lane-guard'."; exit 1; }
            printf '%s' "$raw" | base64 -d > "$out"
            [ -s "$out" ] || {
              echo "::error::lane-guard: '${path}' is empty at base sha ${BASE_SHA}, or exceeds the 1 MB contents-API inline limit. Fail-closed."
              exit 1; }
          }
          fetch "lane-paths.tsv"   lane-paths.raw
          fetch ".github/lane-append-only.map" lane-append-only.map
          fetch ".github/lane-generated.map"   lane-generated.map
          awk 'BEGIN{FS="[ \t]+"} /^[ \t]*#/{next} NF>=2 {print $1"\t"$2}' lane-paths.raw   > ownership.tsv
          awk 'BEGIN{FS="[ \t]+"} /^[ \t]*#/{next} NF>=2 {print $1"\t"$2}' lane-append-only.map > appendonly.tsv
          awk '/^[ \t]*#/{next} NF>=1 {print $1}'                          lane-generated.map   > generated.txt
          [ -s ownership.tsv ] || { echo "::error::lane-guard: ownership map parsed to zero rules. Fail-closed."; exit 1; }
          echo "ownership rules: $(wc -l < ownership.tsv)"

      - name: R0c derive the lane from the head branch
        run: |
          set -euo pipefail
          if [ "$BASE_REF" = "main" ] && [ "$HEAD_REF" != "integration" ]; then
            echo "::error::lane-guard: only 'integration' may open a pull request into 'main'. Head branch is '${HEAD_REF}'."
            echo "STOP. Retarget this pull request at 'integration'."
            exit 1
          fi
          case "$HEAD_REF" in
            lane/1/*)          LANE=L1 ;;
            lane/2/*)          LANE=L2 ;;
            lane/3/*)          LANE=L3 ;;
            lane/4/*)          LANE=L4 ;;
            lane/5/*)          LANE=L5 ;;
            l0/*|integration)  LANE=L0 ;;
            *)
              echo "::error::lane-guard: head branch '${HEAD_REF}' is not a recognised lane branch."
              echo "Allowed: lane/1/<phase>-<task> .. lane/5/<phase>-<task>, l0/<task>, integration."
              echo "STOP. Rename the branch: git branch -m lane/<N>/<phase>-<task> && git push -u origin HEAD && git push origin --delete ${HEAD_REF}"
              exit 1 ;;
          esac
          echo "LANE=${LANE}" >> "$GITHUB_ENV"
          echo "lane resolved: ${LANE}"

      - name: R1-R5 evaluate every changed path
        run: |
          set -euo pipefail

          gh api --paginate "repos/${REPO}/pulls/${PR_NUMBER}/files?per_page=100" \
            --jq '.[] | [.status, .filename, (.previous_filename // "-")] | @tsv' > files.tsv
          [ -s files.tsv ] || {
            echo "::error::lane-guard: this pull request changes no files. Fail-closed."; exit 1; }
          : > violations.txt

          owner_of() {
            local p="$1" best="UNOWNED" bestlen=-1 lane rule len
            while IFS=$'\t' read -r lane rule; do
              case "$rule" in
                ":root:")
                  case "$p" in */*) continue ;; esac
                  len=0 ;;
                */)
                  case "$p" in "$rule"*) len=${#rule} ;; *) continue ;; esac ;;
                *)
                  [ "$p" = "$rule" ] || continue
                  len=$(( ${#rule} + 1000 )) ;;
              esac
              if [ "$len" -gt "$bestlen" ]; then bestlen="$len"; best="$lane"; fi
            done < ownership.tsv
            printf '%s' "$best"
          }

          mode_for() {
            local p="$1" mode="-" bestlen=-1 m pref len
            while IFS=$'\t' read -r m pref; do
              case "$p" in "$pref"*) len=${#pref} ;; *) continue ;; esac
              if [ "$len" -gt "$bestlen" ]; then bestlen="$len"; mode="$m"; fi
            done < appendonly.tsv
            printf '%s' "$mode"
          }

          is_generated() {
            local p="$1" pref
            while read -r pref; do
              if [ "${pref%/}" != "$pref" ]; then
                case "$p" in "$pref"*) return 0 ;; esac
              else
                if [ "$p" = "$pref" ]; then return 0; fi
              fi
            done < generated.txt
            return 1
          }

          while IFS=$'\t' read -r status path prev; do
            owner="$(owner_of "$path")"

            # ---- R1  one owner per path -------------------------------------
            if [ "$owner" = "UNOWNED" ]; then
              echo "R1 UNOWNED    ${path} :: no rule in lane-paths.tsv matches this path. Only L0 adds rules." >> violations.txt
            elif [ "$LANE" != "L0" ] && [ "$owner" != "$LANE" ]; then
              echo "R1 FOREIGN    ${path} :: owned by ${owner}; this branch is ${LANE}. Revert the file and file a request to L0." >> violations.txt
            fi
            if [ "$prev" != "-" ]; then
              powner="$(owner_of "$prev")"
              if [ "$LANE" != "L0" ] && [ "$powner" != "$LANE" ]; then
                echo "R1 FOREIGN    ${prev} :: renamed to ${path}; the source path is owned by ${powner}." >> violations.txt
              fi
            fi

            # ---- R2  contracts/ is frozen -----------------------------------
            case "$path" in
              contracts/*)
                if [ "$LANE" != "L0" ]; then
                  echo "R2 CONTRACT   ${path} :: contracts/ is frozen. Lanes never edit it. File a Contract Change Request (.github/ISSUE_TEMPLATE/contract-change-request.yml) and STOP this task." >> violations.txt
                fi ;;
            esac

            # ---- R3  directory-per-item / append-only -----------------------
            mode="$(mode_for "$path")"
            case "$mode" in
              add-only)
                case "$status" in
                  added) : ;;
                  renamed)
                    if [ "${prev#records/decisions/pending/}" != "$prev" ] && [ "${path#records/decisions/}" != "$path" ] && [ "${path#records/decisions/pending/}" = "$path" ]; then
                      : # the one sanctioned move: a pending decision becomes a decided one, i.e. leaves pending/ (Section 97.2)
                    else
                      echo "R3 APPEND     ${path} :: add-only path (status=${status}). One file per item; existing items are immutable (Section 97.3, invariant 47)." >> violations.txt
                    fi ;;
                  *)
                    echo "R3 APPEND     ${path} :: add-only path (status=${status}). Write a NEW file; never modify or delete an existing one (Section 97.3, invariant 47)." >> violations.txt ;;
                esac ;;
              no-delete)
                case "$status" in
                  removed|renamed)
                    echo "R3 APPEND     ${path} :: no-delete path (status=${status}). A retired identifier is marked retired in place, never removed (Section 97.3)." >> violations.txt ;;
                esac ;;
            esac

            # ---- R4  additive-only: lanes never remove base-branch files ----
            case "$status" in
              removed|renamed)
                if [ "$LANE" != "L0" ]; then
                  if [ "$prev" != "-" ]; then whatwas=" (was ${prev})"; else whatwas=""; fi
                  echo "R4 REMOVAL    ${path}${whatwas} :: lanes do not delete or rename files that exist on ${BASE_REF}. File a Removal Request to L0 (Section 5.3)." >> violations.txt
                fi ;;
            esac

            # ---- R5  generated artifacts are never committed ----------------
            if is_generated "$path"; then
              echo "R5 GENERATED  ${path} :: generated build output. It is produced by 'make' in CI and published as an artifact; it is never committed. Remove it and add nothing to .gitignore (it is already there)." >> violations.txt
            fi

          done < files.tsv

      - name: Verdict
        if: always()
        run: |
          set -euo pipefail
          [ -f violations.txt ] || { echo "::error::lane-guard: evaluation step did not complete. Fail-closed."; exit 1; }
          n="$(wc -l < violations.txt | tr -d ' ')"
          {
            echo "## lane-guard"
            echo ""
            echo "| field | value |"
            echo "| --- | --- |"
            echo "| head branch | \`${HEAD_REF}\` |"
            echo "| resolved lane | \`${LANE:-unresolved}\` |"
            echo "| base | \`${BASE_REF}\` |"
            echo "| files changed | $(wc -l < files.tsv | tr -d ' ') |"
            echo "| violations | ${n} |"
          } >> "$GITHUB_STEP_SUMMARY"
          if [ "$n" -gt 0 ]; then
            {
              echo ""
              echo '```'
              cat violations.txt
              echo '```'
            } >> "$GITHUB_STEP_SUMMARY"
            while IFS= read -r line; do echo "::error::lane-guard: ${line}"; done < violations.txt
            echo ""
            echo "lane-guard FAILED with ${n} violation(s)."
            echo "STOP RULE: do not edit lane-paths.tsv, do not retarget the base branch, do not ask for an admin merge."
            echo "Revert the offending paths, or open a blocker issue labelled 'lane-guard' quoting the lines above."
            exit 1
          fi
          echo "lane-guard PASSED: ${LANE} touched only ${LANE}-owned paths."
```

### 1.4 The local copy — run it before you push

Same rules, run against your working branch, so a lane never learns about a violation from CI.
Path: `tools/lane-guard/pre-push-check.sh` (L0-owned; lanes run it, never edit it).

```bash
#!/usr/bin/env bash
set -euo pipefail
# tools/lane-guard/pre-push-check.sh - local mirror of the lane-guard R1 rule.
# Usage:  bash tools/lane-guard/pre-push-check.sh [base-ref]     (default: origin/integration)
BASE="${1:-origin/integration}"
HEAD_REF="$(git rev-parse --abbrev-ref HEAD)"
case "$HEAD_REF" in
  lane/1/*) LANE=L1 ;; lane/2/*) LANE=L2 ;; lane/3/*) LANE=L3 ;;
  lane/4/*) LANE=L4 ;; lane/5/*) LANE=L5 ;; l0/*|integration) LANE=L0 ;;
  *) echo "STOP: branch '$HEAD_REF' is not a lane branch."; exit 1 ;;
esac
awk 'BEGIN{FS="[ \t]+"} /^[ \t]*#/{next} NF>=2 {print $1"\t"$2}' lane-paths.tsv > /tmp/own.tsv
fail=0
while IFS= read -r p; do
  best=UNOWNED; bestlen=-1
  while IFS=$'\t' read -r lane rule; do
    case "$rule" in
      ":root:") case "$p" in */*) continue ;; esac; len=0 ;;
      */) case "$p" in "$rule"*) len=${#rule} ;; *) continue ;; esac ;;
      *) [ "$p" = "$rule" ] || continue; len=$(( ${#rule} + 1000 )) ;;
    esac
    if [ "$len" -gt "$bestlen" ]; then bestlen=$len; best=$lane; fi
  done < /tmp/own.tsv
  if [ "$LANE" != "L0" ] && [ "$best" != "$LANE" ]; then
    echo "FOREIGN  $p  (owner=$best, you=$LANE)"; fail=1
  fi
done < <(git diff --name-only --diff-filter=ACMRD "$(git merge-base "$BASE" HEAD)"..HEAD)
echo "local lane-guard finished for $LANE on $HEAD_REF"
exit "$fail"
```

Self-verify, unambiguous output:

```bash
bash tools/lane-guard/pre-push-check.sh; echo "exit=$?"
# PASS looks like exactly one line, then exit=0:
#   local lane-guard finished for L3 on lane/3/p3-reconcile-v0
# FAIL prints one "FOREIGN  <path>" line per offending file above that line, then exit=1.
```

### 1.5 Branch protection that makes the check binding

Run once per repository, by L0, on the day `lane-guard.yml` first lands. Consistent with the
Phase 1 completion check of Section 98.2 — "the required-status-check list starts empty per
repository and is populated as each check comes into existence".

**Mechanism: a repository ruleset, not classic branch protection** — `master/02-branch-merge-model.md`
§10 already settles this for `control-plane` (Section 53.1's independent verifier needs one
diffable JSON document per rule, which only rulesets provide) and ships the CP-2 ruleset for this
exact branch, `docs/build/rulesets/cp-2-integration.json`. Apply it, then arm it with the
`lane-guard` context now that the check exists:

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org
gh api -X POST "repos/${ORG}/control-plane/rulesets" \
  --input docs/build/rulesets/cp-2-integration.json
RS_ID="$(gh api "repos/${ORG}/control-plane/rulesets" \
  --jq '.[] | select(.name=="control-plane-integration") | .id')"
jq '(.rules[] | select(.type=="required_status_checks") | .parameters.required_status_checks) = [{"context":"lane-guard"}]' \
  docs/build/rulesets/cp-2-integration.json > /tmp/cp-2-integration.armed.json
gh api -X PUT "repos/${ORG}/control-plane/rulesets/${RS_ID}" \
  --input /tmp/cp-2-integration.armed.json
```

`strict_required_status_checks_policy: true` (already in `cp-2-integration.json`) is load-bearing
here: it forces every lane branch to be up to date with `integration` before it can merge, which is
the mechanical form of the PARTITION rule "rebased on `integration` before PR".
`require_last_push_approval` is invariant 9 (no self-approval, enforced by requiring approval of the
most recent reviewable push) — armed on `main` per `master/02` §10.2; `integration`'s own
`pull_request` rule ships with `required_approving_review_count: 0` because build-time human
headcount does not cover a second reviewed branch (`master/02` §10.3).

Verify it took:

```bash
set -euo pipefail
RS_ID="$(gh api "repos/${ORG}/control-plane/rulesets" \
  --jq '.[] | select(.name=="control-plane-integration") | .id')"
gh api "repos/${ORG}/control-plane/rulesets/${RS_ID}" \
  --jq '{checks: [.rules[] | select(.type=="required_status_checks") | .parameters.required_status_checks[].context],
         strict: (.rules[] | select(.type=="required_status_checks") | .parameters.strict_required_status_checks_policy),
         enforcement: .enforcement}'
# expected exactly:
# {"checks":["lane-guard"],"strict":true,"enforcement":"active"}
```

### 1.6 CODEOWNERS for the build repository

CODEOWNERS here is **routing and visibility**; `lane-guard` is **enforcement**. Do not confuse
them, and do not weaken the guard because CODEOWNERS looks like it covers the case — CODEOWNERS
requests reviewers, it does not block writes.

```
# CODEOWNERS   (control-plane, build phase). Owner: L0.
# Human identities only - Section 98.2 Phase 1 completion check: an approval from a machine
# account does not satisfy branch protection, and CODEOWNERS is generated to contain human
# identities only. The five lane agents are machine actors: they author, they never approve.
*                       @bendrohit-eng
```

That single line is deliberate. Only L0 approves in the build repository, so no AI developer can
approve another AI developer's branch, and invariant 9 holds without depending on any agent's
restraint. Per-lane CODEOWNERS lines are added only if and when a second human joins a lane.

### 1.7 The lane-guard canary — proving the guard is not vacuously passing

Modelled on AT-102 (the seeded reconciliation canary) and EC-109 (a silently-vacuous run): a
guard that finds nothing is assumed broken, never assumed clean.

L0 opens one permanently-open pull request at Phase 0 and never merges it:

```bash
set -euo pipefail
gh label create "lane-guard-canary" --repo "${ORG}/control-plane" --color "#B60205" \
  --description "The permanently-open PR proving lane-guard is not vacuously passing" --force
git checkout -b lane/1/canary-do-not-merge integration
mkdir -p access && echo "lane-guard canary. Do not merge. Do not delete." > access/CANARY.md
git add access/CANARY.md
git commit -m "canary: L1 branch writing an L5-owned path; lane-guard MUST fail this"
git push -u origin lane/1/canary-do-not-merge
gh pr create --base integration --title "DO NOT MERGE: lane-guard canary" \
  --body "Permanently open. lane-guard must report R1 FOREIGN on access/CANARY.md. A green run here means the guard is broken." \
  --label lane-guard-canary
```

Daily assertion (L0 runs it, or a scheduled workflow does):

```bash
set -euo pipefail
CANARY=$(gh pr list --repo "${ORG}/control-plane" --label lane-guard-canary --json number --jq '.[0].number')
STATE=$(gh pr checks "$CANARY" --repo "${ORG}/control-plane" --json name,state \
        --jq '[.[] | select(.name=="lane-guard") | .state] | first' || true)
if [ "$STATE" = "FAILURE" ]; then echo "CANARY OK: lane-guard is live and failing the seeded violation"
else echo "CANARY BROKEN: lane-guard state=$STATE. STOP ALL MERGES. Open a blocker issue."; fi
```

Unambiguous output: `CANARY OK: ...` or `CANARY BROKEN: ...`. Nothing else.

---

## 2. Rule 2 — No shared mutable file, and directory-per-item

### 2.1 Why this is the second half of the guarantee

Rule 1 stops two lanes writing the same path. It does not stop two *tasks inside one lane*, or two
successive PRs from the same lane, colliding on one file — and it does not stop `git` from
producing a conflict when two branches append at the same offset in the same list. The spec
already answers this for events, in Section 97.3: an event is "written as its own file, one file
per event, never a concurrent append to a shared period file, so parallel workflow runs never
contend for the same file; period views are derived by aggregation."

That sentence is the whole convention. This file generalises it from workflow runs to build lanes:
**one file per item, everywhere, and the aggregate is computed, never stored.** Invariant 46 —
"Derived data is computed, never hand-maintained" — makes the aggregate side of it non-optional
anyway.

### 2.2 The banned shapes

| Banned shape | Why it breaks | Replace with |
|---|---|---|
| A list in one file that many items append to (`event_types:`, `products:`, `metrics:`) | Two branches append at the same offset; `git` conflicts every time | One file per entry in a directory; assemble at build time |
| An index or manifest of everything (`INDEX.md`, `registry-of-registries.yaml`) | Every task touches it | Enumerate the directory; there is no index |
| A shared changelog appended per task | Same offset, every task | One file per change under `docs/changes/<date>-<slug>.md` (L0) |
| A shared fixtures file | Two lanes add fixtures | `contracts/fixtures/<contract>/<case>.yaml`, one file per case |
| A `merge=union` git attribute or merge driver | Silently interleaves two lanes' lines into a file that still parses as YAML and is wrong | Nothing. Never configure one. |

Check that no union-merge driver has been introduced, which would defeat the conflict signal
without defeating the bug:

```bash
git config --get-regexp 'merge\..*\.driver' && echo "VIOLATION: custom merge driver configured" || echo "OK: no custom merge driver configured"
grep -rn 'merge=union' .gitattributes 2>/dev/null && echo "VIOLATION: union merge configured" || echo "OK: no union merge in .gitattributes"
```

Expected output, both lines: `OK: ...`.

### 2.3 The directory-per-item conventions, per lane

Every lane writes new files into a directory whose naming grammar is fixed. Two agents following
the grammar cannot produce the same filename unless they are doing the same task, which the task
list prevents.

| Lane | Item | Directory | Filename grammar | Example |
|---|---|---|---|---|
| L1 | Registry schema | `schemas/registry/` | `<entity>.v<N>.schema.json` | `schemas/registry/people.v1.schema.json` |
| L1 | Product-contract schema | `schemas/product/` | `product.v<N>.schema.json` | `schemas/product/product.v1.schema.json` |
| L1 | Registry entry (per person, role, tool) | `registries/<entity>/` | `<id>.yaml` | `registries/people/lead-1.yaml` |
| L1 | Event-type declaration | `registries/platform/event-types/` | `<event_type>.yaml` | `registries/platform/event-types/plan_approved.yaml` |
| L1 | Validator | `validators/registry/` | `<rule-id>.<ext>` | `validators/registry/assignment-names-live-person.py` |
| L2 | Reusable workflow | `.github/workflows/` | `<verb>-<object>.yml` | `.github/workflows/deploy-production.yml` |
| L2 | Workflow template | `templates/workflows/` | `<verb>-<object>.yml` | `templates/workflows/restore-production.yml` |
| L2 | Evidence tool | `tools/evidence/` | `<tool-name>/` (one directory per tool) | `tools/evidence/verify-digest-chain/` |
| L3 | Reconciler check | `reconciler/checks/` | `<drift-class>-<subject>.<ext>` | `reconciler/checks/permission-team-membership.py` |
| L3 | Provisioning operation | `tools/provision/` | `<operation>/` | `tools/provision/create-product/` |
| L3 | Drift validator | `validators/drift/` | `<rule-id>.<ext>` | `validators/drift/expired-assignment.py` |
| L4 | Record schema | `schemas/records/` | `<store>.v<N>.schema.json` | `schemas/records/incidents.v1.schema.json` |
| L4 | Metric definition | `metrics/<metric-id>/` | `metric.yaml` + `query.sql` | `metrics/restore-test-currency/metric.yaml` |
| L4 | Record | `records/<store>/` (records repo) | `<YYYY-MM-DD>-<product>-<nnn>.yaml` | `records/incidents/2026-09-14-solvox-001.yaml` |
| L4 | Event | `events/<YYYY-MM-DD>/` (records repo) | `EVT-<YYYY-MM-DD>-<nnnnnn>.yaml` | `events/2026-09-14/EVT-2026-09-14-000317.yaml` |
| L5 | Access rule | `access/` | `<subject>-<scope>.yaml` | `access/teams-write-derivation.yaml` |
| L5 | Infra unit | `infra/<unit>/` | one directory per unit | `infra/ops-vm-compose/` |
| L5 | Notification route | `notify/routes/` | `<signal-or-channel>.yaml` | `notify/routes/sig-13.yaml` |

The record and event paths and filename shapes are the spec's own (Section 97.2 store table and
the Section 97.3 event envelope example); the rest apply the same convention to build artifacts.

### 2.4 `.github/lane-append-only.map`

Two modes. `add-only` means files may only be created; `no-delete` means files may be created and
modified but never removed or renamed.

```
# .github/lane-append-only.map
# Owner: L0.  <mode> <path prefix>
#   add-only   : only status=added is permitted under this prefix
#   no-delete  : status=removed and status=renamed are forbidden under this prefix
# Basis: Section 97.3 (one file per event, never a concurrent append) and
#        invariant 47 (history is append-only for state, decisions, approvals and records).

add-only     events/
add-only     records/
no-delete    registries/platform/event-types/
no-delete    schemas/records/
no-delete    schemas/registry/
no-delete    schemas/product/
```

`schemas/*` are `no-delete` rather than `add-only` because a schema version is amended in place
until it ships and then frozen by version — but a shipped version is never removed, which is
invariant 73 ("Contract schemas are versioned, and simultaneous fleet migration is never
required") stated as a file rule. Event-type fragments are `no-delete` because Section 97.3 says
retiring an identifier "marks it retired in the enum and never removes it".

The one sanctioned rename in the whole system is hard-coded in the guard: a pending decision
moving from `records/decisions/pending/` to `records/decisions/`, which Section 97.2 specifies.

**The `events/` and `records/` lines above cannot fire from this file's mechanism.** Both prefixes
exist only inside `control-plane-records` (Section 1.2's note at line 120; PARTITION.md), and the
`lane-guard` workflow of Section 1.3 runs only against pull requests into `control-plane`'s
`integration`/`main`. `events/**` and `records/**` therefore never appear in a changed-file list R3
evaluates, and this map's `add-only` rows for them are dead weight, not enforcement. The actual
append-only guarantee for that repository is a different mechanism — D89 ("append-only by
convention and by the write path, not by review") plus the no-bypass branch and tag rulesets of D107
(`lanes/L4-01-records-repo.md` tasks `L4-P1-T05`/`T06`) — and is out of this file's scope. See the
added row in Section 7.

### 2.5 Assembly: the spec's single-file artifacts, without the single file

Some spec artifacts genuinely are one file — `platform.yaml` holds the event-type enum
(Section 97.3), `people.yaml` holds the roster (Section 7). Those files are **build outputs**,
assembled from the per-item directories, and are **never committed**. Consumers get them the way
PARTITION rule 4 requires: "through `contracts/**` or a published artifact — never by reaching
into its source tree."

```
# .github/lane-generated.map
# Owner: L0. Paths listed here are build outputs. Committing one fails lane-guard rule R5.
build/
dist/
platform.yaml
people.yaml
roles.yaml
topology.yaml
docs/metrics.md
```

The assembler for the event enum, as an L0-owned `Makefile` target (`Makefile` is a root file,
therefore L0's):

```bash
set -euo pipefail
# make build/platform.yaml  -- deterministic, sorted, no hand-maintained list anywhere
mkdir -p build
{ echo "platform_version: 1"
  echo "event_types:"
  sed -n 's/^id: //p' registries/platform/event-types/*.yaml | LC_ALL=C sort | sed 's/^/  - /'
} > build/platform.yaml
```

`platform.yaml` is the one root-named artifact whose per-item files are themselves the whole
content (an event-type fragment has nothing beyond `id`, `introduced`, `retired`). `people.yaml`
and `roles.yaml` assemble the same way from Section 2.3's other directory-per-item trees
(`registries/people/<login>.yaml`, `registries/roles/<name>.yaml`), but each fragment there is a
full record, not one id — so the assembler nests the fragment wholesale rather than extracting a
field:

```bash
set -euo pipefail
# make build/people.yaml, build/roles.yaml  -- same discipline, full-record fragments
mkdir -p build
for entity in people roles; do
  { echo "${entity}_version: 1"
    echo "${entity}:"
    find "registries/${entity}" -maxdepth 1 -name '*.yaml' 2>/dev/null | LC_ALL=C sort | \
      while IFS= read -r f; do
        printf '  -\n'; sed 's/^/    /' "$f"
      done
  } > "build/${entity}.yaml"
done
```

Sort the *filenames*, not the assembled content — each fragment is a multi-line record, and piping
that through `sort` (as an earlier draft of this assembler did) sorts every line independently,
scrambling record boundaries instead of ordering whole records.

`topology.yaml` is not assembled here: this file names no `registries/topology/` directory-per-item
convention anywhere (Section 2.3's table has no `topology` row), so — unlike `people` and `roles` —
there is no source tree yet for a Makefile target to read. It stays listed in
`.github/lane-generated.map` as a future generated artifact, but naming its source directory is an
L0 decision this document does not make on its own (an addition to D-REQ-2, not covered by REG-008
as recorded).

Verify the platform assembly is total — every fragment reached the artifact, and nothing else did:

```bash
set -euo pipefail
diff <(sed -n 's/^id: //p' registries/platform/event-types/*.yaml | LC_ALL=C sort) \
     <(sed -n 's/^  - //p' build/platform.yaml) \
  && echo "ASSEMBLY OK: fragment set == artifact set" \
  || echo "ASSEMBLY BROKEN: fragments and artifact disagree. STOP."
```

Because `build/platform.yaml` is regenerated and never stored, two lanes adding two event types on
two branches produce two new files and zero conflicts, and the assembled artifact contains both.
Section 6 demonstrates exactly this, runnably.

---

## 3. Rule 3 — Contract-first, with `contracts/**` frozen

### 3.1 What `contracts/` is

`contracts/` is the interface surface every lane codes against and no lane owns. L0 authors it in
Phase 0, before any lane branch exists, and freezes it. It contains, at minimum:

| Path | Contents | Consumed by |
|---|---|---|
| `contracts/schemas/` | The JSON Schema `$id`s and shapes every registry, record and event must satisfy | L1, L4 |
| `contracts/event-types/` | The canonical `event_type` identifier strings and their payload field lists (Section 97.3: "Event types are identifiers, not prose") | L1, L2, L4 |
| `contracts/records/` | The record envelope: `record_schema_version`, `id`, `product`, `timestamp` (Section 97.2) and the event envelope of Section 97.3 | L2, L4 |
| `contracts/workflow-io/` | Inputs, outputs and required status-check context names of each reusable workflow | L2, L3 |
| `contracts/cli/` | Argument and exit-code contracts for `create-product`, `add-person`, `record-decision`, `check-commitment` (Section 99.2 named tools) | L3 |
| `contracts/fixtures/<contract>/<case>.yaml` | One file per case; the golden inputs every lane tests against | all |
| `contracts/CONTRACTS.lock` | sha256 of every file above | the guard |

A lane never needs another lane's source tree, because everything it needs to compile, validate
and test against is here, plus the fixtures. That is the whole reason five agents with no repo
context can work simultaneously without reading each other's work.

### 3.2 The freeze mechanism

Two independent locks, because one is a convention and the other is arithmetic.

**Lock 1 — the guard.** `contracts/` resolves to L0 in the ownership map, and rule R2 names the
CCR procedure in its error message so a lane agent that trips it knows the next step without
asking.

**Lock 2 — the lockfile.** L0 generates it at freeze time:

```bash
set -euo pipefail
# L0, once, at the end of Phase 0, on the integration branch:
find contracts -type f ! -name CONTRACTS.lock -print0 \
  | LC_ALL=C sort -z \
  | xargs -0 sha256sum > contracts/CONTRACTS.lock
git add contracts/CONTRACTS.lock
git commit -m "L0: freeze contracts/ at Phase 0"
```

Anyone, any time, on any branch:

```bash
set -euo pipefail
sha256sum -c contracts/CONTRACTS.lock --quiet \
  && echo "CONTRACTS FROZEN: intact" \
  || echo "CONTRACTS BROKEN: contracts/ has changed without a Contract Change Request. STOP."
```

Exactly one of those two lines is printed. Wire it as a second step in whatever CI job L0 runs on
`integration`, and run it locally before starting any task.

### 3.3 What a lane codes against while waiting

Nothing in `contracts/` moves during a lane's task. If a lane's task cannot be completed against
the frozen contract, the task is wrong or the contract is wrong, and both answers belong to L0.
The lane does not invent an adapter, a shim, a "temporary local copy of the schema", or a
`TODO: reconcile with contract later`. It files the CCR and stops. This is the "no judgment
authority" clause of the PARTITION AI-developer profile, made concrete.

---

## 4. The Contract Change Request procedure

### 4.1 When a lane files one

File a CCR when, and only when, all three are true:

1. The task cannot be completed as written against the frozen contract.
2. The blocker is in `contracts/**` — a missing field, a wrong type, an absent event type, a
   fixture that contradicts the schema.
3. You have re-read the contract file and the task's acceptance criteria once.

Do not file a CCR for: a bug in your own lane's code; a foreign-path edit you want to make
(that is a different request, Section 5.3); a preference about naming.

### 4.2 The form — `.github/ISSUE_TEMPLATE/contract-change-request.yml`

The template's `labels:` line below creates neither label on issue creation — GitHub requires both
to already exist on the repository, or `gh issue create`/the web form's implied create fails.
`blocker` is created by the Phase 0 bootstrap (Section 1.7's canary needs `lane-guard-canary` the
same way). L0 creates `ccr` alongside it, once, before this template can be used:

```bash
set -euo pipefail
gh label create "ccr" --repo "${ORG}/control-plane" --color "#1D76DB" \
  --description "Contract Change Request against contracts/**" --force
```

```yaml
# .github/ISSUE_TEMPLATE/contract-change-request.yml   Owner: L0
name: Contract Change Request
description: Request a change to a frozen file under contracts/. Only L0 executes it.
title: "CCR: <contract path> - <one line>"
labels: ["ccr", "blocker"]
body:
  - type: input
    id: lane
    attributes: { label: Lane, description: "L1..L5", placeholder: "L3" }
    validations: { required: true }
  - type: input
    id: branch
    attributes: { label: Blocked branch, placeholder: "lane/3/p3-reconcile-v0" }
    validations: { required: true }
  - type: input
    id: contract_path
    attributes: { label: Contract file, placeholder: "contracts/schemas/drift-finding.v1.schema.json" }
    validations: { required: true }
  - type: textarea
    id: blocked_by
    attributes:
      label: What the task cannot do
      description: The exact command or assertion that fails, and its output. No paraphrase.
    validations: { required: true }
  - type: dropdown
    id: shape
    attributes:
      label: Change shape
      options:
        - additive (new optional field / new enum member / new fixture)
        - breaking (field removed, type changed, required field added)
    validations: { required: true }
  - type: textarea
    id: proposed
    attributes:
      label: Proposed contract text
      description: The literal replacement text or diff. Not a description of it.
    validations: { required: true }
  - type: textarea
    id: blast_radius
    attributes:
      label: Which other lanes consume this contract
      description: From contracts/CONSUMERS.md. If unknown, write "unknown - L0 to determine".
    validations: { required: true }
  - type: checkboxes
    id: stop
    attributes:
      label: Stop rule acknowledged
      options:
        - label: "I have stopped work on this task and will not proceed until L0 closes this CCR."
          required: true
```

### 4.3 Lifecycle

| Step | Actor | Action | Output | Target |
|---|---|---|---|---|
| 1 | Lane | File the CCR, stop the task, move the task card to Blocked | Issue with labels `ccr`,`blocker` | Immediately on discovery |
| 2 | L0 | Triage: reject / additive / breaking | Comment on the issue naming the shape | Same working day |
| 3a | L0 (additive) | Edit `contracts/**` on `l0/ccr-<n>`, regenerate `CONTRACTS.lock`, merge to `integration` | New contract + lock | Same working day |
| 3b | L0 (breaking) | Author `contracts/<name>.v<N+1>` **alongside** `v<N>`; both remain present | Two live versions | Next working day |
| 4 | L0 | Append a decision record (Section 97.2 `records/decisions/`) and an event-type-free note in `docs/changes/` | Decision record id | With step 3 |
| 5 | L0 | Comment `CCR CLOSED. Rebase and resume.` and close the issue | Issue closed | With step 3 |
| 6 | Lane | `git fetch && git rebase origin/integration`, re-run the local guard, resume | Green `lane-guard` | On notification |

**Breaking changes never mutate a version in place.** Invariant 73 — versioned contracts, both
versions supported, no simultaneous fleet migration — applies to the build's own contracts exactly
as it applies to the estate's. That is what makes step 3b safe with five branches in flight: a
lane that has not rebased still compiles against `v<N>`, which is still there.

### 4.4 L0's execution commands

```bash
set -euo pipefail
# additive CCR #<n>
git checkout -b "l0/ccr-<n>" integration
# ... apply the proposed contract text verbatim ...
find contracts -type f ! -name CONTRACTS.lock -print0 | LC_ALL=C sort -z | xargs -0 sha256sum > contracts/CONTRACTS.lock
git add contracts && git commit -m "L0: CCR #<n> - <contract path> additive change"
git push -u origin "l0/ccr-<n>"
gh pr create --base integration --title "L0: CCR #<n>" --body "Closes #<n>"
```

```bash
set -euo pipefail
# breaking CCR #<n>: v2 lands beside v1, v1 is untouched
git checkout -b "l0/ccr-<n>" integration
cp contracts/schemas/<name>.v1.schema.json contracts/schemas/<name>.v2.schema.json
# ... edit only the v2 file ...
find contracts -type f ! -name CONTRACTS.lock -print0 | LC_ALL=C sort -z | xargs -0 sha256sum > contracts/CONTRACTS.lock
git add contracts && git commit -m "L0: CCR #<n> - <name> v2 added; v1 retained"
```

### 4.5 The lane's STOP rule, verbatim

> If `lane-guard` reports `R2 CONTRACT`, or `sha256sum -c contracts/CONTRACTS.lock --quiet` fails,
> or the task cannot be completed against the frozen contract: **stop**. Do not edit `contracts/`.
> Do not copy a contract file into your lane's tree. Do not proceed to the next task on the branch.
> File the Contract Change Request, comment the CCR number on your task issue, and wait.

### 4.6 A temporary waiver is an exception with an expiry, or it does not exist

If L0 ever needs to let a lane past the guard for a bounded reason, it is recorded in
`registries/exceptions.yaml` (D-REQ-2, closed — REG-008: committed directly, not a generated build
output) with an expiry, an owner and a deactivation trigger — invariant 77 ("Every
exception has an expiry; an exception without one is invalid and fails CI") and Section 54.2. It
inherits SIG-39 and cannot age quietly. There is no `[skip lane-guard]` commit token, no admin
merge convention, and `enforce_admins` is left `false` deliberately so that the one bypass path is
visible in the audit log rather than hidden in a commit message.

---

## 5. Rule 4 — Additive-only discipline

### 5.1 The ladder

Take the highest rung that does the job. Every rung down is a rung closer to a conflict.

| Rung | Action | Conflict risk | Allowed |
|---|---|---|---|
| 1 | Create a new file in your lane's directory-per-item tree | Zero | Always |
| 2 | Append to a file only your lane's current task touches | Near zero | Always |
| 3 | Modify an existing file inside your owned paths | Real, within-lane only | Yes, inside owned paths |
| 4 | Delete or rename a file that exists on `integration` | High | **No** — L0 only (R4) |
| 5 | Touch a foreign path | Certain | **Never** (R1) |

### 5.2 Why deletion is L0's alone

A delete-modify pair is the one conflict class the ownership map cannot prevent, because it can
arise between a lane's branch and `integration` itself: L0 amends a file on `integration` while a
lane deletes it. Git reports `CONFLICT (modify/delete)` and there is no automatic answer. Removing
the delete from lanes removes the class. Rule R4 does that mechanically.

### 5.3 The Removal Request

Same channel as the CCR, different label. One comment is enough:

```bash
set -euo pipefail
gh label create "removal-request" --repo "${ORG}/control-plane" --color "#B60205" \
  --description "Requests L0 delete or rename a base-branch file (Rule R4)" --force
gh issue create --repo "${ORG}/control-plane" \
  --title "Removal Request: <path>" \
  --label removal-request,blocker \
  --body "Lane: L<N>
Branch: lane/<N>/<task>
Path to remove: <path>
Why it must go: <one sentence>
What replaces it: <path of the replacement, or 'nothing'>
I have stopped this task."
```

L0 executes the removal on `l0/<task>` into `integration`; the lane rebases and resumes.

### 5.4 Rebase discipline

PARTITION: "A lane NEVER merges another lane's branch. A lane NEVER rebases another lane's
branch." The only two git operations a lane performs against a branch it does not own are `fetch`
and `rebase onto origin/integration`:

```bash
set -euo pipefail
# the ONLY refresh a lane ever runs
git fetch origin
git rebase origin/integration
bash tools/lane-guard/pre-push-check.sh
git push --force-with-lease
```

`--force-with-lease`, never `--force`: it refuses if someone else has pushed to your branch, which
on a five-agent repo is the difference between a rejected push and a silently destroyed commit.

Forbidden, and why:

```bash
set -euo pipefail
git merge origin/lane/2/...        # FORBIDDEN: imports another lane's history into yours
git rebase origin/lane/4/...       # FORBIDDEN: rewrites onto a branch you do not own
git push origin HEAD:lane/5/...    # FORBIDDEN: writes another lane's branch
git push --force                   # FORBIDDEN: use --force-with-lease
```

---

## 6. Worked example — the merge that would have conflicted

### 6.1 The change

Two units of work land in the same cycle:

* **W1, restore-test evidence.** Needs the event type for "restore test executed with result"
  (Section 97.3 taxonomy) and the metric for restore-test currency (SIG-17, Section 97.2
  `records/restore-tests/`).
* **W2, eval-regression signalling.** Needs the event type for "eval regression detected"
  (Section 97.3 taxonomy) and the metric for eval pass rate (SIG-42, Section 97.2 `records/eval/`).

The identifier strings below (`restore_test_executed`, `eval_regression_detected`) are the shapes
the Section 97.3 rule mandates — lower-case, underscore-separated — applied to that section's
prose. The canonical strings themselves are a `contracts/event-types/` deliverable authored by L0
in Phase 0; a lane never coins one.

### 6.2 Naive split — by feature — conflicts

Two agents, one per work item, each touching the two files their feature needs:
`platform.yaml` (the event enum) and `docs/metrics.md` (the metric table).

| Branch | Files touched |
|---|---|
| `feat/restore-test` | `platform.yaml`, `docs/metrics.md` |
| `feat/eval-regression` | `platform.yaml`, `docs/metrics.md` |

Both append at the end of the same list, in the same file, from the same base. The second merge
conflicts on both files. Nothing either agent did was wrong; the split was.

### 6.3 Partitioned split — by artifact class — does not

The frozen partition splits by *what kind of artifact it is*, not by *what feature it serves*.
Event-type declarations are `registries/**`, which is L1. Metric definitions are `metrics/**`,
which is L4. So the same two work items become two branches with **zero overlapping paths**:

| Branch | Files touched | Owner |
|---|---|---|
| `lane/1/p1-event-types` | `registries/platform/event-types/restore_test_executed.yaml`, `registries/platform/event-types/eval_regression_detected.yaml` | L1 |
| `lane/4/p1-metric-defs` | `metrics/restore-test-currency/metric.yaml`, `metrics/eval-pass-rate/metric.yaml` | L4 |

Four new files, four distinct paths, no file modified. `platform.yaml` and `docs/metrics.md` do
not exist in git at all — they are assembled at build time from the fragments (Section 2.5), so
there is no shared list for anyone to append to.

### 6.4 Reproduce it

Copy-paste the whole block. It builds two throwaway repositories under your temp directory, runs
both scenarios, and prints the two verdicts. Nothing outside the temp directory is touched.

```bash
#!/usr/bin/env bash
set -euo pipefail
DEMO="${TMPDIR:-/tmp}/lane-conflict-demo"
rm -rf "$DEMO"; mkdir -p "$DEMO"

echo "================ PART 1: naive split (by feature) ================"
mkdir -p "$DEMO/naive"; cd "$DEMO/naive"
git init -q -b integration
git config user.email demo@example.invalid; git config user.name demo
mkdir -p docs
cat > platform.yaml <<'YAML'
platform_version: 1
event_types:
  - plan_approved
  - production_deployed
YAML
cat > docs/metrics.md <<'MD'
| metric | source store |
| --- | --- |
| deployment frequency | records/deployments/ |
MD
git add -A; git commit -qm "baseline"

git checkout -q -b feat/restore-test
printf '  - restore_test_executed\n' >> platform.yaml
printf '| restore-test currency | records/restore-tests/ |\n' >> docs/metrics.md
git commit -qam "W1 restore-test evidence"

git checkout -q integration
git checkout -q -b feat/eval-regression
printf '  - eval_regression_detected\n' >> platform.yaml
printf '| eval pass rate | records/eval/ |\n' >> docs/metrics.md
git commit -qam "W2 eval regression signal"

git checkout -q integration
git merge -q --no-edit feat/restore-test
git merge --no-edit feat/eval-regression >/dev/null 2>&1
CONFLICTED="$(git diff --name-only --diff-filter=U | tr '\n' ' ')"
if [ -n "$CONFLICTED" ]; then
  echo "NAIVE RESULT: CONFLICT on: $CONFLICTED"
else
  echo "NAIVE RESULT: unexpectedly clean - check your git version"
fi
git merge --abort >/dev/null 2>&1

echo "================ PART 2: the frozen partition ===================="
mkdir -p "$DEMO/partitioned"; cd "$DEMO/partitioned"
git init -q -b integration
git config user.email demo@example.invalid; git config user.name demo
mkdir -p registries/platform/event-types metrics/deployment-frequency
printf 'id: plan_approved\nintroduced: 2026-09-01\nretired: null\n'      > registries/platform/event-types/plan_approved.yaml
printf 'id: production_deployed\nintroduced: 2026-09-01\nretired: null\n' > registries/platform/event-types/production_deployed.yaml
printf 'id: deployment_frequency\nsource_store: records/deployments/\n'   > metrics/deployment-frequency/metric.yaml
cat > assemble.sh <<'SH'
#!/usr/bin/env sh
# In the real repository this is the L0-owned Makefile target "build/platform.yaml".
mkdir -p build
{ echo "platform_version: 1"; echo "event_types:"
  sed -n 's/^id: //p' registries/platform/event-types/*.yaml | LC_ALL=C sort | sed 's/^/  - /'
} > build/platform.yaml
SH
chmod +x assemble.sh
printf 'build/\n' > .gitignore
git add -A; git commit -qm "baseline"

git checkout -q -b lane/1/p1-event-types
printf 'id: restore_test_executed\nintroduced: 2026-09-14\nretired: null\n'   > registries/platform/event-types/restore_test_executed.yaml
printf 'id: eval_regression_detected\nintroduced: 2026-09-14\nretired: null\n' > registries/platform/event-types/eval_regression_detected.yaml
git add -A; git commit -qm "L1: two new event-type declarations"

git checkout -q integration
git checkout -q -b lane/4/p1-metric-defs
mkdir -p metrics/restore-test-currency metrics/eval-pass-rate
printf 'id: restore_test_currency\nsource_store: records/restore-tests/\nsignal: SIG-17\n' > metrics/restore-test-currency/metric.yaml
printf 'id: eval_pass_rate\nsource_store: records/eval/\nsignal: SIG-42\n'                 > metrics/eval-pass-rate/metric.yaml
git add -A; git commit -qm "L4: two new metric definitions"

git checkout -q integration
git merge -q --no-edit lane/1/p1-event-types
git merge --no-edit lane/4/p1-metric-defs >/dev/null 2>&1
if [ -z "$(git ls-files -u)" ]; then
  echo "PARTITIONED RESULT: CLEAN - zero unmerged paths"
else
  echo "PARTITIONED RESULT: CONFLICT - the partition is not being followed"
fi
./assemble.sh
echo "--- assembled build/platform.yaml ---"
cat build/platform.yaml
```

Expected output, exactly (on Windows Git Bash, git additionally emits
`warning: ... LF will be replaced by CRLF` lines; they are harmless and do not affect the result):

```
================ PART 1: naive split (by feature) ================
NAIVE RESULT: CONFLICT on: docs/metrics.md platform.yaml
================ PART 2: the frozen partition ====================
PARTITIONED RESULT: CLEAN - zero unmerged paths
--- assembled build/platform.yaml ---
platform_version: 1
event_types:
  - eval_regression_detected
  - plan_approved
  - production_deployed
  - restore_test_executed
```

### 6.5 The four properties that produced the clean merge

1. **Disjoint paths.** L1 wrote only `registries/**`; L4 wrote only `metrics/**`. Rule R1 would
   have failed either branch that strayed. No overlap, no conflict — arithmetic, not care.
2. **New files only.** Four `added`, zero `modified`. Git's three-way merge has no hunk to resolve
   when neither side edits a common line.
3. **No shared list.** The enum both work items extend does not exist as a committed file. It is
   assembled, sorted, from one file per entry.
4. **Split by artifact class, not by feature.** This is the counter-intuitive one and it is the
   whole design. A feature-split gives every agent a slice of every file; an artifact-split gives
   every agent whole files nobody else can name. Features are assembled at the end, by the build,
   from parts that never met.

---

## 7. What this machinery does *not* prevent

Say the limits out loud, because a guard trusted beyond its scope is worse than no guard.

| Not prevented | Detected by | Owner |
|---|---|---|
| Two tasks *in the same lane* editing the same owned file on two branches | Ordinary git conflict at rebase time | The lane; serialise its own tasks |
| A lane writing a semantically wrong file in a path it legitimately owns | Schema validation, unit tests, L0 review | L0 |
| A lane depending on another lane's *behaviour* rather than its contract | `contracts/CONSUMERS.md` review at merge-train time | L0 |
| A lane consuming another lane's source tree by reading it (not writing it) | Nothing mechanical; PARTITION rule 4 is a review item | L0 |
| Merge-train ordering (L1 → L4 → L2 → L3 → L5) | Not enforced by the guard; L0 sequences the merges | L0 |
| A modify/delete under `events/**` or `records/**` (Section 2.4's `add-only` rows for them) | Nothing in this file — those paths live in `control-plane-records`, which `lane-guard` never scans; D89's write-path convention plus D107's no-bypass rulesets (`lanes/L4-01-records-repo.md`) | L0 / L4 |
| Paths belonging to subsystems the partition does not assign to a lane | Rule R1 `UNOWNED`, fail-closed — see D-REQ-4 | L0 |

The last row deserves its name in full: the PARTITION lane table assigns subsystems A, B, C, D, E,
F, I, K, L, M, N, Q and R. Section 99.2 also defines subsystems **G** (plan-checker and Gate 1
tooling), **H** (dashboards and views), **J** (background machine layer), **O** (governance
registries and jobs) and **P** (people intelligence engine). No lane owns a path for those, so the
first PR that touches one fails R1 as `UNOWNED`. That is the guard working correctly. Resolving it
is D-REQ-4.

---

## 8. L0 DECISION REQUIRED

None of these is a specification gap — Section 99.3 lists the seven design-open items and
repository partitioning is not among them, because the spec does not address the build's
concurrency model. Each is an implementation-plan decision. Each blocks a line of
`lane-paths.tsv`, which blocks the guard, which blocks Phase 0 completion. No lane
agent resolves any of them.

Three of the four are already closed elsewhere in this corpus (`lanes/L0-04-decisions-register.md`)
and this document's map, workflow and text above are written against the recorded outcome:
D-REQ-1 (`REG-010`), D-REQ-2 (`REG-008`) and D-REQ-3 (`REG-002`/`FD-003`). Only D-REQ-4 remains open.

---

> ### D-REQ-1: L0's own branch prefix — **CLOSED**, recorded as `REG-010`
>
> **Why it had to be decided:** the guard derives the lane from the head branch name. PARTITION
> defines `lane/N/*` for lanes and names `main` and `integration` for L0, but does not name the
> branch L0 opens its own PRs from — and L0 must open PRs (branch protection forbids direct pushes
> to `integration`).
>
> **Decided: Option A**, `l0/<task>` (`lanes/L0-04-decisions-register.md` `REG-010`, closed). This
> requires no further edit here — Section 1.3's `R0c` (`l0/*|integration) LANE=L0`) and Section
> 1.4's local mirror both already implement it. The options below are kept for the record.
> - **A (assumed by the workflow as written):** `l0/<task>` — e.g. `l0/ccr-14`,
>   `l0/freeze-contracts`. One line in the `case` statement, already present.
> - **B:** L0 pushes directly to `integration` with `enforce_admins: false` letting an admin
>   bypass. Costs the audit trail and contradicts the Section 98.2 Phase 1 completion check ("no
>   direct human push to any default branch succeeds").
> - **C:** L0 uses `lane/0/*` for symmetry. Requires the `case` arm and the ownership map's L0
>   rules to be re-keyed to `L0`; cosmetic only.
>
> **Recommendation:** A. It is what the workflow above implements, it costs nothing, and it keeps
> every change to `integration` reviewable.
>
> **Unblocks:** `R0c derive the lane from the head branch`.

---

> ### D-REQ-2: where the spec's root-named registry files physically live — **CLOSED**, recorded as `REG-008`
>
> **Why it had to be decided:** the spec writes `people.yaml`, `roles.yaml`, `platform.yaml`,
> `topology.yaml`, `exceptions.yaml`, `policies.yaml`, `tools.yaml` and `economics.yaml` as
> repository-root files (Sections 7, 8, 54, 55, 60, 62, 66, 68). PARTITION gives **root files to
> L0** and **`registries/**` to L1**. Taken literally, L1 — the Registries & Contracts lane — owns
> no registry file at all, and every registry change becomes an L0 CCR. The ownership map cannot
> be written until this is settled, because the guard resolves paths, not intentions.
>
> **Decided: Option A, with a split** (`lanes/L0-04-decisions-register.md` `REG-008`, closed).
> `platform.yaml`, `people.yaml`, `roles.yaml` and `topology.yaml` are the generated build outputs
> of Section 2.5 (`.github/lane-generated.map`), assembled from `registries/**` and never
> committed. The remainder — `exceptions.yaml`, `policies.yaml`, `tools.yaml`, `economics.yaml` —
> are committed directly under `registries/<name>.yaml` (L1-owned; see Section 4.6's
> `registries/exceptions.yaml` citation). The options below are kept for the record.
> - **A (assumed throughout this document):** registries live under `registries/` as
>   directory-per-item trees (`registries/people/<login>.yaml`,
>   `registries/platform/event-types/<id>.yaml`, ...). The root-named files are **build outputs**,
>   assembled by `make` and never committed (Section 2.5, `.github/lane-generated.map`). L1 owns
>   the source; L0 owns the assembler in the root `Makefile`. Consistent with invariant 46
>   ("derived data is computed, never hand-maintained") and with Section 97.3's one-file-per-item
>   rule. Consumers read the published artifact, per PARTITION rule 4.
> - **B:** the root-named files are hand-maintained at the root and owned by L0. Every registry
>   entry — every new person, tool, policy, event type — becomes an L0 serialisation point, and
>   L1's lane has almost no content. Also reintroduces exactly the shared-mutable-file conflict
>   class this document exists to remove.
> - **C:** root-named files exist at the root but the ownership map assigns each one individually
>   to L1 (`L1 people.yaml`, `L1 platform.yaml`, ...), overriding `:root:` by the exact-file rule.
>   Preserves the spec's literal layout and keeps L1 productive, but keeps the shared-list conflict
>   class alive inside L1 and forces every lane task in L1 to serialise.
>
> **Recommendation:** A. If L0 chooses B or C, the only edits required are to
> `lane-paths.tsv` and `.github/lane-generated.map`; nothing else in this document
> changes, and Section 6's demonstration still holds for whatever remains directory-per-item.
>
> **Unblocks:** the `L1 registries/` line, the whole of Section 2.5, and L1's first task.

---

> ### D-REQ-3: who may edit `.github/workflows/lane-guard.yml` — **CLOSED**, recorded as `REG-002`
>
> **Why it had to be decided:** PARTITION gives `.github/workflows/**` to L2 without carve-out. The
> lane-guard workflow lives there. Enforcement is already safe — `pull_request_target` runs the
> base branch's copy, so an L2 edit cannot take effect on L2's own PR — but the *authoring*
> question is open, and the ownership map needs an answer either way.
>
> **Decided: Option A** (named-file carve-out), plus cycle-1 Option E (retroactive replay)
> (`lanes/L0-04-decisions-register.md` `REG-002`, closed by `FD-003`, 2026-09-02).
> `.github/workflows/lane-guard.yml` is exclusively L0-owned; the exact-file rule is already in
> Section 1.2's `lane-paths.tsv`, and Section 9 criterion 1's expected count already includes it.
> The options below are kept for the record.
> - **A:** add one exact-file rule `L0 .github/workflows/lane-guard.yml` (exact rules beat prefix
>   rules, so it overrides `L2 .github/workflows/`). L2 keeps every other workflow. Narrows L2's
>   stated ownership by exactly one file.
> - **B:** leave the map as PARTITION states it. L2 may edit the file; the edit takes effect only
>   after L0 merges it to `integration`, and CODEOWNERS routes the review to L0 anyway. No change
>   to the partition; relies wholly on `pull_request_target` semantics and on L0 review.
> - **C:** move the guard to the records repository or a separate `control-plane-ci` repository and
>   invoke it as a required check via a reusable workflow. Strongest isolation; adds a repository
>   PARTITION does not list.
>
> **Recommendation:** A, and keep `pull_request_target` regardless — belt and braces, since B's
> safety rests entirely on one GitHub semantic and A's rests on a rule the guard itself enforces.
>
> **Unblocks:** the final line of the L0 block in `lane-paths.tsv`.

---

> ### L0 DECISION REQUIRED — D-REQ-4: ownership of the unassigned subsystems G, H, J, O, P
>
> **Why it must be decided:** the guard is fail-closed. Section 99.2 defines subsystems G
> (plan-checker and Gate 1 tooling), H (dashboards and views), J (background machine layer), O
> (governance registries and jobs) and P (people intelligence engine). The PARTITION lane table
> assigns none of them, so any path they need resolves to `UNOWNED` and the first PR touching one
> fails R1. This is correct behaviour, and it stalls that work until L0 acts.
>
> **Options**
> - **A:** L0 declares each unassigned subsystem out of scope for the five-lane build and holds
>   its paths itself (`L0 dashboards/`, `L0 plan-checker/`, ...). Matches Section 99.4's minimal
>   honest V1, which defers most of these; H is partly covered by "Founder view v0" and O by "the
>   exception registry with mandatory expiry".
> - **B:** L0 adds each subsystem's paths to the nearest existing lane by dependency — H to L4
>   (which already owns `metrics/**` and is H's declared dependency), O to L3 (which owns the
>   reconciler that expires exceptions), G/J/P to L0. Extends the frozen table by ownership map
>   only, without altering any line PARTITION already states.
> - **C:** leave them `UNOWNED` deliberately, so that any attempt to build them fails loudly until
>   a decision is made. Zero work now; guarantees a mid-build stall at the first attempt.
>
> **Recommendation:** L0's call, and it is a scope decision rather than a mechanics one — this
> document takes no position beyond noting that C is the current state by default and that the
> failure it produces is a correct fail-closed stop, not a bug to be worked around by adding a map
> rule locally. **A lane agent that hits `R1 UNOWNED` files a blocker issue and stops; it never
> edits the ownership map.**
>
> **Unblocks:** any task touching subsystems G, H, J, O or P.

---

## 9. Acceptance criteria for this file's mechanisms

L0 runs these once, at the end of Phase 0, before any lane branch is created. Every command prints
one unambiguous line. All ten must pass.

| # | What is checked | Command | Pass output |
|---|---|---|---|
| 1 | Ownership map parses to the expected rule count | `awk 'BEGIN{FS="[ \t]+"} /^[ \t]*#/{next} NF>=2' lane-paths.tsv \| wc -l` | `25`, for the map exactly as printed in Section 1.2 (D-REQ-3's Option A exact-file rule is already in it) |
| 2 | No path is claimed by two lanes | `awk 'BEGIN{FS="[ \t]+"} /^[ \t]*#/{next} NF>=2{print $2}' lane-paths.tsv \| sort \| uniq -d \| wc -l` | `0` |
| 3 | Guard workflow is valid YAML and uses no third-party action | `grep -c 'uses:' .github/workflows/lane-guard.yml \|\| echo 0` | `0` |
| 4 | Guard is a required status check on `integration` | `RS_ID=$(gh api repos/$ORG/control-plane/rulesets --jq '.[]|select(.name=="control-plane-integration")|.id'); gh api repos/$ORG/control-plane/rulesets/$RS_ID --jq '[.rules[]|select(.type=="required_status_checks")|.parameters.required_status_checks[].context]'` | `["lane-guard"]` |
| 5 | Branches must be up to date before merge | `gh api repos/$ORG/control-plane/rulesets/$RS_ID --jq '.rules[]|select(.type=="required_status_checks")|.parameters.strict_required_status_checks_policy'` | `true` |
| 6 | Contracts are frozen and intact | `sha256sum -c contracts/CONTRACTS.lock --quiet && echo FROZEN` | `FROZEN` |
| 7 | No union merge driver anywhere | `git config --get-regexp 'merge\..*\.driver' \|\| echo NONE` | `NONE` |
| 8 | No generated artifact is committed | `git ls-files \| grep -E '^(build/|dist/|platform\.yaml$|people\.yaml$|roles\.yaml$|topology\.yaml$|docs/metrics\.md$)' \| wc -l` | `0` |
| 9 | The canary PR is open and failing | `gh pr checks $CANARY --repo $ORG/control-plane --json name,state --jq '[.[]\|select(.name=="lane-guard")\|.state]\|first'` | `FAILURE` |
| 10 | The worked example reproduces | run the Section 6.4 script | `NAIVE RESULT: CONFLICT ...` then `PARTITIONED RESULT: CLEAN ...` |

Criterion 1's expected count changes if L0 answers D-REQ-2 or D-REQ-3 differently; recompute it
from the map L0 actually ships and record the number here. Criteria 2 through 10 are invariant to
those decisions.

**Phase 0 is not complete, and no lane branch may be created, until all ten pass.**
