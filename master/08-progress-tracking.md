# 08 — Progress Tracking and Control

**Owner: L0 (human/lead integrator). Audience: L0 first, the five lane developers second.**
Conforms to `implementation/PARTITION.md` (FROZEN). Nothing here redesigns the lane partition.

---

## 0. The one rule this document exists to enforce

> **A lane never reports its status. Status is derived from git.**

The five lane developers are Sonnet-4.6-class, hold no repo context and no judgment authority
(PARTITION §"AI developer profile"). Asking such a reader "how far along are you?" produces a
number that is confident, cheap to produce, and unrelated to reality. So nobody is asked.

A lane's total observable output is exactly three things:

| Artifact | Surface | Who writes it |
|---|---|---|
| Commits on `lane/<N>/<phase>-<nnn>-<slug>` | git | the lane |
| One pull request from that branch into `integration` | GitHub | the lane |
| One blocker issue, **only when the task's STOP rule fires** | GitHub Issues | the lane |

There is no percentage, no standup, no "80% done", no status field a lane can set, and no
progress file a lane can edit. Every status value in §3 is computed from the three artifacts
above plus the L0-written task ledger. This mirrors the specification's own discipline:
*"Humans write decisions and meaning; machines write measurable state"* (Section 101.7,
invariant 40; Section 94.9), and *"Derived data is computed, never hand-maintained"*
(invariant 46).

The single self-reported artifact — the blocker issue — is treated as an *event*, not as a
status: it is counted, aged, classified by L0, and audited at closure (§6, §9). It is never
trusted as a description of progress.

---

## 1. Environment — every command in this file assumes exactly these variables

Set these once per shell. Nothing else in this document contains a literal organisation name,
path, or host. Every command below is copy-pasteable after this block runs.

```bash
set -euo pipefail
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org
export CP="$HOME/build/control-plane"                       # control-plane working copy
export CPR="$HOME/build/control-plane-records"              # control-plane-records working copy
export SPEC="$HOME/build/spec/MultiProduct_MasterSpec_v4.0.md"
export TZ=UTC                                               # Section 97.1: time is written one way
```

Required tooling on L0's machine. Nothing in §1–§9 runs on a lane developer's machine.

```bash
set -euo pipefail
git --version          # >= 2.40
gh --version           # >= 2.40, authenticated: gh auth status
jq --version           # >= 1.6
yq --version           # mikefarah yq v4.x  (NOT the python wrapper)
```

Verify in one line — output must be exactly `TOOLING OK`:

```bash
for t in git gh jq yq; do command -v "$t" >/dev/null || { echo "MISSING $t"; exit 1; }; done; echo "TOOLING OK"
```

### 1.1 One-time label bootstrap

Run once per repository, **after `L0-00-T01` has created the base labels** (`blocker`, `lane-0`–`lane-5`). The triage labels (`class-*`) and disposition labels (`disp-*`) used in §6 and §8 are L0-only labels that lanes may not create (`L0D-04`). They are not included in `L0-00-T01` because they are consumed only by L0 procedures, never by lane issue templates.

```bash
set -euo pipefail
gh label create class-amber          --color "#FFA500" --description "Non-urgent; lane has other issued tasks" --repo "$ORG/control-plane" --force
gh label create class-red            --color "#D93F0B" --description "Material risk to partition or contract; 2-bd deadline" --repo "$ORG/control-plane" --force
gh label create class-blocking       --color "#B60205" --description "Unsafe to proceed; hold merge-train slot immediately" --repo "$ORG/control-plane" --force
gh label create disp-unblock         --color "#0E8A16" --description "Answered; task resumes" --repo "$ORG/control-plane" --force
gh label create disp-respec          --color "#0E8A16" --description "Packet rewritten; task re-issued under same id" --repo "$ORG/control-plane" --force
gh label create disp-contract-change --color "#0E8A16" --description "L0 edited contracts/**; all lanes notified" --repo "$ORG/control-plane" --force
gh label create disp-reassign        --color "#0E8A16" --description "Work moved to owning lane; new task issued" --repo "$ORG/control-plane" --force
gh label create disp-withdraw        --color "#0E8A16" --description "Task cancelled; withdrawn: true written to ledger" --repo "$ORG/control-plane" --force
echo "LABELS OK"
```

---

## 2. The task ledger

### 2.1 Where it lives and who writes it

```
control-plane/
  docs/
    plan/
      tasks/
        lane-0/          # L0's own tasks and the seeded canary
        lane-1/          # one file per L1 task
        lane-2/
        lane-3/
        lane-4/
        lane-5/
      reports/           # one file per day, generated (§4)
      decisions/         # one file per L0 decision, until records/decisions/ exists (§8.3)
      bootstrap-log/     # one file per week, until records/bootstrap-log/ exists (§7.4)
      bin/               # the generators in this document
```

`docs/**` is owned **exclusively by L0** (PARTITION §"The five build lanes", L0 row). That is
the whole reason the ledger lives there: **no lane can write a ledger file, so no lane can
report its own status, and no two writers ever touch one file.** Directory-per-item is
preserved (PARTITION anti-conflict rule 3): one file per task, one file per day, one file per
decision. There is no index, no `tasks.yaml`, no roll-up file — every roll-up in this document
is regenerated from the directory on demand.

A lane that discovers it needs a ledger file changed has hit its STOP rule and opens a blocker
issue (§6). It never edits `docs/**`. A PR from `lane/<N>/*` touching `docs/**` fails the
lane-guard check (§4.5) and is closed unmerged.

> **L0 DECISION REQUIRED — D-08-1: home for the programme's ledger and generators**
>
> `docs/plan/bin/*.sh` puts executable programme tooling inside a documentation path. It is
> the only path L0 owns exclusively in `control-plane` that can hold it without colliding with
> a lane (`tools/evidence/**` is L2, `tools/provision/**` is L3, `tools/records/**` is L4, and
> `tools/ledger/**` is unclaimed by the frozen partition — claiming it would be a partition
> edit, which this document may not make).
>
> - **Option A (assumed by this document):** keep the ledger and generators under
>   `docs/plan/**` in `control-plane`. Zero new repositories, zero partition change, and the
>   programme's own state is version-controlled beside the thing it tracks. Cost: scripts in a
>   docs tree.
> - **Option B:** a sixth repository, `build-ops`, owned by L0, holding `tasks/`, `reports/`,
>   `bin/`. Cleaner separation; costs one repository, one more clone for L0, and a decision
>   that the frozen repository table in PARTITION is a build-lane contract rather than an
>   exhaustive list of repositories.
> - **Option C:** claim `tools/ledger/**` for L0 in the partition. **Rejected here** — this
>   document may not amend the frozen partition.
>
> Decide before the first task packet is issued. Every path in §2–§9 changes root if B is
> chosen; nothing else changes.

### 2.2 Task identity and branch naming — one derivation, both directions

| Thing | Form | Example |
|---|---|---|
| Task id | `L<lane>-<phase>-<nnn>` | `L1-p0-003` |
| Ledger file | `docs/plan/tasks/lane-<lane>/<task-id>.yaml` | `docs/plan/tasks/lane-1/L1-p0-003.yaml` |
| Branch | `lane/<lane>/<phase>-<nnn>-<slug>` | `lane/1/p0-003-people-schema` |

The branch form is exactly PARTITION's `lane/N/<phase>-<task>`. The derivation is mechanical
in both directions, which is what lets §3 join a branch to a ledger file with no lookup table:

```bash
# task id -> branch prefix
task="L1-p0-003"; lane="${task:1:1}"; key="${task#L${lane}-}"; echo "lane/${lane}/${key}-"
# expected output: lane/1/p0-003-
```

A branch that does not match `lane/[1-5]/*` is an unattributable branch and is reported as a
lane-guard violation (§4.5), not as progress.

### 2.3 Ledger schema

One file per task. Written by L0 at issuance; **never edited after issuance except by L0, and
every post-issuance edit is itself a decision record (§8.3).** There is deliberately no
`status:` field, no `percent:` field and no `updated_by:` field — those are the fields a
status-reporting culture grows around.

```yaml
ledger_schema_version: 1

task_id: L1-p0-003
lane: 1
phase: p0                      # the phase label this task belongs to (§5.1)
subsystem: A                   # Section 99.2 subsystem letter, A..R — exactly one
branch: lane/1/p0-003-people-schema
issued: 2026-08-27T09:00:00Z
issued_by: L0
estimate_band: M               # Section 29.3 vocabulary: XS S M L XL — see §5.4
priority: P0                   # P0 | P1 | P2 | P3 — Section 98.1 P0-before-P2 rule is checked on this

owns_paths:                    # every path this task may create or edit. Subset of the lane's
  - schemas/registry/people.schema.json   # owned paths in PARTITION. Checked by §4.5.

reads_paths:                   # read-only inputs; contracts/** and generated fixtures only
  - contracts/registry/people.contract.md
  - contracts/fixtures/people.valid.json
  - contracts/fixtures/people.invalid-no-end-date.json

spec_refs:                     # real section numbers only; each is grep-checkable in $SPEC
  - "Section 7"                # People Registry
  - "Section 99.2 A"           # Control-plane repository subsystem
at_ids: [AT-002]               # acceptance tests this task advances — real AT ids only
invariants: [50, 51, 54]       # Section 101 invariant numbers this task makes enforceable
v1_item: 1                     # Section 99.4 minimal-honest-V1 item number, or null

toolchain:                     # the exact binaries the acceptance commands call
  # JSON Schema validation uses Python check-jsonschema (REG-005), not ajv-cli.
  # npx --yes ajv-cli@5.0.0 removed — FD-005 fixes minimal toolchain to Python only (no Node).

acceptance:                    # every criterion is a command with an exact expected stdout
  - id: AC-1
    command: "cd \"$CP\" && python -m json.tool schemas/registry/people.schema.json >/dev/null && echo OK"
    expect: "OK"
  - id: AC-2
    command: "cd \"$CP\" && npx --yes ajv-cli@5.0.0 validate -s schemas/registry/people.schema.json -d contracts/fixtures/people.valid.json 2>&1 | tail -1"
    expect: "contracts/fixtures/people.valid.json valid"
  - id: AC-3                   # negative test — Section 95.4 discipline, applied to every schema task
    command: "cd \"$CP\" && npx --yes ajv-cli@5.0.0 validate -s schemas/registry/people.schema.json -d contracts/fixtures/people.invalid-no-end-date.json >/dev/null 2>&1 && echo UNEXPECTED-PASS || echo REJECTED"
    expect: "REJECTED"

self_verify: "bash docs/plan/bin/verify-task.sh L1-p0-003"

stop_rule: >
  If contracts/registry/people.contract.md does not exist, or names a field this schema cannot
  express, or if any acceptance command requires editing a path not in owns_paths — do not
  proceed, do not edit contracts/**, do not touch another lane's path. Open a blocker issue
  per docs/escalation/BLOCKER.md and stop this task.
```

> **Note:** JSON Schema validation uses Python `check-jsonschema` (REG-005), not ajv-cli. The `npx --yes ajv-cli@5.0.0` calls shown in AC-2 and AC-3 above are illustrative placeholders; any real task packet must use the Python equivalent — FD-005 fixes the minimal toolchain to Python only (no Node).

**The `toolchain:` field is the lane packet's choice, not this document's.** The example above
shows the *shape* of an acceptance block. Which validator binary L1 uses is decided in L1's own
task packet and recorded here so the daily report can prove which binary produced a pass.

### 2.4 Rules L0 enforces on every ledger file before issuance

Each rule below has a command; a task packet failing any of them is not issued.

| # | Rule | Why |
|---|---|---|
| 1 | Every `acceptance[].expect` is an **exact** stdout string, never a regex, substring or "contains" | PARTITION: "a self-verify command whose output is unambiguous" |
| 2 | At least one acceptance criterion is a **negative** test | Section 95.4: gates are verified negatively, or they read armed and are not |
| 3 | Every `owns_paths` entry starts with a prefix the lane owns | PARTITION anti-conflict rule 1 |
| 4 | `reads_paths` contains only `contracts/**` or paths the lane owns | PARTITION rules 2 and 4 |
| 5 | Every `spec_refs`, `at_ids`, `invariants` entry resolves in `$SPEC` | no invented identifiers |
| 6 | `stop_rule` is present and names the blocker path | PARTITION: every task has a STOP rule |
| 7 | No `status:`, `percent:`, `progress:` or `updated_by:` key exists | §0 |

```bash
set -euo pipefail
# docs/plan/bin/lint-ledger.sh — L0 runs this before issuing any task. Output: LEDGER OK, or lines naming defects.
cat > "$CP/docs/plan/bin/lint-ledger.sh" <<'EOF'
#!/usr/bin/env bash
set -uo pipefail
: "${CP:?set CP}"; : "${SPEC:?set SPEC}"
cd "$CP"; bad=0
own_prefixes() { case "$1" in
  0) echo "contracts/ docs/ CODEOWNERS Makefile" ;;
  1) echo "schemas/registry/ schemas/product/ registries/ validators/registry/" ;;
  2) echo ".github/workflows/ templates/workflows/ tools/evidence/" ;;
  3) echo "reconciler/ tools/provision/ validators/drift/" ;;
  4) echo "schemas/records/ metrics/ tools/records/" ;;
  5) echo "access/ infra/ ops-vm/ notify/ assets/" ;;
esac; }
for f in docs/plan/tasks/lane-*/*.yaml; do
  [ -e "$f" ] || continue
  t=$(yq -r '.task_id' "$f"); l=$(yq -r '.lane' "$f")
  grep -qE '^(status|percent|progress|updated_by):' "$f" && { echo "$t: forbidden self-report key"; bad=1; }
  [ "$(yq -r '.stop_rule // ""' "$f")" = "" ] && { echo "$t: no stop_rule"; bad=1; }
  n=$(yq -r '.acceptance | length' "$f")
  [ "$n" -ge 1 ] || { echo "$t: no acceptance criteria"; bad=1; }
  yq -r '.acceptance[].expect' "$f" | grep -qE '\*|\.\*|contains|~=' && { echo "$t: non-exact expect"; bad=1; }
  yq -r '.acceptance[].command' "$f" | grep -q 'UNEXPECTED-PASS\|REJECTED\||| echo' || { echo "$t: no negative test"; bad=1; }
  for p in $(yq -r '.owns_paths[]' "$f"); do
    ok=0; for pre in $(own_prefixes "$l"); do case "$p" in "$pre"*) ok=1;; esac; done
    [ "$ok" = 1 ] || { echo "$t: owns_paths '$p' not owned by lane $l"; bad=1; }
  done
  for p in $(yq -r '.reads_paths[]? // empty' "$f"); do
    case "$p" in contracts/*) ;; *) ok=0; for pre in $(own_prefixes "$l"); do case "$p" in "$pre"*) ok=1;; esac; done
      [ "$ok" = 1 ] || { echo "$t: reads_paths '$p' is neither contracts/** nor lane-owned"; bad=1; };; esac
  done
  for a in $(yq -r '.at_ids[]? // empty' "$f"); do
    grep -q "$a" "$SPEC" || { echo "$t: $a does not exist in the specification"; bad=1; }; done
  while IFS= read -r s; do
    [ -n "$s" ] || continue
    grep -qF "$s" "$SPEC" || { echo "$t: spec_ref '$s' not found"; bad=1; }
  done < <(yq -r '.spec_refs[]? // empty' "$f")
done
[ "$bad" = 0 ] && echo "LEDGER OK"
exit "$bad"
EOF
chmod +x "$CP/docs/plan/bin/lint-ledger.sh"; bash "$CP/docs/plan/bin/lint-ledger.sh"
```

---

## 3. Status vocabulary — derived, never declared

### 3.1 The closed enum

Exactly nine values. No lane can produce any of them directly.

| Status | Meaning | Derivation (all facts from git/GitHub) | Caused by |
|---|---|---|---|
| `issued` | ledger file exists; work has not started | ledger file present on `integration`; **no** remote ref matching the branch prefix | L0 |
| `in-progress` | branch exists, no PR | remote ref matches prefix; no PR with that `headRefName` | lane |
| `in-review` | PR open into `integration` | PR state `OPEN`, `baseRefName == integration` | lane |
| `blocked` | STOP rule fired | an **open** issue labelled `blocker` whose title starts `<task-id> ` | lane (overrides all below) |
| `rejected` | PR closed unmerged | PR state `CLOSED`, `mergedAt` null | L0 |
| `integrated` | merged into `integration`, acceptance not yet re-run | PR state `MERGED`, merge commit not an ancestor of `origin/main` | merge train |
| `accepted` | merged **and** `verify-task.sh` exits 0 against `integration` head | `integrated` + acceptance re-run passes | derived |
| `released` | merge commit is an ancestor of `origin/main` | `git merge-base --is-ancestor <mergeCommit> origin/main` | L0 |
| `withdrawn` | L0 cancelled the task | `withdrawn: true` present in the ledger file | L0 |

**Precedence, binding:** `withdrawn` > `blocked` > `released` > `accepted` > `integrated` >
`rejected` > `in-review` > `in-progress` > `issued`. A blocked task is blocked even if its
branch has commits and its PR is open — that is the whole point of the flag. This mirrors
Section 29.1: **Blocked is a flag, not a column**; any in-flight state can carry it.

**`accepted` is the only status that means anything.** `integrated` means a merge happened.
`accepted` means the task's own acceptance commands, re-run on `integration` head after the
merge, produced their exact expected output. Section 53.6's closure-quality rule applied to the
build: a finding closed without evidence of remediation is reopened, not counted.

### 3.2 The derivation script

```bash
set -euo pipefail
cat > "$CP/docs/plan/bin/ledger-status.sh" <<'EOF'
#!/usr/bin/env bash
# Derives the status of every issued task. WRITES NOTHING. Output: TSV, one row per task.
set -uo pipefail
: "${CP:?set CP}"; : "${ORG:?set ORG}"
cd "$CP"
git fetch --prune --quiet origin '+refs/heads/*:refs/remotes/origin/*'

PRS=$(gh pr list --repo "$ORG/control-plane" --state all --limit 1000 \
      --json number,headRefName,baseRefName,state,mergedAt,mergeCommit)
BLK=$(gh issue list --repo "$ORG/control-plane" --state open --label blocker --limit 1000 \
      --json number,title)

printf 'task\tlane\tstatus\tevidence\n'
for f in docs/plan/tasks/lane-*/*.yaml; do
  [ -e "$f" ] || continue
  task=$(basename "$f" .yaml)
  lane=$(basename "$(dirname "$f")"); lane=${lane#lane-}
  key=${task#L${lane}-}
  branch=$(git for-each-ref --format='%(refname:short)' "refs/remotes/origin/lane/${lane}/${key}-*" | head -n1)
  branch=${branch#origin/}

  if grep -qE '^withdrawn:[[:space:]]*true' "$f"; then
    printf '%s\t%s\twithdrawn\tledger\n' "$task" "$lane"; continue; fi

  bnum=$(printf '%s' "$BLK" | jq -r --arg t "$task" \
        '[.[] | select(.title | startswith($t + " "))] | .[0].number // empty')
  if [ -n "$bnum" ]; then
    printf '%s\t%s\tblocked\tissue#%s\n' "$task" "$lane" "$bnum"; continue; fi

  if [ -z "$branch" ]; then printf '%s\t%s\tissued\tno-branch\n' "$task" "$lane"; continue; fi

  pr=$(printf '%s' "$PRS" | jq -c --arg b "$branch" '[.[] | select(.headRefName==$b)] | .[0] // empty')
  if [ -z "$pr" ]; then printf '%s\t%s\tin-progress\t%s\n' "$task" "$lane" "$branch"; continue; fi

  state=$(printf '%s' "$pr" | jq -r '.state')
  num=$(printf   '%s' "$pr" | jq -r '.number')
  sha=$(printf   '%s' "$pr" | jq -r '.mergeCommit.oid // empty')

  case "$state" in
    OPEN)   printf '%s\t%s\tin-review\tPR#%s\n' "$task" "$lane" "$num" ;;
    CLOSED) printf '%s\t%s\trejected\tPR#%s\n'  "$task" "$lane" "$num" ;;
    MERGED)
      if [ -n "$sha" ] && git merge-base --is-ancestor "$sha" origin/main 2>/dev/null; then
        printf '%s\t%s\treleased\tPR#%s\n' "$task" "$lane" "$num"
      elif bash docs/plan/bin/verify-task.sh "$task" >/dev/null 2>&1; then
        printf '%s\t%s\taccepted\tPR#%s\n' "$task" "$lane" "$num"
      else
        printf '%s\t%s\tintegrated\tPR#%s\n' "$task" "$lane" "$num"
      fi ;;
  esac
done
EOF
chmod +x "$CP/docs/plan/bin/ledger-status.sh"
```

Run it. It writes nothing and can be run as often as L0 likes:

```bash
bash "$CP/docs/plan/bin/ledger-status.sh" | column -t -s $'\t'
```

### 3.3 The acceptance re-runner

```bash
set -euo pipefail
cat > "$CP/docs/plan/bin/verify-task.sh" <<'EOF'
#!/usr/bin/env bash
# Re-runs one task's acceptance criteria against the CURRENT working tree.
# Exit 0 = every criterion produced its exact expected stdout.
set -uo pipefail
: "${CP:?set CP}"
task="${1:?usage: verify-task.sh <task-id>}"
f=$(ls "$CP"/docs/plan/tasks/lane-*/"$task".yaml 2>/dev/null | head -n1)
[ -n "$f" ] || { echo "NO-SUCH-TASK $task"; exit 2; }
n=$(yq -r '.acceptance | length' "$f"); fail=0
for i in $(seq 0 $((n-1))); do
  id=$(yq  -r ".acceptance[$i].id"      "$f")
  cmd=$(yq -r ".acceptance[$i].command" "$f")
  exp=$(yq -r ".acceptance[$i].expect"  "$f")
  out=$(bash -c "$cmd" 2>&1 | tail -n1)
  if [ "$out" = "$exp" ]; then echo "PASS $task $id"
  else echo "FAIL $task $id"; echo "  expected: [$exp]"; echo "  actual:   [$out]"; fail=1; fi
done
exit "$fail"
EOF
chmod +x "$CP/docs/plan/bin/verify-task.sh"
```

Sweep every merged task against `integration` head:

```bash
set -euo pipefail
git -C "$CP" checkout --quiet integration && git -C "$CP" pull --quiet --ff-only
bash "$CP/docs/plan/bin/ledger-status.sh" | awk -F'\t' '$3=="integrated"||$3=="accepted"{print $1}' \
  | while read -r t; do bash "$CP/docs/plan/bin/verify-task.sh" "$t"; done
```

---

## 4. The daily integration report

Generated by L0 once per working day, before the merge train runs. Every number in it comes
from `git`, `gh` or a re-run acceptance command. **No section of this report has a human input
field.** One file per day under `docs/plan/reports/<YYYY-MM-DD>.md` — directory-per-item, so
regenerating a day never rewrites another day and no two writers ever meet in one file.

### 4.0 The header — the five numbers that answer "where is the programme?"

```
PROGRAMME STATE: Healthy | Degrading | Impaired
  accepted / issued        : <n>/<N>
  AT ids covered           : <n>/110
  invariants enforceable   : <n>/111
  open blockers  A/R/B     : <a>/<r>/<b>
  merge train              : OK | OUT-OF-ORDER | HALTED
```

**The headline is computed from budget consumption, not from the presence of a class**, exactly
as Section 52.1 computes operating-system health, and using the same three words so that no
second vocabulary exists (Section 53.4 retires all other severity vocabularies; D43):

- **Impaired** — any `class-blocking` blocker is open, **or** the flat programme-wide Red
  tolerance is exceeded.
- **Degrading** — any `class-red` blocker is open, **or** the per-lane Amber tolerance is exceeded.
- **Healthy** — otherwise.

Tolerances, mirroring the two-basis rule of Section 53.4 and D84 rather than inventing a third:

| Class | Tolerance | Basis |
|---|---|---|
| Amber | **2 open per lane** (10 at five lanes) | scales with the work surface; routine remediation debt |
| Red | **3 open programme-wide, flat** | the volume of material unremediated risk L0 can hold in attention at once — a property of the integrator, not of the lane count |
| Blocking | **no budget** | unsafe to proceed |

### 4.1 R1 — merge-train order compliance

The train order is frozen: **L1 → L4 → L2 → L3 → L5** (PARTITION §"Branch & merge model").
A cycle that merged out of order merged a consumer before its producer.

```bash
set -euo pipefail
cat > "$CP/docs/plan/bin/r1-merge-train.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
: "${CP:?set CP}"
git -C "$CP" log --first-parent --merges --reverse --since="24 hours ago" \
    --format='%s' origin/integration \
  | sed -nE 's#.*lane ([1-5])[^0-9].*#\1#p; s#.*lane ([1-5])$#\1#p; s#.*\[L([1-5])-[A-Z][0-9]-[0-9][0-9]\].*#\1#p' \
  | awk 'BEGIN{o["1"]=1;o["4"]=2;o["2"]=3;o["3"]=4;o["5"]=5;p=0;bad=0}
         {if(o[$1]<p){bad=1;print "OUT-OF-ORDER lane " $1}; p=o[$1]}
         END{if(bad==0) print "MERGE-TRAIN OK"}'
EOF
chmod +x "$CP/docs/plan/bin/r1-merge-train.sh"; bash "$CP/docs/plan/bin/r1-merge-train.sh"
```

> **DF-0224 fix note:** The subject format from `L0-03:831` is `merge-train cycle 7: lane 5 (#120)` —
> `lane N` with a space, no slashes. The previous regex `lane/([1-5])/` never matched it, so the
> extractor produced no lane numbers and the awk `END` block always printed `MERGE-TRAIN OK`.
> The three patterns above now cover: (1) `lane N` followed by a non-digit, (2) `lane N` at end-of-line,
> and (3) the `[LN-…]` bracket form kept as fallback.

**Paired negative — assert the check does go red on out-of-order input:**

```bash
set -euo pipefail
# DF-0224 regression test: feed a reversed-order history (lane 5 before lane 1) and assert
# the extractor fires. Run this whenever R1 is modified.
printf '%s\n' \
  'merge-train cycle 1: lane 5 (#100)' \
  'merge-train cycle 1: lane 1 (#101)' \
| sed -nE 's#.*lane ([1-5])[^0-9].*#\1#p; s#.*lane ([1-5])$#\1#p' \
| awk 'BEGIN{o["1"]=1;o["4"]=2;o["2"]=3;o["3"]=4;o["5"]=5;p=0;bad=0}
       {if(o[$1]<p){bad=1;print "OUT-OF-ORDER lane " $1}; p=o[$1]}
       END{if(bad==0) print "MERGE-TRAIN OK"}' \
| grep -q 'OUT-OF-ORDER lane 1' && echo "NEGATIVE-OK" || echo "NEGATIVE-FAIL: extractor did not fire on reversed order"
```

Expected output: `NEGATIVE-OK`. If `NEGATIVE-FAIL` appears, the sed patterns no longer extract
lane numbers from the actual commit-subject format — do not run the real R1 until fixed.

Output is either the single line `MERGE-TRAIN OK` or one `OUT-OF-ORDER lane <N>` line per
violation. No other output is possible.

### 4.2 R2 — branch age (PARTITION: lane branches are short-lived, < 1 day)

```bash
set -euo pipefail
cat > "$CP/docs/plan/bin/r2-branch-age.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
: "${CP:?set CP}"
now=$(date -u +%s)
git -C "$CP" for-each-ref --format='%(refname:short)' 'refs/remotes/origin/lane/*' \
| while read -r ref; do
    base=$(git -C "$CP" merge-base origin/integration "$ref" 2>/dev/null) || continue
    first=$(git -C "$CP" rev-list --reverse "$base..$ref" | head -n1)
    [ -n "$first" ] || { echo "EMPTY   ${ref#origin/}"; continue; }
    ts=$(git -C "$CP" log -1 --format=%ct "$first")
    age=$(( (now - ts) / 3600 ))
    if [ "$age" -gt 24 ]; then echo "STALE   ${age}h  ${ref#origin/}"
    else                        echo "FRESH   ${age}h  ${ref#origin/}"; fi
  done
EOF
chmod +x "$CP/docs/plan/bin/r2-branch-age.sh"; bash "$CP/docs/plan/bin/r2-branch-age.sh"
```

Any `STALE` line is a task that outgrew its packet. It is a §7 review item, and at two
consecutive reviews it is STOP signal **S6** (§8).

### 4.3 R3 — rebase staleness

PARTITION requires a lane branch to be rebased on `integration` before its PR. `behind` > 0 on
an open PR means the rebase did not happen.

```bash
set -euo pipefail
git -C "$CP" for-each-ref --format='%(refname:short)' 'refs/remotes/origin/lane/*' \
| while read -r ref; do
    printf '%s\tahead:%s\tbehind:%s\n' "${ref#origin/}" \
      "$(git -C "$CP" rev-list --count "origin/integration..$ref")" \
      "$(git -C "$CP" rev-list --count "$ref..origin/integration")"
  done | column -t
```

### 4.4 R4 — PR queue, age and CI

```bash
set -euo pipefail
gh pr list --repo "$ORG/control-plane" --base integration --state open --limit 200 \
  --json number,headRefName,createdAt,isDraft,mergeable,statusCheckRollup \
  --jq '.[] | [ .number, .headRefName, .createdAt, .isDraft, .mergeable,
                ([.statusCheckRollup[]? | select(.conclusion=="FAILURE") | .name] | join(",") // "-") ] | @tsv' \
| column -t -s $'\t'
```

### 4.5 R5 — the lane-guard check (the single most important section)

PARTITION anti-conflict rule 1: **one owner per path; a lane PR touching a foreign path FAILS.**
This is the check that proves the partition is holding. It runs against every open PR.

```bash
set -euo pipefail
cat > "$CP/docs/plan/bin/lane-guard.sh" <<'EOF'
#!/usr/bin/env bash
# Output: nothing at all when clean; one FOREIGN line per violation.
set -uo pipefail
: "${CP:?set CP}"; : "${ORG:?set ORG}"
own_prefixes() { case "$1" in
  1) echo "schemas/registry/ schemas/product/ registries/ validators/registry/" ;;
  2) echo ".github/workflows/ templates/workflows/ tools/evidence/" ;;
  3) echo "reconciler/ tools/provision/ validators/drift/" ;;
  4) echo "schemas/records/ metrics/ tools/records/" ;;
  5) echo "access/ infra/ ops-vm/ notify/ assets/" ;;
esac; }
gh pr list --repo "$ORG/control-plane" --base integration --state open --limit 200 \
   --json number,headRefName --jq '.[] | [.number,.headRefName] | @tsv' \
| while IFS=$'\t' read -r n head; do
    lane=$(printf '%s' "$head" | sed -nE 's#^lane/([1-5])/.*#\1#p')
    [ -n "$lane" ] || { echo "FOREIGN PR#$n unattributable-branch $head"; continue; }
    gh pr diff "$n" --repo "$ORG/control-plane" --name-only | while read -r p; do
      ok=0; for pre in $(own_prefixes "$lane"); do case "$p" in "$pre"*) ok=1;; esac; done
      [ "$ok" = 1 ] || echo "FOREIGN PR#$n lane$lane $p"
    done
  done
EOF
chmod +x "$CP/docs/plan/bin/lane-guard.sh"; bash "$CP/docs/plan/bin/lane-guard.sh"
```

And the historical version — the **collision detector**, which is STOP signal **S1**. It asks
one question: has any single path ever been touched by two different lanes on `integration`?

```bash
set -euo pipefail
cat > "$CP/docs/plan/bin/r5b-collisions.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
: "${CP:?set CP}"
git -C "$CP" log --first-parent --merges --since="30 days ago" --format='%H%x09%s' origin/integration \
| while IFS=$'\t' read -r sha subj; do
    lane=$(printf '%s' "$subj" | sed -nE 's#.*lane ([1-5])[^0-9].*#\1#p; s#.*lane ([1-5])$#\1#p; s#.*\[L([1-5])-[A-Z][0-9]-[0-9][0-9]\].*#\1#p'); [ -n "$lane" ] || continue
    git -C "$CP" diff-tree --no-commit-id --name-only -r "$sha^1" "$sha" | sed "s/^/${lane}\t/"
  done \
| sort -u \
| awk -F'\t' '{s[$2]=s[$2] $1} END{for(f in s) if(length(s[f])>1) print "COLLISION " f " lanes:" s[f]}'
EOF
chmod +x "$CP/docs/plan/bin/r5b-collisions.sh"; bash "$CP/docs/plan/bin/r5b-collisions.sh"
```

> **DF-0224 fix note (S1 collision detector):** Same regex fix as R1 above — the old
> `lane/([1-5])/` pattern never matched the actual subject format, so every merge commit was
> skipped (`[ -n "$lane" ] || continue` fired on every row), yielding structurally empty output
> and a permanently silent S1. The three-pattern sed now extracts the lane from all subject forms.

**Paired negative — assert the collision detector does fire on a two-lane path conflict:**

```bash
set -euo pipefail
# DF-0224 regression test: synthesise the sorted lane-path table that the collision
# detector's awk step consumes, and assert it prints COLLISION.
printf '%s\n' '1\tschemas/registry/foo.json' '2\tschemas/registry/foo.json' \
| awk -F'\t' '{s[$2]=s[$2] $1} END{for(f in s) if(length(s[f])>1) print "COLLISION " f " lanes:" s[f]}' \
| grep -q '^COLLISION' && echo "NEGATIVE-OK" || echo "NEGATIVE-FAIL: awk did not print COLLISION on a two-lane path"
```

Expected output: `NEGATIVE-OK`. `NEGATIVE-FAIL` means the awk logic is broken independently of
the sed fix — stop and investigate before running the real collision detector.

Clean output is **empty**. One `COLLISION` line means the frozen partition has a hole and the
programme stops (§8, S1).

### 4.6 R6 — blockers, aged and classed

```bash
set -euo pipefail
cat > "$CP/docs/plan/bin/r6-blockers.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
: "${ORG:?set ORG}"
gh issue list --repo "$ORG/control-plane" --state open --label blocker --limit 200 \
  --json number,title,createdAt,labels \
  --jq '.[] | [ .number, .createdAt, ([.labels[].name | select(startswith("class-"))] | join(",") // "UNTRIAGED"), .title ] | @tsv' \
| while IFS=$'\t' read -r n created class title; do
    age=$(( ( $(date -u +%s) - $(date -u -d "$created" +%s) ) / 3600 ))
    printf '#%s\t%sh\t%s\t%s\n' "$n" "$age" "$class" "$title"
  done | column -t -s $'\t'
EOF
chmod +x "$CP/docs/plan/bin/r6-blockers.sh"; bash "$CP/docs/plan/bin/r6-blockers.sh"
```

An `UNTRIAGED` line older than one working day is an L0 latency failure, measured the same way
the Founder's own decision latency is measured (Section 103.8) — a system property, never a
person's score.

### 4.7 R7 — the status roll-up

```bash
bash "$CP/docs/plan/bin/ledger-status.sh" | tail -n +2 | awk -F'\t' '{c[$3]++} END{for(s in c) printf "%-12s %s\n", s, c[s]}' | sort
```

### 4.8 R8 — branch health of `integration` itself

```bash
set -euo pipefail
git -C "$CP" rev-list --left-right --count origin/main...origin/integration   # <behind main>  <ahead of main>
gh run list --repo "$ORG/control-plane" --branch integration --limit 1 \
  --json workflowName,headSha,conclusion --jq '.[] | [.workflowName, .headSha[0:7], .conclusion] | @tsv'
```

`integration` red for more than one working day is STOP signal **S8**.

### 4.9 R9 — record-store write freshness (only once L4 has stood the records repo up)

Section 97.2 makes write freshness an instrument *because zero is the good value*: a workflow
whose record-write step fails silently renders every count-shaped metric as zero, which is
indistinguishable from health.

```bash
set -euo pipefail
for s in events records/deployments records/uat; do
  [ -d "$CPR/$s" ] || { echo "$s ABSENT"; continue; }
  last=$(git -C "$CPR" log -1 --format=%ct -- "$s" 2>/dev/null)
  [ -n "$last" ] && echo "$s $(( ( $(date -u +%s) - last ) / 3600 ))h" || echo "$s NO-WRITES"
done
```

### 4.10 The generator

```bash
cat > "$CP/docs/plan/bin/daily-report.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
: "${CP:?set CP}"; : "${ORG:?set ORG}"; : "${SPEC:?set SPEC}"
d=$(date -u +%F); out="$CP/docs/plan/reports/$d.md"; mkdir -p "$(dirname "$out")"
{
  echo "# Daily integration report — $d (UTC)"; echo
  echo '## Header';        echo '```'; bash "$CP/docs/plan/bin/burndown.sh"        ; echo '```'
  echo '## R1 merge train';echo '```'; bash "$CP/docs/plan/bin/r1-merge-train.sh"  ; echo '```'
  echo '## R2 branch age'; echo '```'; bash "$CP/docs/plan/bin/r2-branch-age.sh"   ; echo '```'
  echo '## R5 lane guard'; echo '```'; bash "$CP/docs/plan/bin/lane-guard.sh"      ; echo '```'
  echo '## R5b collisions';echo '```'; bash "$CP/docs/plan/bin/r5b-collisions.sh"  ; echo '```'
  echo '## R6 blockers';   echo '```'; bash "$CP/docs/plan/bin/r6-blockers.sh"     ; echo '```'
  echo '## R7 status';     echo '```'; bash "$CP/docs/plan/bin/ledger-status.sh" | tail -n +2 | awk -F'\t' '{c[$3]++} END{for(s in c) printf "%-12s %s\n", s, c[s]}' | sort; echo '```'
  echo '## S-signals';     echo '```'; bash "$CP/docs/plan/bin/stop-signals.sh"    ; echo '```'
} > "$out"
echo "WROTE $out"
EOF
chmod +x "$CP/docs/plan/bin/daily-report.sh"
```

Each `r*.sh` is the corresponding command block above, saved verbatim into its own file. They
are split into one file per section for the same reason the ledger is split into one file per
task: a section can be fixed without touching the others.

> **L0 DECISION REQUIRED — D-08-3: who runs the daily report**
>
> The natural home for a scheduled generator is `.github/workflows/`, but that path is owned
> **exclusively by L2** (PARTITION). L0 cannot add a workflow there without breaking the one
> rule the whole partition rests on.
>
> - **Option A (assumed by this document):** L0 runs `daily-report.sh` from a workstation each
>   morning and commits the day's file to `integration`. Zero partition pressure. Cost: it does
>   not run when L0 does not.
> - **Option B:** L0 issues an L2 task packet whose deliverable is
>   `.github/workflows/plan-daily-report.yml`, calling the same scripts. The generator becomes a
>   scheduled job; L2 owns the workflow file and never touches `docs/**`, so the partition holds.
>   Cost: the programme's own instrument becomes a lane deliverable with a lane's lead time.
> - **Option C:** the report runs on the operations VM once L5 has stood it up. Cost: the
>   instrument depends on the thing being built — the same trap D94 names for detection.
>
> Recommendation to L0: **A now, B once L2 has merged its first workflow task.** Decide at the
> first weekly review.

---

## 5. The burn-downs that matter

### 5.1 What is not a burn-down

Counting merged PRs, commits, lines, files, or "tasks closed" measures motion. The five lanes
can produce all five of those without the programme advancing one step. So none of them appears
in the header. The header carries only quantities that are **hard to move without building
something**, and every one of them has a fixed, spec-derived denominator.

### 5.2 The five denominators — all extracted from the specification, none invented

```bash
set -euo pipefail
grep -oE 'AT-[0-9]{3}' "$SPEC" | sort -u | wc -l          # 110  acceptance tests (Section 100)
seq 1 111 | wc -l                                          # 111  invariants     (Section 101)
grep -oE '\| SIG-[0-9]{2} \|' "$SPEC" | sort -u | wc -l    #  47  health signals (Section 52.2)
printf 'A B C D E F G H I J K L M N O P Q R\n' | wc -w     #  18  subsystems     (Section 99.2)
seq 1 9 | wc -l                                            #   9  minimal-V1 items (Section 99.4)
```

| # | Burn-down | Numerator | Denominator | Why it is the honest one |
|---|---|---|---|---|
| B1 | **Acceptance-criteria burn-down** | acceptance criteria whose command passes on `integration` head | all criteria in all issued ledger files | The only quantity that cannot be moved by writing code that does not work |
| B2 | **AT coverage** | union of `at_ids` over `accepted` tasks | 110 (Section 100) programme-wide; per-phase denominator from `docs/plan/at-phase-map.yaml` (D-08-6) | Section 100: the OS is complete only if every test passes by configuration alone |
| B3 | **Invariant enforceability** | union of `invariants` over `accepted` tasks | 111 (Section 101) | Section 101 makes the invariants a compliance checklist; each is `mechanical`, `policy` or `review-held` |
| B4 | **Subsystem coverage** | subsystems (A–R) with ≥1 `accepted` task, weighted by complexity band | 18 (Section 99.2) | The spec prices the build in subsystem complexity bands (S/M/L/XL), not in weeks |
| B5 | **Minimal-V1 items** | Section 99.4 items 1–9 with every mapped task `accepted` | 9 | Section 99.4 defines what "delivered" means before anything else |

```bash
cat > "$CP/docs/plan/bin/burndown.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
: "${CP:?set CP}"; : "${SPEC:?set SPEC}"
cd "$CP"
ST=$(bash docs/plan/bin/ledger-status.sh | tail -n +2)
ACC=$(printf '%s' "$ST" | awk -F'\t' '$3=="accepted"||$3=="released"{print $1}')
ISS=$(printf '%s' "$ST" | wc -l)
files_for() { for t in $1; do ls docs/plan/tasks/lane-*/"$t".yaml 2>/dev/null; done; }
AF=$(files_for "$ACC")

n_at=0;  [ -n "$AF" ] && n_at=$(yq -r '.at_ids[]? // empty'     $AF | sort -u | wc -l)
n_inv=0; [ -n "$AF" ] && n_inv=$(yq -r '.invariants[]? // empty' $AF | sort -u | wc -l)
n_sub=0; [ -n "$AF" ] && n_sub=$(yq -r '.subsystem // empty'     $AF | sort -u | wc -l)
n_v1=0;  [ -n "$AF" ] && n_v1=$(yq -r '.v1_item // empty'        $AF | grep -v '^null$' | sort -u | wc -l)

crit_tot=$(yq -r '.acceptance | length' docs/plan/tasks/lane-*/*.yaml 2>/dev/null | awk '{s+=$1} END{print s+0}')
crit_ok=0
for t in $ACC; do f=$(ls docs/plan/tasks/lane-*/"$t".yaml); crit_ok=$((crit_ok + $(yq -r '.acceptance|length' "$f"))); done

printf 'B1 acceptance criteria : %s/%s\n' "$crit_ok" "${crit_tot:-0}"
# B2 denominator 110 is programme-wide only; per-phase AT coverage must be driven by docs/plan/at-phase-map.yaml (D-08-6).
printf 'B2 AT ids covered      : %s/110\n' "$n_at"
printf 'B3 invariants enforced : %s/111\n' "$n_inv"
printf 'B4 subsystems touched  : %s/18\n'  "$n_sub"
printf 'B5 minimal-V1 items    : %s/9\n'   "$n_v1"
printf 'accepted / issued      : %s/%s\n'  "$(printf '%s' "$ACC" | grep -c . )" "$ISS"
EOF
chmod +x "$CP/docs/plan/bin/burndown.sh"; bash "$CP/docs/plan/bin/burndown.sh"
```

**Uncovered work is as important as covered work.** These two commands name what nothing is
building yet — the report shows them at every weekly review:

```bash
set -euo pipefail
# Acceptance tests with no task claiming them
yq -r '.at_ids[]? // empty' "$CP"/docs/plan/tasks/lane-*/*.yaml | sort -u > /tmp/at.claimed
grep -oE 'AT-[0-9]{3}' "$SPEC" | sort -u > /tmp/at.all
comm -13 /tmp/at.claimed /tmp/at.all | tr '\n' ' '; echo

# Invariants with no task claiming them
yq -r '.invariants[]? // empty' "$CP"/docs/plan/tasks/lane-*/*.yaml | sort -un > /tmp/inv.claimed
seq 1 111 > /tmp/inv.all
comm -13 /tmp/inv.claimed /tmp/inv.all | tr '\n' ' '; echo
```

### 5.3 The P0-before-P2 check (Section 98.1, binding)

> *"no P2 or P3 capability may be started while a P0 capability is unbuilt."*

```bash
set -euo pipefail
cat > "$CP/docs/plan/bin/p0-before-p2.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
: "${CP:?set CP}"
ST=$(bash "$CP/docs/plan/bin/ledger-status.sh" | tail -n +2)
p0_open=$(for f in "$CP"/docs/plan/tasks/lane-*/*.yaml; do
   [ "$(yq -r '.priority' "$f")" = "P0" ] || continue
   t=$(basename "$f" .yaml)
   s=$(printf '%s' "$ST" | awk -F'\t' -v t="$t" '$1==t{print $3}')
   case "$s" in accepted|released|withdrawn) ;; *) echo "$t";; esac
 done)
p2_started=$(for f in "$CP"/docs/plan/tasks/lane-*/*.yaml; do
   case "$(yq -r '.priority' "$f")" in P2|P3) ;; *) continue;; esac
   t=$(basename "$f" .yaml)
   s=$(printf '%s' "$ST" | awk -F'\t' -v t="$t" '$1==t{print $3}')
   case "$s" in issued|withdrawn) ;; *) echo "$t";; esac
 done)
if [ -n "$p0_open" ] && [ -n "$p2_started" ]; then
  echo "P0-BEFORE-P2 BREACH"; echo "  P0 not accepted: $p0_open"; echo "  P2/P3 started:   $p2_started"
else echo "P0-BEFORE-P2 OK"; fi
EOF
chmod +x "$CP/docs/plan/bin/p0-before-p2.sh"; bash "$CP/docs/plan/bin/p0-before-p2.sh"
```

A `declined` phase releases the lock; an `unbuilt` one holds it (Section 98.1). L0 records a
decline as a decision record (§8.3) and marks the P0 task `withdrawn: true` with a
`declined_decision:` pointer — that is why `withdrawn` is excluded from `p0_open` above.

### 5.4 Estimate calibration — the burn-down's own error bar

Ledger `estimate_band` uses the **Section 29.3 vocabulary and initial point values**, reused
rather than reinvented: `XS` half a day, `S` one day, `M` three days, `L` five days, `XL` ten
days and a prompt to split the item.

```bash
set -euo pipefail
bash "$CP/docs/plan/bin/ledger-status.sh" | tail -n +2 | awk -F'\t' '$3=="accepted"||$3=="released"{print $1}' \
| while read -r t; do
    f=$(ls "$CP"/docs/plan/tasks/lane-*/"$t".yaml)
    band=$(yq -r '.estimate_band' "$f"); iss=$(yq -r '.issued' "$f")
    key=${t#L*-}; lane=${t:1:1}
    sha=$(git -C "$CP" log -1 --format=%H --grep="lane/${lane}/${key}-" origin/integration)
    [ -n "$sha" ] || continue
    done_ts=$(git -C "$CP" log -1 --format=%ct "$sha")
    days=$(( (done_ts - $(date -u -d "$iss" +%s)) / 86400 ))
    case "$band" in XS) p=0.5;; S) p=1;; M) p=3;; L) p=5;; XL) p=10;; *) p=0;; esac
    printf '%s\tband:%s(%sd)\telapsed:%sd\n' "$t" "$band" "$p" "$days"
  done
```

A lane whose cumulative elapsed exceeds cumulative band point-value by more than 2× across two
consecutive review cycles is STOP signal **S9**: the plan's sizing, not the lane, is wrong.

> **D-08-6 — Decided: A — L0 to author `docs/plan/at-phase-map.yaml` before the first weekly review.**
>
> ~~L0 DECISION REQUIRED~~ — Section 100 states each test *"is verified at the implementation phase where the capability it
> exercises activates"* but publishes no AT→phase table. B2 therefore has a programme-wide
> denominator (110) and no per-phase denominator, so "are we done with Phase 1?" cannot be
> answered from AT coverage until the map exists.
>
> - **Option A (chosen):** L0 authors the map once, as `docs/plan/at-phase-map.yaml` (one row per AT id,
>   naming the Section 98 phase). ~110 rows, a few hours, and every phase gate becomes checkable.
> - **Option B:** carry only the programme-wide denominator; phase gates use the Section 98
>   completion checks verbatim instead, which are prose and are checked by hand.
> - **Option C:** derive the map mechanically from `at_ids` on issued task packets. **Rejected
>   here** — it makes the denominator a function of what has already been planned, so coverage
>   can never read below 100% of what was thought of.

> **L0 DECISION REQUIRED — D-08-5: what the phase burn-down is denominated in**
>
> Section 98.2 stamps absolute week labels on the Foundation phases ("Phase 1 — Foundation
> (Week 1)"). Decision **D99** in Appendix A states those phases were split into a Build track
> dated by subsystem with its complexity band and an Onboarding track relative to the subsystems
> it consumes, precisely because §99.2 prices those deliverables three to ten times higher. The
> body text and the register disagree.
>
> - **Option A (assumed by this document):** denominate in **subsystem complexity bands**
>   (Section 99.2: S under a week, M one to three weeks, L three to eight, XL multi-month), per
>   D99. Week labels are treated as configuration-elapsed ordering, never as build-elapsed dates.
> - **Option B:** denominate in Section 98.2's week labels. Simple, and known to be wrong by
>   D99's own reasoning.
>
> This decision sets what "behind schedule" means. Take it at the first weekly review, record it,
> and never revisit it mid-programme.

---

## 6. A blocked task

### 6.1 The lane's side — three steps, no judgment

The `stop_rule` in every ledger file ends with the same instruction. Written out once, in
`docs/escalation/BLOCKER.md`, so the task packet can point at it:

1. **Stop.** Commit whatever is on the branch, push it, and do not continue. Do not work around
   the blocker. Do not edit `contracts/**`. Do not touch any path outside `owns_paths`. Do not
   open a PR.
2. **Open one issue**, on the exact template below, in `$ORG/control-plane`.
3. **Move to your next `issued` task** if the ledger contains one. If it does not, stop and wait.

Never: propose a fix, choose between options, message another lane, or reopen a closed blocker.
Classification and disposition are judgment, and judgment belongs to L0 (PARTITION §"AI
developer profile").

```bash
set -euo pipefail
gh issue create --repo "$ORG/control-plane" \
  --label blocker --label "lane-1" \
  --title "L1-p0-003 BLOCKED: contracts/fixtures/people.invalid-no-end-date.json does not exist" \
  --body-file - <<'EOF'
task: L1-p0-003
branch: lane/1/p0-003-people-schema
stop_rule_triggered: |
  <paste the stop_rule field from the ledger file, verbatim, unedited>
last_command: |
  npx --yes ajv-cli@5.0.0 validate -s schemas/registry/people.schema.json -d contracts/fixtures/people.invalid-no-end-date.json
last_output: |
  error: cannot read contracts/fixtures/people.invalid-no-end-date.json: no such file
files_touched: |
  schemas/registry/people.schema.json
what_i_did_not_do: |
  I did not create the fixture. contracts/** is not in owns_paths.
EOF
```

The lane applies **exactly two labels**: `blocker` and `lane-<N>`. It never applies a `class-`
label. A blocker arriving with a class label is a packet defect, not a triage shortcut.

### 6.2 L0's side — triage within one working day

L0 applies one `class-` label, using the **one drift severity scale** of Section 53.4 (D43:
no other severity vocabulary exists anywhere in this system), with that section's response times:

| Label | Meaning for the build programme | Response time | Blocks work |
|---|---|---|---|
| `class-amber` | Real but non-urgent; the lane has other issued tasks | by the next weekly review (§7) | No |
| `class-red` | Material risk to the partition, a contract, or a dependency edge | within 2 business days | No, but appears in the daily header |
| `class-blocking` | Unsafe to proceed: the lane cannot advance, or the blocker implicates `contracts/**` or another lane's owned path | Immediate | **Yes** — that lane's position in the merge train is held until closed |

```bash
gh issue edit <N> --repo "$ORG/control-plane" --add-label "class-red"
```

L0's triage latency is itself measured (§4.6). An `UNTRIAGED` blocker older than one working day
means the integrator is the constraint — read exactly as Founder-decision latency is read
(Section 103.8): a system-constraint metric, never a performance one.

### 6.3 Disposition — a closed enum, applied at close

Every blocker closes with exactly one `disp-` label. A blocker closed without one fails the
weekly closure-quality audit (§9.3) and is reopened.

| Label | What L0 did | Side effects |
|---|---|---|
| `disp-unblock` | Answered the question; nothing changes | Comment carries the answer; task resumes |
| `disp-respec` | Rewrote the task packet | New `ledger_schema_version` bump on that file + a decision record; old branch abandoned; task re-issued under the **same** task id |
| `disp-contract-change` | L0 edited `contracts/**` and re-froze | A Contract Change Request is recorded; **every lane** is notified; counted for STOP signal **S2** |
| `disp-reassign` | The work belongs to a different lane | Task withdrawn; a new task issued in the owning lane; counted for STOP signal **S1** if a path was in two lanes' packets |
| `disp-withdraw` | The task should not exist | `withdrawn: true` written into the ledger file + a decision record |

```bash
gh issue close <N> --repo "$ORG/control-plane" --comment "disposition: respec — packet omitted the fixture dependency; re-issued." \
  && gh issue edit <N> --repo "$ORG/control-plane" --add-label "disp-respec"
```

### 6.4 Escalation ladder

```
t0        lane opens the blocker, stops the task
≤1 wd     L0 triages -> class-amber | class-red | class-blocking
          class-blocking: L0 holds that lane's merge-train slot immediately
≤2 bd     class-red must be dispositioned                (Section 53.4 response time)
≤1 week   class-amber must be dispositioned              (Section 53.4 "next planning cycle")
>1 wd     a class-blocking still open  -> STOP signal S5 (§8): halt issuance programme-wide
>3 open   class-red beyond the flat budget of 3          -> header reads Impaired
```

`wd` = working day, `bd` = business day, resolved against L0's declared working calendar —
never the runner's local time (Section 97.1).

---

## 7. The weekly L0 review

### 7.1 When

**Friday 16:00, sixty minutes, timeboxed.** Placed deliberately: after the Friday 15:00
deployment freeze and before the Friday 17:00 Ready-queue refill in the specification's own
cadence (Section 94.8), so the programme's review does not collide with the operating rhythm it
is building.

### 7.2 Inputs — all generated before the meeting, none written during it

```bash
set -euo pipefail
bash "$CP/docs/plan/bin/daily-report.sh"          # today's report
bash "$CP/docs/plan/bin/burndown.sh"              # B1..B5 with last week's file for the delta
diff <(git -C "$CP" show "HEAD@{7.days.ago}:docs/plan/reports/$(date -u -d '7 days ago' +%F).md" 2>/dev/null) \
     "$CP/docs/plan/reports/$(date -u +%F).md" | head -50
```

### 7.3 Agenda — fixed, in this order, with a decision at every item

| # | Box | Item | Input | Decision L0 must take |
|---|---|---|---|---|
| 1 | 5 min | Partition integrity | R5 + collision detector (§4.5) | Partition holds, or **STOP (S1)** |
| 2 | 10 min | Burn-down | B1–B5 with the week's delta, and the two "uncovered" lists (§5.2) | Which uncovered AT ids and invariants get task packets next cycle |
| 3 | 10 min | Blocker ageing | R6 (§4.6) | A disposition for every `class-red` past 2 business days and every `class-blocking` |
| 4 | 10 min | Contract Change Requests | count of `disp-contract-change` this week | Approve / reject / defer. `contracts/**` is frozen; two or more accepted in one week is **STOP (S2)** |
| 5 | 5 min | Packet quality | count of `disp-respec` per lane; STALE branches (§4.2) | Which packets are underspecified. Two respecs in one lane in one week is **STOP (S6)** |
| 6 | 10 min | Next cycle issuance | the uncovered lists from item 2 | Write the new ledger files; run `lint-ledger.sh`; commit to `integration` |
| 7 | 5 min | Instrument integrity | canary check + closure-quality sample (§9) | Reopen any task that no longer passes its own acceptance |
| 8 | 5 min | STOP roll-call | `stop-signals.sh` (§8.2) | Continue, or STOP AND REPLAN |

**A review that only adds is a failed review.** Section 98.5 applies this to the quarterly
operating-system review (exit: *"at least one policy retirement, one automation verdict and one
metric deletion"*) and AT-045 makes it a test. The same discipline applies here: item 6 may not
close until L0 has either withdrawn a task, narrowed a packet, or explicitly recorded that
nothing warranted withdrawal.

### 7.4 Output — one file, written by L0, in the specification's own three-field shape

Section 95.4 requires a **weekly bootstrap log entry** throughout bootstrap — which gates are
stubbed and which armed, which bootstrap exceptions opened or closed, which phase completion
checks ran and their results — with a detector: control-plane CI raises **Blocking** drift when
the newest entry is older than the calibrated staleness window, initial value 7 days. This
review produces that entry. Two of the three fields are pre-filled by the generator; L0 writes
only the judgment lines.

Until L4 has stood up `control-plane-records`, the entry is written to
`docs/plan/bootstrap-log/<YYYY-MM-DD>.md`. On cutover it moves to `records/bootstrap-log/` in
the records repository, where a human write travels as a direct push — that repository carries
no review protection, only the no-bypass ruleset blocking force-push and deletion (PARTITION
repository table; D107). L4 owns that repository, so L0's entry is a human record write on the
normal path of Section 97.1, not a lane deliverable.

---

## 8. STOP AND REPLAN

### 8.1 What STOP means, exactly

1. L0 **issues no new task packets.**
2. Lanes finish the task in hand or abandon the branch — L0 says which, per lane, in one comment.
3. L0 records a decision record (§8.3) naming the signal, the evidence command output, and the
   remedy.
4. The programme resumes only when the signal's detection command produces its clean output.

STOP is not a failure ritual. It is the alternative to five lanes producing merge conflicts,
foreign-path edits and unverifiable work for another week.

### 8.2 The signals

Each is detectable, has an unambiguous threshold, and has a command whose clean output is stated.

| Id | Signal | Detection | Threshold that means STOP | Why |
|---|---|---|---|---|
| **S1** | **Path collision on `integration`** | §4.5 collision detector | **any** `COLLISION` line | PARTITION rule 1 — one owner per path — has a hole. The partition is wrong, not the lane |
| **S2** | Contract churn | `gh issue list --repo "$ORG/control-plane" --state closed --label disp-contract-change --search "closed:>=$(date -u -d '7 days ago' +%F)" --json number --jq 'length'` | ≥ 3 open CCRs, or ≥ 2 accepted in one week | `contracts/**` was frozen too early or in the wrong shape (PARTITION rule 2) |
| **S3** | Repeated rebase conflict | count of lane branches with `behind > 0` at PR-open time (§4.3), plus any PR whose `mergeable` is `CONFLICTING` | the same lane twice in one cycle | PARTITION rule 3 — "no shared mutable file, ever" — is being violated somewhere |
| **S4** | Motion without progress | B1 and B2 (§5.2) versus merged-PR count | B1 **and** B2 flat across two consecutive weekly reviews while merged PRs rise | Code is landing that satisfies no acceptance criterion |
| **S5** | Blocking blocker unresolved | §4.6, `class-blocking` age | any `class-blocking` open > 1 working day | The integrator is the constraint and the lanes are idling |
| **S6** | Packets need judgment | `disp-respec` count per lane per week; STALE branches (§4.2) | 2 in one lane in one week, or a branch STALE at two consecutive reviews | PARTITION: "No task may require designing, choosing, or interpreting" — the packets are underspecified |
| **S7** | P0-before-P2 breach | §5.3 | any `P0-BEFORE-P2 BREACH` output | Section 98.1, binding: the primary defence against building the interesting parts first |
| **S8** | `integration` red | §4.8 | CI conclusion ≠ `success` on `integration` head for > 1 working day | The merge target is not releasable; every subsequent rebase inherits a broken base |
| **S9** | Sizing wrong | §5.4 | cumulative elapsed > 2× cumulative band point-value for a lane, two cycles running | The plan's estimates, not the lane's speed, are the defect |
| **S10** | Instrument stopped looking | §9.1 canary | the canary task reports anything other than `FAIL` | Section 53.1 seeded-canary rule (D63; AT-102): a run that finds nothing is assumed broken, never assumed clean |
| **S11** | Cross-lane traffic | `git -C "$CP" log --format='%s' --all --since='7 days ago' \| grep -cE 'Merge branch .lane/[1-5]' ` | any merge of one lane's branch into another lane's branch | PARTITION: "A lane NEVER merges another lane's branch" |
| **S12** | Auto-repair built too early | `git -C "$CP" log --since='7 days ago' --name-only --format= origin/integration \| grep -c '^reconciler/.*repair'` | any repair-class file merged before detect-only reconciliation has run clean for the declared period | Section 98.3 and Section 99.6 risk 6: auto-repair is the riskiest code in the system |

```bash
cat > "$CP/docs/plan/bin/stop-signals.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
: "${CP:?set CP}"; : "${ORG:?set ORG}"
raise=0
c=$(bash "$CP/docs/plan/bin/r5b-collisions.sh" | grep -c '^COLLISION' ); [ "$c" -gt 0 ] && { echo "S1 RAISED ($c collisions)"; raise=1; }
c=$(gh issue list --repo "$ORG/control-plane" --state open --label blocker --label class-blocking --json createdAt \
     --jq "[.[] | select((now - (.createdAt|fromdate)) > 86400)] | length"); [ "$c" -gt 0 ] && { echo "S5 RAISED ($c)"; raise=1; }
bash "$CP/docs/plan/bin/p0-before-p2.sh" | grep -q BREACH && { echo "S7 RAISED"; raise=1; }
bash "$CP/docs/plan/bin/verify-task.sh" L0-canary-000 >/dev/null 2>&1 && { echo "S10 RAISED (canary passed)"; raise=1; }
c=$(gh run list --repo "$ORG/control-plane" --branch integration --limit 1 --json conclusion --jq '.[0].conclusion')
[ "$c" = "success" ] || { echo "S8 CHECK integration=$c"; }
[ "$raise" = 0 ] && echo "NO STOP SIGNALS"
exit 0
EOF
chmod +x "$CP/docs/plan/bin/stop-signals.sh"
```

Clean output is the single line `NO STOP SIGNALS`.

### 8.3 Recording a STOP

```bash
set -euo pipefail
d=$(date -u +%F); f="$CP/docs/plan/decisions/${d}-stop-<slug>.md"
cat > "$f" <<EOF
# STOP — $d

signal: S1
evidence: |
$(bash "$CP/docs/plan/bin/r5b-collisions.sh" | sed 's/^/  /')
lanes_halted: [1,2,3,4,5]
remedy: |
  <what L0 changed>
resume_condition: |
  the collision detector produces empty output
EOF
git -C "$CP" add "$f" && git -C "$CP" commit -m "STOP: S1 path collision" && git -C "$CP" push origin integration
```

One file per decision, under L0's exclusively-owned `docs/**` — directory-per-item, so a STOP
recorded during a merge cycle never conflicts with anything. Once `control-plane-records` is
live these migrate into `records/decisions/`, the canonical store of Section 97.2, and are
written thereafter by the `record-decision` CLI (Section 99.2, named tools of the build surface).

---

## 9. Keeping the instrument honest

The tracking system is itself an instrument, and Section 52.5 is explicit: *instruments are
gamed unless they are calibrated by someone other than the party they measure.* Four guards,
each borrowed from a rule the specification already states rather than invented here.

### 9.1 The seeded canary — the tracking system's own AT-102

Section 53.1 requires a permanent, clearly labelled seeded drift record that every reconciliation
run must find; a run reporting zero findings is a **failed** run (D63; AT-102). The same rule
applies to the acceptance sweep.

`docs/plan/tasks/lane-0/L0-canary-000.yaml` is permanent, is never fixed, and its single
acceptance criterion is designed to fail:

```yaml
ledger_schema_version: 1
task_id: L0-canary-000
lane: 0
phase: canary
subsystem: A
canary: true
issued: 2026-08-27T09:00:00Z
issued_by: L0
priority: P0
owns_paths: []
acceptance:
  - id: AC-CANARY
    command: "echo CANARY-ALIVE"
    expect: "CANARY-DEAD"
stop_rule: "This task is a permanent instrument check. Never work on it. Never fix it."
```

```bash
bash "$CP/docs/plan/bin/verify-task.sh" L0-canary-000 >/dev/null 2>&1 \
  && echo "CANARY FAILED — the sweep is broken (S10)" || echo "CANARY OK"
```

A sweep in which everything passes, canary included, proves the sweep stopped looking — it does
not prove the programme is done.

### 9.2 Status can never be written

The only write path into a status value is git history. There is no `status:` key (enforced by
`lint-ledger.sh` rule 7), no lane can write `docs/**`, and `ledger-status.sh` writes nothing at
all. If L0 ever needs to accept a task whose acceptance commands do not pass, that is a
`force_accept:` key with a mandatory `reason:` — and force-accepts are counted:

```bash
grep -l '^force_accept:' "$CP"/docs/plan/tasks/lane-*/*.yaml | wc -l
```

Repeated force-accepts against the same acceptance criterion make it a **suspect criterion**,
exactly as SIG-32 makes a repeatedly overridden signal a suspect signal (Section 52.5). The
weekly review rewrites the criterion; it never widens the tolerance quietly.

### 9.3 Closure-quality audit

Section 53.6: *a finding closed without evidence of remediation, or one that recurs in the same
scope shortly after closure, is reopened and counted as a closure-quality defect, not as new
drift.* Applied weekly, at review item 7, to three randomly sampled `accepted` tasks:

```bash
set -euo pipefail
git -C "$CP" checkout --quiet integration && git -C "$CP" pull --quiet --ff-only
bash "$CP/docs/plan/bin/ledger-status.sh" | awk -F'\t' '$3=="accepted"{print $1}' | shuf -n3 \
  | while read -r t; do bash "$CP/docs/plan/bin/verify-task.sh" "$t"; done
```

Any `FAIL` line means an accepted task has regressed. It is reopened as a new task packet with
the **same** AT ids and invariants, and B1–B3 fall accordingly. Burn-downs are allowed to go
backwards; that is what makes them believable.

Blockers are audited the same way: every closed blocker must carry exactly one `disp-` label.

```bash
gh issue list --repo "$ORG/control-plane" --state closed --label blocker --limit 200 \
  --json number,labels --jq '.[] | select([.labels[].name | select(startswith("disp-"))] | length != 1) | .number'
```

Clean output is empty.

### 9.4 Reporting party ≠ consuming party

Section 52.5 keeps the Founder as the consumer and the Team Lead as the threshold owner
deliberately. During the build there is only L0, so the separation is structural instead of
personal: **every threshold in this document is either quoted from the specification (the
Section 53.4 response times, the Section 53.4/D84 drift budget bases, the Section 29.3 estimate
bands) or is a count with a fixed spec-derived denominator (110, 111, 46, 18, 9).** L0 cannot
loosen a threshold without editing a number this document traces to a spec line — which is a
recorded decision, not an adjustment.

---

## 10. L0 decisions raised by this file

| Id | Decision | Blocks |
|---|---|---|
| D-08-1 | Home for the ledger and generators: `docs/plan/**` in `control-plane`, a new `build-ops` repository, or a partition amendment claiming `tools/ledger/**` | Issuing the first task packet |
| D-08-2 | ~~Duplicate `SIG-43` in Section 52.2~~ — **Withdrawn** — §52.4 L4600 tiers SIG-47 P2 (not the tiered P1 D-08-2 predicted) | The signal-arming burn-down; the Section 52.4 one-tier CI check |
| D-08-3 | Who runs the daily report: L0's workstation, an L2-owned scheduled workflow, or the ops VM | The first daily report |
| D-08-4 | reserved — not issued | — |
| D-08-5 | Whether the phase burn-down is denominated in Section 98.2 week labels or in D99 subsystem complexity bands | Any statement of "behind schedule" |
| D-08-6 | Authoring the AT→phase map that Section 100 assumes and does not publish — **Decided: A** (`docs/plan/at-phase-map.yaml`) | Per-phase acceptance-test coverage |

> **D-08-2 — Withdrawn.** D-08-2 withdrawn — §52.4 L4600 tiers SIG-47 P2 (not the tiered P1 D-08-2 predicted).
>
> ~~L0 DECISION REQUIRED — D-08-2: `SIG-43` is used twice in Section 52.2~~
>
> Section 52.2 states there are *exactly forty-six signals* and the table contains 46 distinct
> identifiers across **47 rows**: `SIG-43` labels both *"Unclosed learning-loop items"* and
> *"Founder operating load"*. Section 52.4 lists `SIG-43` (Founder operating load) in P1 only,
> and D104 records the SIG-43…SIG-46 additions as Founder operating load, operating-system net
> value, change-budget breach and audit-log review staleness — so the learning-loop row is the
> one carrying a borrowed identifier. Reproduce it:
>
> ```bash
> grep -oE '\| SIG-[0-9]{2} \|' "$SPEC" | sort | uniq -c | awk '$1>1'   # -> 2 | SIG-43 |
> ```
>
> This matters here because Section 52.4 mandates a CI check that *"every SIG identifier in the
> signal table appears in exactly one priority tier"*, and one row would be untiered forever.
>
> - **Option A:** keep `SIG-43` = Founder operating load (as D104 and Section 52.4 have it) and
>   assign the unclosed-learning-loop signal a new identifier `SIG-47`, tiered P1 alongside the
>   other learning-loop measures. The count becomes 47, stated honestly per D8 and D44.
> - **Option B:** fold the unclosed-learning-loop condition into an existing signal and delete
>   the row; the count stays 46.
>
> ~~Either way this is a **specification change** and travels the platform-change process~~
> ~~(invariant 82). It is not a tracking decision, and no lane may resolve it.~~
> **Resolution:** §52.4 L4600 tiers SIG-47 as P2, not the tiered P1 this decision predicted. D-08-2 is withdrawn.

---

## 11. What a lane developer is told about all of this

Exactly one paragraph, reproduced verbatim in every task packet:

> You are not asked for status. Your progress is read from git. Do the task in your packet on
> the branch it names, touching only the paths it lists. Run the packet's self-verify command;
> when every line reads PASS, open one pull request into `integration`. If your STOP rule fires,
> open one blocker issue on the template in `docs/escalation/BLOCKER.md` and stop that task. Never
> report a percentage, never estimate a completion date, never edit `docs/**`, never edit
> `contracts/**`, and never touch a path another lane owns.

---

## 12. Session history and current programme state

*This section is written by L0 at the close of each session. It is a human log, not derived data.*
*Nothing here overrides §3 (derived status from git). It exists so L0 can re-orient quickly.*

### 12.1 Session log

| Session | Date | FD range | Key output | Status |
|---|---|---|---|---|
| Sessions 1–5 | 2026-08-27..2026-09-01 | FD-001..FD-066 | Spec analysis; 35 structural blockers identified; coherence-review BLOCKED on 6 design conflicts | COMPLETE |
| Session 6 | 2026-09-02 | — | Mechanical bug fixes (dual-plan conflict, incompatible namespace errors) resolved | COMPLETE |
| Sessions 7–10 | 2026-09-03..2026-09-07 | — | Lane coherence reviews; Phase 0 tasks L0-P0-001..L0-P0-024 issued and accepted | COMPLETE |
| Session 11 | 2026-09-07 | FD-067 | L0-P0-025 (STOP rule audit); 5/6 lane coherence reviews PASS | COMPLETE |
| Session 12 | 2026-09-08 | FD-067..070 | 92 files, 0 ORG placeholders; `contracts/project-config.sh` created; L0-P0-026 closes B-04; all 6 coherence reviews PASS | COMPLETE |
| Session 13 | 2026-09-08 | FD-071..081 | Q1-Q12 answered; FD-071..081 closed (81 total); 32 PFDs written (PFD-001..032); 6/6 coherence PASS; Phase 0 complete (26 tasks + run-phase-0.sh); L4-CONCORDANCE 103 mapped (residue 14); Commands labels complete (L1/L4/L5-07); verify_handover.sh INTACT | COMPLETE |
| Session 14 | 2026-09-08 | — | Concordance check 5/5 OK (71 FAILs fixed); L3 Commands COMPLETE (228 labels); mutation scripts placed (7 stubs); verify_handover INTACT | COMPLETE |

### 12.2 Current programme state (as of Session 13, 2026-09-08)

| Metric | Value | Notes |
|---|---|---|
| Founder decisions (FD) | FD-001..FD-081 (81 total) | All closed; FD-090..093 reserved (PENDING) |
| PFDs written | **32** (PFD-001..032) | PENDING_FOUNDER_DECISIONS.md; PFD-020..032 added in Session 13 final wave |
| Plan files | 94 | .md files in lanes/ + protocol/ |
| Phase 0 tasks (L0-P0) | 26 complete — L0-P0-001..L0-P0-026 | L0-P0-026 (FD-068, 2026-09-08) closes the B-04 blocker group; run-phase-0.sh created |
| Lane coherence reviews | 6/6 PASS | All six lanes unblocked; FD-014 gate cleared |
| Dispatch gate | CLEAR — Q1-Q12 all ANSWERED | Answered in Session 13 (2026-09-08) |
| L3 Commands blocks | 73 | All phases P1-P8 |
| L5 orphan bodies indexed | 26 | 0 remaining |
| verify_handover.sh | HANDOVER INTACT | 0 failures, 0 warnings |
| L0-04 REG items | 7 closed; 7 open | Open items need Founder values |
| decisions/open-decisions.yaml | 27 entries | — |
| `contracts/project-config.sh` | CREATED | FD-068, authored 2026-09-08; `source … check_org` idiom operative |
| ORG placeholder count | 0 | All `$ORG` / `<ORG>` placeholders resolved across 92 tracked files |
| Structural blockers (Session 5 baseline: 35) | 0 open | All 35 resolved across Sessions 6–12 |
| Remaining non-agent item | Team-tier GitHub purchase | Deferred by Founder; not a build-lane blocker; no agent action pending |
| L4-CONCORDANCE mapped | **103** (residue 14) | 21 rows added in Session 13 final wave; residue dropped 35→14 |
| L3-CONCORDANCE index | **82** (was 78) | 4 rows added in Session 13 final wave |
| L5 unclaimed orphans | **15** genuinely unclaimed bodies indexed | Covered entries annotated (12); remainder truly unclaimed |
| Commands labels | L1-00, L1-02, L1-05, L1-06, L5-07, L4-02, L4-03-write-paths, L4-04, L4-05, L4-07 complete | 185 labels added in final wave |
| L1-06 stubs | 4 tasks with prose only (T07/T08/T12/T15) | No bash block; stubs require Founder-value input before executable |
| _DECISION_DOCKET audit | 21 RESOLVED, 2 PENDING(PFD), 37 UNTRACKED | 13 Founder-required; 24 technical defaults |
| verify_handover.sh | HANDOVER INTACT | 0 failures — 2026-09-08 final run |
| Session 13 status | **COMPLETE** | All final-wave items closed |
