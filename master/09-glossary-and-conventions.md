# 09 — Glossary and Conventions

**Status:** Normative for the whole implementation programme.
**Audience:** L1–L5 AI developers and the L0 integrator.
**Authority:** Subordinate to `implementation/PARTITION.md` (frozen) and to `Research/MultiProduct_MasterSpec_v4.0.md` (the specification). Where this file and either of those disagree, they win and this file is defective — open a blocker issue (§7.1 below).

This file exists for one reason: **five agents on five branches must produce code that reads as though one author wrote it.** Every rule below is prescriptive. None is a preference. If a rule does not cover your case, you do not invent a convention — you STOP and open a blocker issue (§7.1).

---

## 0. How to use this file

| If you are about to… | Read |
| --- | --- |
| Name a file, directory or schema | §8, §9 |
| Create a branch | §4 |
| Write a commit message | §5 |
| Open a pull request | §6 |
| Hit something you cannot do | §7 |
| Write or edit YAML | §10 |
| Write or edit a JSON Schema | §11 |
| Write a test or a fixture | §12 |
| Write a self-verify command or a check script | §13 |
| Add a `make` target | §14 |
| Rebase, squash, force-push, sign | §15 |
| Write prose in a PR, issue or doc | §16, §1 |
| Cite the specification | §2.1 |

**The one absolute rule of this file:** *a name, format or identifier not fixed here and not fixed by the specification is not yours to choose.* Open a blocker issue and wait. This is the same rule as `PARTITION.md` line 47 ("No task may require designing, choosing, or interpreting").

---

## 1. Vocabulary

The specification fixes one vocabulary in **Spec §6 (Unified Terminology and Glossary)**. These documents, all code comments, all commit messages, all PR bodies and all identifiers use it without redefining it. The following table is the enforcement list: the left column is the only permitted form.

### 1.1 Terms from the specification — write this, never that

| Write this | Never write this | Why (spec) |
| --- | --- | --- |
| `business.criticality` **or** `classification.reliability_criticality` | "criticality" unqualified | §6.1 — an unqualified "criticality" is a specification defect |
| attention ranking | attention allocation, attention score | §6.2 |
| attention hours | effort points, time spent, man-hours | §6.2, §6.6 |
| Management Attention | management score, manager load rating | §6.2 — diagnostic only, never a performance score |
| the eight categories: Engineering, Review, Verification, Planning, Architecture, Incident, Operational, Coordination | any ninth category, any second taxonomy | §6.6 |
| drift classes `Green`, `Amber`, `Red`, `Blocking` | "dangerous", "correctable", "informational" | §6.7 — retired vocabulary |
| Levels 1–5: Detect, Warn, Auto-repair, Block, Escalate | "fix", "heal", "remediate" | §6.7 |
| `availability` (person lifecycle: `active`/`on_leave`/`departing`/`departed`) | "availability" meaning calendar or leave | §6.4 |
| working calendar / approved leave | availability calendar | §6.4 |
| capacity / utilisation / remaining safe bandwidth / workload | any two of these used interchangeably | §6.5 |
| shipped (the eight-condition definition) | shipped meaning merged | §6.9 |
| merged, deployed — tracked separately | "released" as a synonym for either | §6.9 |
| the designated work-management system | any vendor product name | §6.10, D18 |
| Layer A, Layer B-M, Layer B-S | "the people dashboard", "HR view" | §6.11 |
| control-plane repository / records repository | "the control plane" when one specific repository is meant | §6.12, D89 |
| Product / Repository (distinct concepts) | using them interchangeably | §101 #62 |
| capability | permission, when the registry concept is meant | §101 #11, AT-081 |
| verification contract | test plan, QA plan | §6.12, §31 |
| Bootstrap Mode / pre-onboarding mode | "temporary mode", "interim mode" | §6.12, §95, §96 |
| PLU (Product Load Unit) | "load score", "complexity points" | §6.12 |
| Gate 1 / Gate 2 / production approval / deploy — four distinct events | "approval" unqualified | §27 |
| exception (with expiry) | TODO, FIXME, "temporary" | §101 #77 |
| reconciliation, auto-repair | sync, self-heal | §6.7, §53 |
| evidence chain | audit trail, when the eleven questions are meant | §6.12, §32 |
| record store | database, table | §97.2 |
| event log, one file per event | event stream, event table | §97.3 |

### 1.2 Terms of this implementation programme — defined here

| Term | Meaning |
| --- | --- |
| **Lane** | One of the five build lanes L1–L5 defined in `PARTITION.md`. Never "team", "squad", "workstream", "track". |
| **L0** | The human/lead integrator. Never "the reviewer", "the maintainer", "the architect". |
| **Task** | The smallest unit of assignable work; carries exactly one task id (§3), one branch (§4), one PR (§6). Never "ticket", "story", "issue", "item". |
| **Phase** | A phase of Spec §98, tokenised per §3.2. Never "sprint", "milestone", "iteration". |
| **Merge train** | The fixed L1 → L4 → L2 → L3 → L5 merge order (`PARTITION.md` line 35). |
| **Lane guard** | The CI check that fails a PR touching a path the lane does not own (`PARTITION.md` line 13). |
| **CCR** | Contract Change Request — the only way a lane can cause `contracts/**` to change (`PARTITION.md` line 26; format §7.2). |
| **Blocker** | The issue a lane opens when its STOP rule fires (`PARTITION.md` line 46; format §7.1). |
| **Self-verify command** | The single command a task's acceptance criterion is checked by; its output convention is §13. |
| **STOP rule** | The literal sentence in a task that says when not to proceed (template §7.3). |

### 1.3 Spelling, person and mood

| Rule | Correct | Incorrect |
| --- | --- | --- |
| Prose is **British English**, matching the specification | organisation, utilisation, authorisation, behaviour, licence (noun) | organization, utilization, authorization, behavior, license (noun) |
| Identifiers, API paths and third-party field names are copied **verbatim**, whatever their spelling | `GET /orgs/{org}/teams`, `organization_permission` | "corrected" to `organisation` |
| Commit subjects and PR titles are **imperative mood, lower case, no full stop** | `add people registry schema v1` | `Added people registry schema v1.` |
| Documentation prose is **present tense, third person, no first person** | "The validator rejects an expired assignment." | "We reject expired assignments." / "I added a check." |
| Never use emoji anywhere in the repositories, commits, PRs or docs | `PASS: AT-033` | `✅ AT-033` |

### 1.4 Numbers, dates and units

| Quantity | Written as | Source |
| --- | --- | --- |
| Timestamp | ISO 8601, UTC, `Z` offset: `2026-09-14T02:11:00Z` | §97.1 — "stored in UTC with its offset" |
| Date | ISO 8601 calendar date: `2026-09-14` | §97.1 |
| Duration in days | integer days, field name ends `_days`: `deletion_sla_days: 30` | §51.1 |
| Business-day / working-hour rules | never computed from a runner's local time; resolved against the declared working calendar | §97.1 |
| Attention hours | multiples of `0.25`, rounded to nearest, never to zero | §97.4 |
| Digest | full `sha256:` prefixed digest, never a short form | §101 #22 |
| Third-party GitHub Action ref | full 40-character commit SHA, never a tag | §101 #85, §33.2 |
| Reusable workflow ref | pinned tag `v1`, `v2`, … | §101 #85, §60.1 |

---

## 2. Identifier spaces

### 2.1 Spec-owned identifiers — never invent one

These identifier spaces belong to the specification. **You do not create a new one, extend one, renumber one, or cite one you have not grepped.**

| Space | Format | Range in v4.0 | Lives in |
| --- | --- | --- | --- |
| Acceptance test | `AT-###` — three digits, zero-padded | AT-001 … AT-110 (110 tests) | Spec §100 |
| Invariant | plain integer, no prefix, no padding | 1 … 111 (111 invariants) | Spec §101 |
| OS health signal | `SIG-##` — two digits, zero-padded | SIG-01 … SIG-47 (47 signals) | Spec §52.2 |
| Edge case | `EC-#` — **not** zero-padded | EC-1 … EC-112 (112 cases) | Spec §102 |
| Consolidation decision | `D#` — **not** zero-padded | D1 … D110+ | Spec Appendix A |
| Section | `§N` or `§N.M` | §1 … §104, Appendix A | Spec |

**Citation format, exactly:**

| Citing | Correct | Incorrect |
| --- | --- | --- |
| A section | `Spec §97.2` | `Section 97.2 of the spec`, `[97.2]`, `§97.02` |
| An acceptance test | `AT-033` | `AT-33`, `AT033`, `at-033` |
| An invariant | `Spec §101 #47` | `INV-47`, `Invariant 47.0`, `#47` alone |
| A signal | `SIG-13` | `SIG-6`, `Signal 13` |
| An edge case | `EC-98` | `EC-098` |
| A decision | `D89` | `D-89`, `D089` |

**Verify every identifier before you write it.** From Git Bash:

```bash
set -euo pipefail
SPEC="C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md"
grep -n 'AT-033' "$SPEC" | head -1
grep -n 'SIG-13' "$SPEC" | head -1
grep -n '| D89 |' "$SPEC" | head -1
```

Batch-check every identifier in a file you have written:

```bash
set -euo pipefail
SPEC="C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md"
FILE="$1"
FAILURES=0
while read -r id; do
  grep -q "$id" "$SPEC" || { echo "FAIL: unknown identifier $id"; FAILURES=$((FAILURES + 1)); }
done < <(grep -oE '\b(AT-[0-9]{3}|SIG-[0-9]{2}|EC-[0-9]{1,3})\b' "$FILE" | sort -u)
if [ $FAILURES -eq 0 ]; then echo "PASS: citation-check"; else echo "FAIL: $FAILURES citations broken"; exit 1; fi
```

If the identifier is not in the spec, the identifier does not exist. Do not create it. Open a blocker issue.

### 2.2 Programme-owned identifiers — defined here

| Space | Format | Assigned by | Section |
| --- | --- | --- | --- |
| Task id | `L<lane>-<phase>-<seq>` | L0, in the lane task files | §3 |
| Blocker issue | GitHub issue, title format fixed | Any lane | §7.1 |
| Contract Change Request | `CCR` GitHub issue, title format fixed | Any lane | §7.2 |
| Check id (self-verify) | `<scope>-<verb>` matching the make target | Owning lane | §13.2, §14 |

### 2.3 Record and event identifiers — spec-owned formats, runtime-assigned values

These are produced by the running system, not by you, but tools and schemas you write must match the formats exactly (Spec §97.2, §97.3):

| Record type | Id format | Example |
| --- | --- | --- |
| Incident | `INC-YYYY-MM-DD-NNN` | `INC-2026-09-14-001` |
| Deployment | `DEP-YYYY-MM-DD-NNN` | `DEP-2026-09-12-014` |
| Decision | `DEC-YYYY-MM-DD-NNN` | `DEC-2026-09-10-003` |
| Demo | `DEMO-YYYY-MM-DD-NNN` | `DEMO-2026-09-11-002` |
| Event | `EVT-YYYY-MM-DD-NNNNNN` (six digits) | `EVT-2026-09-14-000317` |

`event_type` values are **lower-case, underscore-separated identifiers from the closed enum in `platform.yaml`, never free text and never renamed once shipped** (Spec §97.3).

**Correct:** `event_type: plan_approved`
**Incorrect:** `event_type: plan-approved`, `event_type: "Gate 1 approval"`, `event_type: planApproved`

---

## 3. Task id scheme

### 3.1 Shape

```
L<lane>-<phase>-<seq>
```

| Part | Values | Rules |
| --- | --- | --- |
| `<lane>` | `0`, `1`, `2`, `3`, `4`, `5` | The owning lane from `PARTITION.md`. `L0` is the integrator. |
| `<phase>` | `F0`–`F7`, `G1`–`G8`, `P1`–`P8` | See §3.2. Upper case in the task id. |
| `<seq>` | `01`–`99`, zero-padded, two digits | Ascending within `(lane, phase)`. **Never reused, never renumbered, never gap-filled.** |

**Correct:** `L1-F3-04`, `L4-G1-11`, `L0-F0-01`, `L5-P2-03`
**Incorrect:** `L1-F3-4` (not padded), `l1-f3-04` (lower case), `L1-3-04` (phase token missing letter), `T-104` (no lane), `L1-F3-04a` (suffixed), `L6-F1-01` (no lane 6 exists)

A task id is immutable once written into a lane task file. If a task turns out to be two tasks, **L0** splits it and issues a new id; a lane never renumbers, never subdivides, never merges task ids.

### 3.2 Phase tokens

Spec §98 uses three tiers, and two of them number from 1, so the raw numbers collide. This programme therefore uses these tokens, and only these:

| Spec §98 phase | Token | Note |
| --- | --- | --- |
| Contract freeze (`PARTITION.md` line 26) | `F0` | L0 only; not a Spec §98 phase — the programme's own Phase 0 |
| Phase 1 — Foundation | `F1` | Spec §98.2 |
| Phase 2 — Visibility | `F2` | Spec §98.2 |
| Phase 3 — Registries and Standards | `F3` | Spec §98.2 |
| Phase 4 — Environments | `F4` | Spec §98.2 |
| Phase 5 — Verification | `F5` | Spec §98.2 |
| Phase 6 — Delivery Pipeline | `F6` | Spec §98.2 |
| Phase 7 — GSD Activation | `F7` | Spec §98.2 |
| Phases G1–G8 — Governance tier | `G1`…`G8` | Spec §98.5; tokens identical to the spec |
| Phases P1–P8 — People tier | `P1`…`P8` | Spec §98.6; tokens identical to the spec |

**`F` is a programme token, not a spec token.** When citing the spec in prose, write "Phase 3 (Spec §98.2)"; when writing a task id, branch, label or trailer, write `F3`. Never write "Phase F3" in prose about the specification.

**Incorrect:** using `P3` to mean Foundation Phase 3. `P3` is People-tier Phase 3, always.

---

## 4. Branch naming

`PARTITION.md` line 34 fixes the shape: `lane/N/<phase>-<task>`. This section fixes the two slots.

```
lane/<N>/<phase-lower>-<seq>-<slug>
```

| Part | Rule |
| --- | --- |
| `<N>` | `1`–`5`. A lane never creates a branch under another lane's number. |
| `<phase-lower>` | The §3.2 token, lower case: `f3`, `g1`, `p2` |
| `<seq>` | The task id's two-digit sequence |
| `<slug>` | 2–5 words, lower case, hyphen-separated, ASCII letters/digits/hyphens only, ≤ 40 characters, describing the deliverable not the activity |

Full regex covering all branch types (permissive — a non-matching branch name is reported, not rejected at exit 1):

```
^(lane/[1-5]/(f[0-7]|g[1-8]|p[1-8])-[0-9]{2}-[a-z0-9]+(-[a-z0-9]+){1,4}|l0/.+|integration|main)$
```

**Correct**

```bash
set -euo pipefail
git switch -c lane/1/f3-04-people-registry-schema
git switch -c lane/2/f6-02-deploy-production-template
git switch -c lane/4/g1-11-event-envelope-schema
```

**Incorrect**

```bash
set -euo pipefail
git switch -c feature/people-schema          # no lane, no phase
git switch -c lane/1/people-schema           # no phase token, no seq
git switch -c lane/1/F3-04-PeopleSchema      # upper case
git switch -c lane/1/f3-4-schema             # seq not padded
git switch -c lane/1/f3-04-fix-the-thing     # slug names an activity, not a deliverable
git switch -c lane/1/f3-04-add-schemas-and-validators-and-fixtures-for-people-and-roles  # slug too long
```

**L0 branches:** `l0/<phase-lower>-<seq>-<slug>`, merging to `integration`. `main` receives only `integration` (`PARTITION.md` line 32).

**Records repository (`control-plane-records`, L4):** the same scheme, `lane/4/...`.

**Branch lifetime:** one task, less than one day, rebased on `integration` immediately before the PR (`PARTITION.md` line 34). Delete the branch on merge.

```bash
set -euo pipefail
git fetch origin
git rebase origin/integration
git push --force-with-lease origin HEAD
```

Never `git push --force`. Always `--force-with-lease`. Never force-push `integration` or `main`. Never force-push after a review has been submitted — approval is bound to the most recent reviewable push (Spec §101 #9), so a force-push silently discards it.

---

## 5. Commit message format

### 5.1 The template — exact

```
<type>(<scope>): <subject>

<body>

Task-Id: <task-id>
Lane: L<N>
Phase: <phase-token>
Spec: <citations>
AT: <at-ids or "none">
Invariant: <invariant numbers or "none">
Agent-Authored: <true|false>
Self-Verify: <command>
```

Blank line after the subject. Blank line before the trailer block. The trailer block is the last thing in the message, one trailer per line, `Key: value`, in the order shown, no blank lines inside it.

### 5.2 Header rules

| Field | Rule |
| --- | --- |
| `<type>` | One of: `feat`, `fix`, `schema`, `test`, `ci`, `docs`, `chore`, `refactor`. No others. |
| `<scope>` | One token from §5.3. Must be a path the lane owns. |
| `<subject>` | Imperative, lower case, no trailing full stop, ≤ 60 characters. |
| Whole header | ≤ 72 characters including `<type>(<scope>): `. |

### 5.3 Scope tokens — enumerated from `PARTITION.md`, one per owned path

| Lane | Permitted `<scope>` tokens | Owned path |
| --- | --- | --- |
| L1 | `schemas-registry`, `schemas-product`, `registries`, `validators-registry` | `schemas/registry/**`, `schemas/product/**`, `registries/**`, `validators/registry/**` |
| L2 | `workflows`, `templates-workflows`, `evidence` | `.github/workflows/**`, `templates/workflows/**`, `tools/evidence/**` |
| L3 | `reconciler`, `provision`, `validators-drift` | `reconciler/**`, `tools/provision/**`, `validators/drift/**` |
| L4 | `records`, `events`, `schemas-records`, `metrics`, `tools-records` | `control-plane-records` (all), `schemas/records/**`, `metrics/**`, `tools/records/**` |
| L5 | `access`, `infra`, `ops-vm`, `notify`, `assets` | `access/**`, `infra/**`, `ops-vm/**`, `notify/**`, `assets/**` |
| L0 | `contracts`, `codeowners`, `docs`, `root`, `makefile` | `contracts/**`, `CODEOWNERS`, `docs/**`, root files, `Makefile` |

A commit whose `<scope>` is not on its lane's row is a lane-guard violation waiting to happen. If you believe you need a foreign scope, **STOP** — that is a Contract Change Request (§7.2) or a blocker (§7.1), not a commit.

### 5.4 Trailer rules

| Trailer | Required | Value |
| --- | --- | --- |
| `Task-Id:` | Always | Exactly one task id, §3 format |
| `Lane:` | Always | `L0`–`L5`, matching the task id's lane |
| `Phase:` | Always | The §3.2 token, upper case |
| `Spec:` | Always | One or more citations, comma-separated, §2.1 format. `Spec: none` is never valid — every task implements something. |
| `AT:` | Always | Comma-separated `AT-###`, or the literal `none` |
| `Invariant:` | Always | Comma-separated integers, or the literal `none` |
| `Agent-Authored:` | Always | `true` for any commit an AI developer authored — which is every lane commit (Spec §97.2 requires the `agent_authored` flag; this trailer is its git-side carrier) |
| `Self-Verify:` | Always | The single command from §13 that proves the commit's claim |

### 5.5 Correct and incorrect

**Correct**

```
schema(schemas-registry): add people registry schema v1

Adds the JSON Schema for people.yaml at registry_version 1, with
additionalProperties false and an explicit closed enum for
availability. Rejects an assignment whose end_date is absent for a
non-employee.

Task-Id: L1-F3-04
Lane: L1
Phase: F3
Spec: §7, §60.2, §101 #58
AT: AT-002, AT-008
Invariant: 50, 58
Agent-Authored: true
Self-Verify: make schemas-registry-validate
```

**Incorrect** — with the reason for each

```
Added people schema.                       # past tense, capitalised, full stop, no type/scope
feat: people schema                        # no scope
feat(schemas): people schema               # scope not on the enumerated list
feat(schemas-registry): add schema         # subject says nothing
WIP                                        # no WIP commits reach a PR
fix(reconciler): tweak                      # L1 committing an L3 scope
feat(schemas-registry): add people registry schema v1 and roles registry schema v1 and the validator  # two tasks, one commit
```

```
feat(schemas-registry): add people registry schema v1
Task-Id: L1-F3-04                          # no blank line before the trailer block
```

### 5.6 One commit, one task

A commit belongs to exactly one task id. A branch may carry several commits; every one of them carries the same `Task-Id:`. A commit that would need two task ids is two commits.

### 5.7 Local enforcement — install this hook on every lane clone

> **NOTE:** The commit-msg hook previously documented here has been removed. Its `Task-Id` validation regex (`L[0-5]-(F[0-7]|G[1-8]|P[1-8])-[0-9]{2}`) rejects valid task ids produced by four of the six lanes (L0, L1, L2, L4) and is therefore a commit blocker. A replacement requires a crosswalk of all lane task-id formats agreed by L0. Until that crosswalk exists in `contracts/**`, `Task-Id` format is validated by human review on the PR, not by a hook. Open a CCR if you need enforced local validation.

Optional message template, to avoid retyping the trailers:

```bash
set -euo pipefail
cat > "$HOME/.gitmessage-lane" <<'EOF'


Task-Id: 
Lane: 
Phase: 
Spec: 
AT: none
Invariant: none
Agent-Authored: true
Self-Verify: 
EOF
git config commit.template "$HOME/.gitmessage-lane"
```

---

## 6. Pull request format

### 6.1 Title — exact

```
[<task-id>] <type>(<scope>): <subject>
```

The part after the bracket is byte-identical to the first commit's header (§5.2). Total ≤ 72 characters.

**Correct:** `[L1-F3-04] schema(schemas-registry): add people registry schema v1`
**Incorrect:** `[L1-F3-04] Add people schema` · `L1-F3-04: people schema` · `Draft: people schema` · `[lane 1] schema(...): ...`

### 6.2 Body — exact template, all sections, in this order

````markdown
## Task
<task-id> — <one-line task title, copied verbatim from the lane task file>

## Lane and paths
Lane: L<N>
Paths touched (every one owned by this lane per PARTITION.md):
- <path>
- <path>

## Spec references
- §<section> — <what it requires>
- AT-<nnn> — <what it tests>
- §101 #<n> — <the invariant upheld>

## What changed
<Three sentences maximum. What now exists that did not exist before.>

## Acceptance criteria
- [ ] <criterion 1, stated as an observable fact>
- [ ] <criterion 2>

## Self-verify transcript
```bash
$ <the exact command>
<the exact output, unedited, including the final PASS line>
```

## Agent-authored
Agent-Authored: true

## STOP conditions
<"None encountered." or the exact STOP condition and the blocker issue number.>

## Contract Change Request
<"None." or "CCR #<issue number>" — see 09-glossary-and-conventions.md §7.2.>
````

### 6.3 Body rules

| Rule | Correct | Incorrect |
| --- | --- | --- |
| Every checkbox in **Acceptance criteria** is ticked before review is requested; an unticked box means the PR is not ready | `- [x] every fixture under invalid/ is rejected` | `- [ ] mostly working` |
| The self-verify transcript is **pasted, not described**, and includes the command and the final `PASS:` line | see §13.2 | "tests pass locally" |
| **Paths touched** lists every path in `git diff --name-only origin/integration...HEAD` | complete list | "various files under schemas/" |
| A PR delivers **exactly one task id** | one `## Task` line | two task ids, or "and also fixed…" |
| No screenshots, no logs beyond the transcript, no prose narrative of the work | — | "First I tried X, then Y…" |

Produce the paths list mechanically:

```bash
git fetch origin
git diff --name-only origin/integration...HEAD | sed 's/^/- /'
```

Confirm every path is owned by your lane before opening the PR:

```bash
set -euo pipefail
# Replace the pattern with your lane's owned prefixes from PARTITION.md.
git diff --name-only origin/integration...HEAD \
  | grep -vE '^(schemas/registry/|schemas/product/|registries/|validators/registry/)' \
  && echo "FAIL: foreign path in diff — do not open this PR" \
  || echo "PASS: lane-paths"
```

### 6.4 Draft, review and merge

| Rule | Detail |
| --- | --- |
| A PR is opened **ready**, never as a draft, unless the STOP rule fired | drafts are for the background machine layer (Spec §101 #18), not for lanes |
| Base branch is always `integration` | never `main`, never another lane's branch (`PARTITION.md` line 36) |
| ~~Merge method is **squash**~~ — **superseded by REG-012** (`allow_squash_merge=false`; `required_signatures` applies). Use the repository's configured merge method; do not set squash manually. §6.5 below is retained for reference but does not apply while REG-012 is in force. | — |
| A lane never merges its own PR into `integration` outside the merge train order | L1 → L4 → L2 → L3 → L5 (`PARTITION.md` line 35) |
| A lane never merges, rebases, reviews-and-approves, or force-pushes another lane's branch | `PARTITION.md` line 36 |

### 6.5 Squash commit message

> **NOTE — superseded by REG-012:** `allow_squash_merge=false` disables squash merges. This section is retained for reference only. If REG-012 is not yet in effect on your repository, the format below still applies.

Because squashing discards the individual commits' trailers, the squash commit carries the trailer block explicitly:

```
schema(schemas-registry): add people registry schema v1 (#412)

Task-Id: L1-F3-04
Lane: L1
Phase: F3
Spec: §7, §60.2, §101 #58
AT: AT-002, AT-008
Invariant: 50, 58
Agent-Authored: true
Self-Verify: make schemas-registry-validate
```

---

## 7. Blockers, CCRs and STOP rules

### 7.1 Blocker issue

Opened when a task's STOP rule fires, or when this file does not cover a naming decision you need. The canonical template file lives at `docs/escalation/BLOCKER.md`; the body format below is the authoritative definition.

**Title:** `BLOCKER [<task-id>]: <one line, imperative, ≤ 60 chars>`
**Labels:** `blocker`, `lane/<N>`, `phase/<phase-lower>`
**Body:**

```markdown
## Task
<task-id>

## STOP condition that fired
<the exact sentence from the task file>

## What I observed
<the exact command run and its exact output>

## What I need decided
<one question, answerable yes/no or by naming one option from a list>

## Options I can see
1. <option>
2. <option>

## What I have NOT done
<confirm no foreign path was touched, no convention was invented, no branch was pushed>
```

**Correct title:** `BLOCKER [L3-F3-07]: reconciler needs a contracts/ field not present`
**Incorrect:** `Help` · `Question about schemas` · `BLOCKER: something is wrong` (no task id)

Then stop. Do not proceed, do not guess, do not open the PR.

### 7.2 Contract Change Request

The only permitted route to a change in `contracts/**` (`PARTITION.md` line 26). A lane **never** edits `contracts/**` and never opens a PR against it.

**Title:** `CCR [<task-id>]: <the contract field or file that must change>`
**Labels:** `ccr`, `lane/<N>`
**Body:**

```markdown
## Contract file
contracts/<path>

## Change requested
<Exact before and after, as a diff fragment.>

## Why the task cannot proceed without it
<One paragraph. Cite the spec section that requires the field.>

## Lanes affected
<Which other lanes consume this contract, from PARTITION.md.>

## Blocked task
<task-id> — blocked as of <date>
```

A CCR is a GitHub issue, never a file, because `docs/**` and `contracts/**` are L0-owned and a lane may not write them.

### 7.3 STOP rule sentence template

Every task in the lane files carries one. This is its canonical form; use it verbatim with the placeholders filled:

```
STOP: if <observable condition>, do not proceed — open a blocker issue titled
"BLOCKER [<task-id>]: <condition>" and make no further commits on this branch.
```

**Correct:** `STOP: if contracts/product.contract.yaml does not exist on origin/integration, do not proceed — open a blocker issue titled "BLOCKER [L1-F3-04]: contracts/product.contract.yaml absent" and make no further commits on this branch.`
**Incorrect:** `STOP: if something looks wrong, ask.` (not observable, no action, no title)

---

## 8. Repository and directory conventions

### 8.1 The four repositories (`PARTITION.md` lines 5–11)

| Repository | Holds | Protection |
| --- | --- | --- |
| `control-plane` | registries, contracts, schemas, validators, reconciler, provisioning, reusable workflows, access/infra config | Full branch protection. **No machine bypass actor** (D89) |
| `control-plane-records` | `records/**`, `events/**` | No review protection; a no-bypass ruleset blocks force-push and deletion (D107); commits signed by the writing identity |
| `product-template` | the scaffold `create-product` consumes | — |
| `<product>` × 8 | the live products | onboarded, not built by this programme |

### 8.2 `control-plane` layout — owner per directory

Every directory has exactly one owner. This table is `PARTITION.md` lines 17–22 rendered as a tree; it adds no path and removes none.

```
control-plane/
├── contracts/                 L0   frozen at F0; lanes read, never write
├── schemas/
│   ├── registry/              L1   people, roles, assignments, platform, topology, …
│   ├── product/               L1   product.yaml, verification contract, service.yaml
│   └── records/               L4   record envelope, event envelope
├── registries/                L1   the registry instance files themselves
├── validators/
│   ├── registry/              L1   schema + referential + date-rule validators
│   └── drift/                 L3   declared-vs-actual comparison validators
├── reconciler/                L3   the reconciliation engine
├── tools/
│   ├── provision/             L3   create-product, add-person, change-role, remove-person
│   ├── evidence/              L2   verify-digest-chain and the evidence-chain query
│   └── records/               L4   record-decision CLI and record writers
├── metrics/                   L4   metric definitions and computation
├── templates/
│   └── workflows/             L2   the reusable workflow library
├── access/                    L5   Teams, permission model, secret tiers
├── infra/                     L5   ops-VM compose, Grafana/DevLake/Prometheus provisioning
├── ops-vm/                    L5   ops-VM build and rebuild procedure
├── notify/                    L5   notification routing
├── assets/                    L5   asset inventory and deadline watch
├── docs/                      L0
├── .github/workflows/         L2   the control-plane repository's own CI
├── CODEOWNERS                 L0
├── Makefile                   L0   see §14
└── .gitattributes             L0   see §15.1
```

### 8.3 `control-plane-records` layout — L4 owns all of it

Paths are fixed by Spec §97.2 and §97.3. Do not add a store; do not rename one.

```
control-plane-records/
├── records/
│   ├── incidents/          postmortems/        uat/
│   ├── estimates/          deployments/        restore-tests/
│   ├── decisions/          decisions/pending/  breaches/
│   ├── deletion-requests/  security-reviews/   eval/
│   ├── launches/           demos/              support/
│   ├── onboarding/         leave/
└── events/
    └── <YYYY-MM-DD>/
```

### 8.4 The directory-per-item rule

`PARTITION.md` line 27: **no shared mutable file, ever.** One file per event, per record, per schema, per fixture, per check.

**Correct**

```
schemas/registry/people.v1.schema.json
schemas/registry/roles.v1.schema.json
events/2026-09-14/EVT-2026-09-14-000317.yaml
```

**Incorrect**

```
schemas/registry/all-schemas.json           # a registry-of-everything
schemas/registry/index.yaml                 # a shared index two lanes would both append to
events/2026-09.yaml                         # a shared period file; parallel runs contend
validators/registry/checks.txt              # an append-list
```

If your task appears to require appending to a shared file, it does not: **STOP** and open a blocker. The whole anti-conflict design rests on this rule.

### 8.5 Never reach into another lane's tree

`PARTITION.md` line 28. A lane consumes another lane's output only through `contracts/**` or a published artifact.

**Correct:** `from contracts.product import CONTRACT_V1_SCHEMA_PATH`, reading `contracts/product.contract.yaml`
**Incorrect:** `import ../../validators/registry/people_validator`, `open("../reconciler/state.json")`, a relative `$ref` from an L4 schema into `schemas/registry/`

---

## 9. File naming

### 9.1 General

| Rule | Correct | Incorrect |
| --- | --- | --- |
| Lower case, ASCII, hyphen-separated (kebab-case) | `create-product.py`, `deploy-production.yml` | `CreateProduct.py`, `create_product.PY`, `create product.py` |
| No spaces, no upper case, no non-ASCII, ever | `restore-test.yml` | `Restore Test.yml` |
| Python module files are the one exception: `snake_case.py` (import syntax forbids hyphens) | `people_validator.py` | `people-validator.py` |
| Executables invoked by name use kebab-case | `tools/provision/create-product.py` invoked as `make provision-create-product` | — |
| One concept per file; the filename names the concept, not the activity | `people.v1.schema.json` | `schema-work.json`, `new-stuff.yaml` |
| Files end with a single trailing newline, UTF-8, no BOM | — | CRLF, BOM, no final newline |

### 9.2 Extension rules — binding

| Extension | Where | Rule |
| --- | --- | --- |
| `.yml` | **only** under `.github/workflows/` and `templates/workflows/` | GitHub Actions files are named by the spec: `ci.yml`, `build.yml`, `deploy-staging.yml`, `deploy-production.yml`, `migrate.yml`, `restore-test.yml`, `restore-production.yml`, `background-queue.yml` (Spec §33.2) |
| `.yaml` | **everywhere else** | registries, records, events, schemas' instance data, configuration |
| `.json` | JSON Schema files only | §11 |
| `.sh` | POSIX shell scripts | §13.3 |
| `.py` | Python | §13.3 |
| `.md` | Markdown documents | §16 |
| `.mk` | make fragments | §14 |

**Correct:** `registries/people.yaml`, `.github/workflows/ci.yml`
**Incorrect:** `registries/people.yml`, `.github/workflows/ci.yaml`

### 9.3 Schema files

```
schemas/<family>/<entity>.v<N>.schema.json
```

**Correct**

```
schemas/registry/people.v1.schema.json
schemas/registry/roles.v1.schema.json
schemas/product/product.v1.schema.json
schemas/product/product.v2.schema.json      # v1 stays; both are supported (Spec §60.2)
schemas/records/event-envelope.v1.schema.json
```

**Incorrect**

```
schemas/registry/people-schema.json         # version missing
schemas/registry/people_v1.json             # underscore, and ".schema" missing
schemas/registry/people.schema.v1.json      # wrong order
schemas/registry/people.v1.2.schema.json    # contract versions are integers (Spec §60.2)
```

A shipped schema version file is **never edited in place** once its tag exists — a change is a new `v<N+1>` file beside it (Spec §60.2, §101 #47).

### 9.4 Record and event files (Spec §97.2, §97.3)

```
records/<store>/<YYYY-MM-DD>-<product>-<NNN>.yaml
events/<YYYY-MM-DD>/EVT-<YYYY-MM-DD>-<NNNNNN>.yaml
```

**Correct:** `records/incidents/2026-09-14-solvox-001.yaml`, `events/2026-09-14/EVT-2026-09-14-000317.yaml`
**Incorrect:** `records/incidents/solvox-incident.yaml` (no date, no sequence), `events/EVT-317.yaml` (no date directory, sequence not padded)

### 9.5 Test and fixture files

See §12.

### 9.6 Documents of this programme

```
implementation/master/<NN>-<slug>.md
implementation/lanes/<lane>-<NN>-<slug>.md
```

Two-digit prefix, hyphen, kebab-case slug. **Correct:** `09-glossary-and-conventions.md`. **Incorrect:** `9-glossary.md`, `Glossary.md`, `09_glossary_and_conventions.md`.

---

## 10. YAML style

### 10.1 The rules

| # | Rule | Correct | Incorrect |
| --- | --- | --- | --- |
| 1 | Two-space indent. Never tabs. | two spaces per level, as in §10.2 | four spaces, eight spaces, tabs, mixed |
| 2 | Sequence items indented **under** their key | `products:` then `  - name: solvox` | `products:` then `- name: solvox` at column 0 |
| 3 | Keys are `lower_snake_case` | `deletion_sla_days: 30` | `deletionSlaDays`, `Deletion-SLA-Days` |
| 4 | Enum values are `lower_snake_case` | `availability: on_leave` | `availability: On Leave` |
| 5 | **The one capitalised enum:** drift classes | `class: Blocking` | `class: blocking` (Spec §6.7 — CI rejects anything but Green/Amber/Red/Blocking) |
| 6 | Severity keeps its spec form | `severity: SEV-2` | `severity: sev2`, `severity: 2` |
| 7 | Booleans are `true`/`false` only | `pre_onboarding: false` | `yes`, `no`, `on`, `off`, `True` |
| 8 | Strings unquoted unless ambiguous; **always** quote a string that would otherwise parse as a bool, number, date or null | `version: "1.0"`, `country: "NO"` | `version: 1.0`, `country: NO` (parses as `false`) |
| 9 | Timestamps and dates unquoted, ISO 8601 (matching Spec §97.2 examples) — and loaded per §10.3 | `detected: 2026-09-14T02:11:00Z` | `detected: 14/09/2026`, `detected: "Sept 14"` |
| 10 | Nulls are written `null`, never empty, never `~` | `rollback_of: null` | `rollback_of:`, `rollback_of: ~` |
| 11 | One document per file. No `---` separator, no multi-document files. | a single mapping at the root | `---` blocks stacked in one file |
| 12 | No anchors, aliases or merge keys (`&`, `*`, `<<`) — they defeat line-level diffing and confuse validators | repeat the block | `<<: *defaults` |
| 13 | No flow style for mappings or multi-item sequences | block style | `{a: 1, b: 2}`, `[x, y, z]` — except a genuinely short closed list, e.g. `supported: [v3, v4]` as in Spec §60.1 |
| 14 | Comments use `# ` (hash, one space) and sit **above** the key they explain | see §10.2 | trailing comments on data lines |
| 15 | Key order in an instance file matches the `properties` order of its schema | see §11.4 | alphabetical, or arbitrary |
| 16 | Line length ≤ 120 characters | — | 200-character prose values |
| 17 | Every file opens with a two-line header comment: what it is, and its spec section | see §10.2 | no header |
| 18 | The version field is the **first key** in the file | `registry_version: 1` first | version buried mid-file |
| 19 | No `TODO`, `TBD`, `FIXME`, `XXX`, `???` anywhere | an `exceptions.yaml` entry with an expiry | `owner: TODO` (Spec §101 #77) |

### 10.2 A conforming file

```yaml
# people.yaml — the People Registry (Spec §7).
# Schema: schemas/registry/people.v1.schema.json
registry_version: 1
people:
  # Employment type drives the mandatory-end-date rule (Spec §101 #58).
  - login: dev-a
    display_name: Dev A
    employment_type: employee
    availability: active
    start_date: 2025-04-01
    end_date: null
  - login: spec-b
    display_name: Specialist B
    employment_type: contractor
    availability: active
    start_date: 2026-01-15
    end_date: 2026-06-30
```

### 10.3 Loading YAML — binding, because a wrong loader is a cross-lane bug

YAML 1.1 loaders coerce `2026-09-14` into a date object and `no` into `false`. Schemas validate JSON, where both are strings. Every tool in this programme loads control-plane YAML with the implicit timestamp resolver removed, so dates arrive as strings and round-trip unchanged:

```python
import yaml


class ControlPlaneLoader(yaml.SafeLoader):
    """Loads control-plane YAML with timestamps left as strings."""


ControlPlaneLoader.yaml_implicit_resolvers = {
    key: [(tag, regexp) for tag, regexp in resolvers
          if tag != "tag:yaml.org,2002:timestamp"]
    for key, resolvers in ControlPlaneLoader.yaml_implicit_resolvers.items()
}


def load(path):
    with open(path, encoding="utf-8") as handle:
        return yaml.load(handle, Loader=ControlPlaneLoader)
```

**Correct:** every validator, reconciler and record tool imports this loader.
**Incorrect:** `yaml.safe_load`, `yaml.load(..., Loader=yaml.FullLoader)`, `yaml.unsafe_load` — the first silently changes types, the last two execute arbitrary tags.

### 10.4 The lint configuration — L0 places this at the repository root at F0; every lane's YAML must pass it

```yaml
# .yamllint.yaml — YAML style gate for the control-plane repositories.
# Convention source: implementation/master/09-glossary-and-conventions.md §10
extends: default
rules:
  braces: {forbid: non-empty}
  brackets: {max-spaces-inside: 0}
  comments: {require-starting-space: true, min-spaces-from-content: 2}
  comments-indentation: enable
  document-start: disable
  empty-values: enable
  indentation: {spaces: 2, indent-sequences: true}
  key-duplicates: enable
  line-length: {max: 120, allow-non-breakable-words: true}
  new-line-at-end-of-file: enable
  octal-values: {forbid-implicit-octal: true, forbid-explicit-octal: true}
  quoted-strings: {required: only-when-needed}
  trailing-spaces: enable
  truthy: {allowed-values: ["true", "false"]}
```

Run it:

```bash
yamllint -c .yamllint.yaml registries/ schemas/ && echo "PASS: yamllint"
```

---

## 11. JSON Schema conventions

### 11.1 Dialect, identity and header

Every schema file begins with exactly these six keys, in this order (the last two are structural, not identity, fields — see §11.2):

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "urn:multiproduct:schemas:people:v1",
  "title": "People Registry v1",
  "description": "The People Registry declaration. Spec §7; registry_version per Spec §60.2.",
  "type": "object",
  "additionalProperties": false
}
```

The `$id` namespace is fixed by **L0 DECISION REQUIRED 1** (§19, closed): a URN, `urn:multiproduct:schemas:<type>:<version>` — no host or domain is needed.

| Key | Rule |
| --- | --- |
| `$schema` | Draft 2020-12, identical string in every file (§19 Decision 2, closed — Option A) |
| `$id` | `urn:multiproduct:schemas:<type>:<version>`; `<type>` is the entity name (e.g. `people`, `product`); `<version>` is `v<N>` matching the schema file's version |
| `title` | Human name, title case, includes the version |
| `description` | One sentence, ending in a full stop, **citing the spec section it implements** |

### 11.2 Structural rules

| # | Rule | Why |
| --- | --- | --- |
| 1 | `"additionalProperties": false` on **every** object, root and nested | Fail-closed (Spec §101 #79, #80). An unknown key is a defect, never a feature. |
| 2 | `required` lists keys in the same order as `properties` declares them | Diffs stay readable; §11.4 key ordering follows from it |
| 3 | Closed sets use `enum`, never `pattern` | `event_type`, `availability`, drift class, severity |
| 4 | Enum values are listed in the spec's own order, not alphabetised | The spec's order is meaningful (e.g. Levels 1–5) |
| 5 | No `default` anywhere | A default hides an omission; declared state is declared, not inferred (Spec §101 #79) |
| 6 | Every property carries a `description`; every constraint a human can trip carries one too | The error message is the description |
| 7 | Shared shapes live in `$defs` and are referenced `#/$defs/<name>` | One definition per shape |
| 8 | Cross-file `$ref` is permitted **only** to a published schema under `contracts/**` | `PARTITION.md` line 28 — never `$ref` into another lane's tree |
| 9 | A property is never deleted; it is marked `"deprecated": true` | Append-only (Spec §101 #47, §60.2) |
| 10 | Dates and timestamps declare **both** `format` and `pattern` | `format` is annotation-only in 2020-12; without the pattern nothing is enforced |
| 11 | Integers use `"type": "integer"` with explicit `minimum` | An unbounded count is not a constraint |
| 12 | The version field is the first entry in `properties` and is `"const": <N>` in a versioned schema | A v1 schema accepts only `registry_version: 1` |

### 11.3 Date and identifier patterns — copy these verbatim

```json
{
  "$defs": {
    "date": {
      "type": "string",
      "format": "date",
      "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$",
      "description": "ISO 8601 calendar date. Spec §97.1."
    },
    "timestamp_utc": {
      "type": "string",
      "format": "date-time",
      "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$",
      "description": "ISO 8601 instant in UTC with offset. Spec §97.1."
    },
    "digest": {
      "type": "string",
      "pattern": "^sha256:[0-9a-f]{64}$",
      "description": "Full artifact digest. Spec §101 #22."
    },
    "event_id": {
      "type": "string",
      "pattern": "^EVT-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{6}$",
      "description": "Event identifier. Spec §97.3."
    },
    "drift_class": {
      "type": "string",
      "enum": ["Green", "Amber", "Red", "Blocking"],
      "description": "The single drift scale. Spec §6.7."
    }
  }
}
```

### 11.4 Correct and incorrect

**Correct**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "urn:multiproduct:schemas:people:v1",
  "title": "People Registry v1",
  "description": "The People Registry declaration. Spec §7.",
  "type": "object",
  "additionalProperties": false,
  "required": ["registry_version", "people"],
  "properties": {
    "registry_version": {"const": 1, "description": "Contract version. Spec §60.2."},
    "people": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["login", "display_name", "employment_type", "availability", "start_date", "end_date"],
        "properties": {
          "login": {"type": "string", "pattern": "^[a-z0-9][a-z0-9-]{0,38}$",
                    "description": "GitHub login; the identity bridge key. Spec §99.5."},
          "display_name": {"type": "string", "minLength": 1},
          "employment_type": {"type": "string", "enum": ["employee", "contractor", "temporary"]},
          "availability": {"type": "string", "enum": ["active", "on_leave", "departing", "departed"],
                           "description": "Lifecycle state only, never calendar. Spec §6.4."},
          "start_date": {"$ref": "#/$defs/date"},
          "end_date": {"oneOf": [{"$ref": "#/$defs/date"}, {"type": "null"}],
                       "description": "Mandatory for non-employees. Spec §101 #58."}
        }
      }
    }
  }
}
```

**Incorrect** — each line is a rule broken

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",   // wrong dialect
  "title": "people",                                       // no version, not a name
  "type": "object",                                        // no $id, no description
  "properties": {
    "people": {"type": "array"},                           // no item shape at all
    "availability": {"type": "string"},                    // open string where a closed enum exists
    "start_date": {"type": "string", "format": "date"},    // format without pattern enforces nothing
    "role": {"type": "string", "default": "developer"}     // default hides an omission
  }
}
```
(`additionalProperties` absent, `required` absent — the schema accepts an empty object.)

### 11.5 Schema versioning workflow (Spec §60.2)

```
v2 written beside v1 — never replacing it
    -> validator supports both v1 and v2
    -> migration written
    -> canary products migrate first
    -> fleet migrates gradually
    -> v1 deprecation deadline published in platform.yaml
    -> v1 removed only after every product has migrated
```

**Never** edit `people.v1.schema.json` to add a field. Write `people.v2.schema.json`.

---

## 12. Test naming and layout

### 12.1 Directory layout

```
<owned-root>/
├── <code>
└── tests/
    ├── fixtures/
    │   ├── valid/<case>.yaml
    │   └── invalid/<rule-violated>.yaml
    ├── golden/<case>.expected.json
    ├── test_<unit>.py            # Python unit tests
    └── <at-or-inv>.bats          # shell-level tests, §12.4
```

Tests live inside the lane's owned tree, never in a shared top-level `tests/` — that would be a shared mutable directory two lanes append to (`PARTITION.md` line 27).

### 12.2 Unit test naming

```
test_<entity>_v<N>_<accepts|rejects>_<condition>
```

| Correct | Incorrect |
| --- | --- |
| `test_people_v1_rejects_missing_end_date_for_contractor` | `test_people_1` |
| `test_people_v1_accepts_minimal_valid_registry` | `test_it_works` |
| `test_event_envelope_v1_rejects_unknown_event_type` | `testEventEnvelope` |
| `test_product_v2_accepts_transitional_compatibility` | `test_schema_validation_2` |

The name states the **behaviour under test**, never the function called. A reader who sees only the test name must know what broke.

### 12.3 Fixtures — one fixture, one rule

| Rule | Correct | Incorrect |
| --- | --- | --- |
| An `invalid/` fixture violates exactly **one** rule, and its filename names that rule | `invalid/missing-end-date-for-contractor.yaml` | `invalid/bad.yaml`, `invalid/case3.yaml` |
| Every `invalid/` fixture has exactly one `rejects` test | 1:1 | one test looping over a directory |
| `valid/` fixtures are named for the shape they exercise | `valid/minimal.yaml`, `valid/all-optional-fields.yaml` | `valid/test1.yaml` |
| Fixtures use fictitious data only; **no customer data ever** | `product: solvox` | any real customer name or record (Spec §101 #111) |

### 12.4 Acceptance and invariant tests — ids from the spec, never invented

| Kind | Path and name | Example |
| --- | --- | --- |
| Acceptance test (Spec §100) | `tests/acceptance/at-<nnn>-<slug>.bats` | `tests/acceptance/at-102-seeded-reconciliation-canary.bats` |
| Invariant test (Spec §101) | `tests/invariants/inv-<n>-<slug>.bats` | `tests/invariants/inv-47-append-only-history.bats` |
| Signal test (Spec §52.2) | `tests/signals/sig-<nn>-<slug>.bats` | `tests/signals/sig-13-failed-reconciliations.bats` |

`bats` test names carry the identifier and the behaviour:

```bash
set -euo pipefail
@test "AT-033 no auto-loosening: reconciler raises a stricter production control for review" {
  run ./reconciler/reconcile --dry-run --fixture tests/fixtures/stricter-actual.json
  [ "$status" -eq 0 ]
  [[ "${lines[-1]}" == "PASS: reconcile-dry-run" ]]
  [[ "$output" == *"raised_for_review"* ]]
  [[ "$output" != *"auto_repaired"* ]]
}
```

**Correct:** `@test "AT-033 no auto-loosening: ..."`
**Incorrect:** `@test "test reconciler"`, `@test "AT33 works"`, `@test "acceptance test 33"`

**Never invent an AT number.** If the behaviour you are testing has no AT id, name the test for the invariant it upholds, or for nothing at all — `tests/unit/` — but do not mint `AT-111`.

### 12.5 Golden files

`tests/golden/<case>.expected.json`, byte-compared, regenerated only by an explicit `make <scope>-golden-update` target that a human runs. A test never regenerates its own golden file.

---

## 13. Command, output and exit-code conventions

This section exists because `PARTITION.md` line 45 requires "a self-verify command whose output is unambiguous". These rules make that possible.

### 13.1 Exit codes — every check, validator, tool and script

| Code | Meaning | Agent must |
| --- | --- | --- |
| `0` | Pass | proceed |
| `1` | Fail — the checked property does not hold | fix, or STOP if the task's STOP rule names this |
| `2` | Usage error — bad arguments, missing file | fix the invocation |
| `3` | Cannot determine — a precondition is absent | **STOP** and open a blocker; never treat as pass |

Any other exit code is a defect in the tool.

### 13.2 Output — the last line is the verdict

The **final line of stdout** is exactly one of:

```
PASS: <check-id>
FAIL: <check-id>: <one-line reason>
STOP: <check-id>: <the absent precondition>
```

| Rule | Correct | Incorrect |
| --- | --- | --- |
| `<check-id>` equals the make target name (§14) | `PASS: schemas-registry-validate` | `PASS: ok`, `PASS` |
| Verdict line goes to **stdout**; diagnostics to **stderr** | — | interleaved |
| No colour, no ANSI escapes, no spinners, no progress bars | plain ASCII | `\033[32m` |
| Deterministic ordering — sort every list before printing | `sort` | filesystem order |
| No timestamps, hostnames, durations or run ids in the verdict line | `PASS: reconcile-dry-run` | `PASS in 1.4s on RUNNER-7` |
| Exactly one verdict line per invocation | — | a verdict per file checked |

Reference implementation fragment:

```bash
#!/usr/bin/env bash
set -euo pipefail
CHECK_ID="schemas-registry-validate"
fail() { echo "FAIL: ${CHECK_ID}: $1"; exit 1; }
stop() { echo "STOP: ${CHECK_ID}: $1"; exit 3; }

[ -d schemas/registry ] || stop "schemas/registry does not exist"
for f in $(find schemas/registry -name '*.schema.json' | sort); do
  python -c "import json,sys; json.load(open(sys.argv[1]))" "$f" \
    || fail "invalid JSON in $f"
done
echo "PASS: ${CHECK_ID}"
```

### 13.3 Running a self-verify command and reading the verdict

Because `set -e` aborts on a non-zero exit, capture explicitly:

```bash
set -euo pipefail
out="$(make schemas-registry-validate 2>&1)"; rc=$?
printf '%s\n' "$out" | tail -1
exit "$rc"
```

An acceptance criterion in a task file is written so there is nothing to interpret:

> Run `make schemas-registry-validate`. The last line of output is exactly `PASS: schemas-registry-validate` and the exit code is `0`.

**Incorrect acceptance criteria:** "tests should pass", "no errors", "validator works", "output looks right".

### 13.4 Script conventions

| Language | Rules |
| --- | --- |
| Shell | `#!/usr/bin/env bash`, then `set -euo pipefail` on line 2. POSIX-compatible paths (forward slashes) — the lanes run on Windows under Git Bash. Quote every expansion. No `cd` without `|| exit`. |
| Python | 3.11+, standard library plus `pyyaml` and the chosen validator only. `snake_case` functions, type hints on public functions, `if __name__ == "__main__":` entry point calling `main() -> int` that returns the §13.1 exit code. No `print` to stdout except the verdict line. |
| Both | No network access in a validator or a test. No writes outside the tool's own owned tree. No `rm -rf` on a path built from a variable. |

---

## 14. Makefile and target conventions

### 14.1 The no-shared-file rule applied to `make`

`Makefile` is L0-owned (`PARTITION.md` line 22) and no lane may edit it. So the root `Makefile` includes lane fragments by glob and is never touched again:

```make
# Makefile — control-plane. L0-owned. Lane targets arrive via */targets.mk.
-include $(shell git ls-files '*targets.mk')
```

Each lane ships **one** `targets.mk` per owned root, inside that root:

```
validators/registry/targets.mk     L1
reconciler/targets.mk              L3
tools/records/targets.mk           L4
```

### 14.2 Target naming

```
<scope>-<verb>
```

`<scope>` is the §5.3 scope token of the owning lane. This guarantees no two lanes can define the same target.

| Correct | Incorrect |
| --- | --- |
| `schemas-registry-validate` | `validate` (collides across lanes) |
| `reconciler-dry-run` | `run` |
| `records-write-check` | `check-records` (verb first) |
| `provision-create-product` | `create_product` (underscore) |

Every target is `.PHONY`, prints exactly one §13.2 verdict line, and takes no arguments.

```make
# validators/registry/targets.mk — L1
.PHONY: schemas-registry-validate
schemas-registry-validate:
	@bash validators/registry/validate.sh
```

**Note:** the eight standard commands `make setup | dev | test | uat-local | migrate | reset | health | parity` are the **product repository** contract (Spec §33.1). They are not control-plane targets and are never redefined here.

---

## 15. Git hygiene

### 15.1 Line endings — mandatory, because the lanes run on Windows

`.gitattributes` at the root of each repository (L0-owned, placed at F0):

```
* text=auto eol=lf
*.png binary
*.jpg binary
*.pdf binary
```

Every lane, once per clone:

```bash
git config core.autocrlf false
git config core.eol lf
```

**Correct:** every file in the repository has LF endings.
**Incorrect:** a CRLF file — it changes every line of the diff and makes a one-line change unreviewable.

Check before committing:

```bash
git diff --cached --stat | tail -1
file $(git diff --cached --name-only) | grep -i 'CRLF' && echo "FAIL: CRLF line endings" || echo "PASS: line-endings"
```

### 15.2 What never enters a commit

| Never commit | Instead |
| --- | --- |
| Secrets, tokens, API keys of any kind | environment-scoped secrets (Spec §101 #25, #84) |
| Customer data — in fixtures, records, incident evidence, anywhere | reference by identifier (Spec §101 #111) |
| Generated artifacts, build output, `__pycache__`, `.venv`, `node_modules` | `.gitignore` |
| Binary blobs above 1 MB | a published artifact, referenced by digest |
| A `.env` file | `.env.example` (Spec §33.1) |
| Another lane's path | nothing — STOP (§7.1) |

### 15.3 Rebase, squash, force

| Action | Rule |
| --- | --- |
| Rebase your own lane branch on `integration` before opening the PR | required (`PARTITION.md` line 34) |
| Merge commits **into** a lane branch | forbidden — rebase only |
| `git push --force-with-lease` on your own lane branch | permitted before review is requested |
| `git push --force` | forbidden, anywhere, always |
| Force-push after a review is submitted | forbidden — it discards the approval (Spec §101 #9) |
| Force-push or delete on `integration`, `main`, or any branch of `control-plane-records` | forbidden; blocked by ruleset (D107) |
| Rebasing or merging another lane's branch | forbidden (`PARTITION.md` line 36) |

### 15.4 Commit signing

Commits to `control-plane-records` are signed by the writing identity; an unsigned or foreign-signed commit there is Blocking drift (D107). For `control-plane` lane branches, the signing policy is closed (§19 Decision 4): **Option B** — signed commits are required on `main` and `integration` only; lane branches themselves need not sign, and the commit reaching a protected branch is signed by the merging identity. L5 configures branch-protection signing rules under `access/**` to this option.

---

## 16. Markdown conventions for programme documents

These apply to PR bodies, blocker issues, CCRs and any `docs/**` file L0 writes.

| Rule | Correct | Incorrect |
| --- | --- | --- |
| ATX headings, one `#` H1 per file, no skipped levels | `## Task` under `# 09 — …` | `Task\n----`, jumping H1 to H3 |
| Fenced code blocks always carry a language | ` ```bash ` | ` ``` ` bare |
| Every command block is copy-pasteable as-is, no `$` prompt prefix except in a transcript | `make schemas-registry-validate` | `$ make schemas-registry-validate` outside a transcript |
| Tables have a header row and an alignment row; no empty cells — write `none` | `\| none \|` | `\| \|` |
| No trailing whitespace; one blank line between blocks; single final newline | — | — |
| Links are inline `[text](path)`, relative within the repository | `[PARTITION](../PARTITION.md)` | absolute local paths, bare URLs |
| No emoji, no ASCII art, no decorative separators beyond `---` | — | `====`, `★`, `✅` |
| Spec citations follow §2.1 exactly | `Spec §97.2` | `see the spec` |

---

## 17. Labels

| Label | Applied to | Values |
| --- | --- | --- |
| `lane/<N>` | every PR and issue | `lane/0` … `lane/5` |
| `phase/<token>` | every PR and issue | `phase/f0` … `phase/f7`, `phase/g1` … `phase/g8`, `phase/p1` … `phase/p8` (lower case) |
| `blocker` | blocker issues only | — |
| `ccr` | contract change requests only | — |
| `agent-authored` | every lane PR | mirrors the `Agent-Authored: true` trailer (Spec §97.2) |
| `stop` | an issue where a STOP rule fired and work is halted | — |

No other labels. A label not on this list is not created by a lane.

---

## 18. Prohibited constructs — the fast checklist

Run down this list before opening any PR. Each line is a rule stated above; each is a PR rejection.

- [ ] No path outside your lane's ownership appears in `git diff --name-only origin/integration...HEAD`
- [ ] No shared index, list, manifest-of-everything or append-target file was created or edited
- [ ] No `contracts/**` file was edited
- [ ] No import, `$ref` or file read reaches into another lane's tree
- [ ] No `TODO`, `TBD`, `FIXME`, `XXX` string in any committed file
- [ ] No invented `AT-`, `SIG-`, `EC-`, `D` or invariant number — every one was grepped from the spec
- [ ] No invented convention: every name follows a rule in this file
- [ ] No emoji, no ANSI colour, no non-ASCII outside prose
- [ ] No secrets, no `.env`, no customer data, no real person's data beyond registry logins
- [ ] No CRLF line endings
- [ ] No `default` in a JSON Schema; no missing `additionalProperties: false`
- [ ] No `.yml` outside `.github/workflows/` and `templates/workflows/`
- [ ] No YAML anchor, alias or merge key
- [ ] No unpinned third-party GitHub Action (full commit SHA only — Spec §101 #85)
- [ ] Every commit carries the full eight-trailer block
- [ ] The self-verify command's last line is `PASS: <check-id>` and its exit code is `0`

---

## 19. L0 DECISION REQUIRED

Four conventions could not be fixed by this file alone because they depend on facts or design choices that belong to L0. **No lane ever picks one of these itself.** Decisions 1, 2 and 4 below have since been closed by L0 (see each decision's Status line) — a task needing one of those three values uses the resolution recorded there. Decision 3 remains open: a task that needs it STOPs until L0 records the decision in `contracts/**` at F0.

### L0 DECISION REQUIRED 1 — the JSON Schema `$id` host

**Status: Closed.** Resolved by FD-007-R (2026-09-02) and FD-050 (2026-09-06): **Option C**, not this file's recommendation of Option A. The `$id` namespace is a URN, `urn:multiproduct:schemas:<type>:<version>` — no host, domain or GitHub organisation is needed. §11.1, §11.2 and §11.4 use this form.

**What was undecided:** the `<SCHEMA_HOST>` token in `https://schemas.<SCHEMA_HOST>/<family>/<entity>/v<N>.schema.json` (§11.1, now superseded). The spec did not name the company, its domain or its GitHub organisation.

**Why it had to be decided at F0:** `$id` values are baked into every schema file and every cross-file `$ref` from `contracts/**`. Changing them later rewrites every schema in three lanes at once, which the partition exists to prevent.

**Options that were on the table**

| # | Value | Consequence |
| --- | --- | --- |
| A | The company's bare domain, e.g. `<company>.com` | Stable, readable, resolvable if ever published; requires L0 to name the domain. Note: `schemas.` is already the literal prefix in the `$id` template at §11.1 — the value recorded here is the bare domain only, not `schemas.<company>.com` |
| B | The GitHub organisation URL: `https://raw.githubusercontent.com/<org>/control-plane/main/schemas/...` | Resolvable today with no DNS work; couples `$id` to a branch name and to GitHub |
| C (chosen) | A URN: `urn:multiproduct:schemas:<type>:<version>` | No host needed, never resolvable; some tooling handles URNs poorly |

**Decision owner:** L0. **Applied to:** L1 (`schemas/registry/**`, `schemas/product/**`), L4 (`schemas/records/**`).

### L0 DECISION REQUIRED 2 — the JSON Schema validator implementation and dialect

**Status: Closed** — forced by prior decision, no separate L0 ruling needed. **Option A** applies, matching this file's recommendation below: Python `jsonschema` + `check-jsonschema` CLI, with `format` assertion explicitly enabled.

**What was undecided:** which validator the CI gate runs. Spec §99.2 subsystem B requires "multi-version schema validators" but names no implementation, and Spec §99.5 names no schema tooling.

**Why it had to be decided at F0:** the choice fixes the dialect that is actually supported, whether `format` asserts or only annotates, and the exact text of validation errors — which §13.2 verdict lines and every `rejects` test in §12 compare against.

**Options that were on the table**

| # | Implementation | Consequence |
| --- | --- | --- |
| A (chosen) | Python `jsonschema` + `check-jsonschema` CLI | Full 2020-12; `format` assertion opt-in; same language as the reconciler and provisioning tools; one toolchain to install |
| B | `ajv-cli` (Node) | Fast, excellent 2020-12 support; adds a Node toolchain to a Python-shaped build surface |
| C | `yajsv` (Go, draft-07 only) | Single static binary, no runtime; **forces the dialect down to draft-07**, losing `$defs`/`prefixItems` semantics assumed in §11 |

**Decision owner:** L0. **Applied to:** L1, L2 (the CI gate), L4. `format` assertion is enabled, which is why §11.2 rule 10 additionally requires a `pattern` on every date field.

### L0 DECISION REQUIRED 3 — the `make parity` environment-schema declaration format

**What is undecided:** the file format in which an environment's configuration schema is declared, so that local, staging and production can be compared.

**This is design-open in the specification itself:** Spec §99.3 item 2 — "The `make parity` declaration format — comparing local configuration schema against staging and production declarations presumes an environment-schema format to be defined once and reused." It is explicitly listed as something the implementer must invent, so **no lane invents it.**

**Why it must be decided before F4:** Spec §98.2 Phase 4's completion check requires `make parity` to report no divergence, and Spec §33.1 makes a parity violation on a production deployment path a blocking CI failure.

**Options**

| # | Format | Consequence |
| --- | --- | --- |
| A | A per-environment `env.<environment>.yaml` declaring variable names, types and required/optional — validated by a JSON Schema like every other control-plane artifact | Consistent with §10 and §11; one more schema family to own |
| B | Extend `.env.example` with typed comment annotations parsed by the parity job | No new file; parsing comments is brittle and unlike everything else here |
| C | Derive the schema from the running environment and diff the derived sets | No declaration to maintain; compares actual against actual, so it cannot detect a variable missing from *both* — which is the failure Spec §33.1 names |

**Recommendation:** A, owned by L5 under `infra/**` with the schema under L1's `schemas/product/**` via a CCR. **Decision owner:** L0. **Blocks:** L2 (the parity CI job), L5 (`infra/**`).

### L0 DECISION REQUIRED 4 — commit signing on `control-plane` lane branches

**Status: Closed** — forced by spec. **Option B** applies, matching this file's recommendation below: signed commits are required on `main` and `integration` only.

**What was undecided:** whether every lane commit to `control-plane` must be signed. The specification requires signing on the **records** repository only (D107: "commits are signed by the writing identity and an unsigned or foreign-signed commit is Blocking drift"), and is silent for `control-plane` lane branches.

**Why it had to be decided at F0:** it changes the setup step in every lane's first task and the branch-protection configuration L5 writes under `access/**`.

**Options that were on the table**

| # | Policy | Consequence |
| --- | --- | --- |
| A | Signed commits required on all branches of both repositories | Uniform, strongest; every AI developer needs a key provisioned before its first commit |
| B (chosen) | Signed commits required on `main` and `integration` only | Lane branches stay frictionless; the squash-merge commit is signed by the merging identity |
| C | Signed commits required on `control-plane-records` only, per D107 | Minimum the spec demands; leaves `control-plane` authorship unattested |

**Decision owner:** L0. **Applied to:** every lane's first task; L5 (`access/**`), which configures branch-protection signing rules per this decision.

---

## 20. Conformance — the convention gate

L0 wires these into the control-plane CI as one required status check named `conventions`. A lane runs them locally before opening any PR. Each prints one §13.2 verdict line.

```bash
set -euo pipefail
# 1. YAML style
yamllint -c .yamllint.yaml . && echo "PASS: conventions-yamllint" || echo "FAIL: conventions-yamllint"

# 2. No forbidden markers in tracked files
! git grep -nE '\b(TODO|TBD|FIXME|XXX)\b' -- . && echo "PASS: conventions-no-markers" || echo "FAIL: conventions-no-markers"

# 3. No .yml outside the two workflow directories
! git ls-files '*.yml' | grep -vE '^(\.github/workflows/|templates/workflows/)' \
  && echo "PASS: conventions-extensions" \
  || echo "FAIL: conventions-extensions"

# 4. No YAML anchors, aliases or merge keys
! git grep -nE '(^|\s)(&[A-Za-z_]|\*[A-Za-z_]|<<:)' -- '*.yaml' \
  && echo "PASS: conventions-no-anchors" \
  || echo "FAIL: conventions-no-anchors"

# 5. Branch name
git rev-parse --abbrev-ref HEAD \
  | grep -qE '^(lane/[1-5]/(f[0-7]|g[1-8]|p[1-8])-[0-9]{2}-[a-z0-9]+(-[a-z0-9]+){1,4}|l0/.+|integration|main)$' \
  && echo "PASS: conventions-branch-name" || echo "FAIL: conventions-branch-name"

# 6. Every commit on this branch carries the trailer block
for sha in $(git rev-list origin/integration..HEAD); do
  for t in Task-Id Lane Phase Spec AT Invariant Agent-Authored Self-Verify; do
    git log -1 --format=%B "$sha" | grep -qE "^${t}: " \
      || { echo "FAIL: conventions-trailers: $sha missing ${t}:"; exit 1; }
  done
done
echo "PASS: conventions-trailers"

# 7. Diff stays inside the lane's owned paths (edit the pattern to your lane, §6.3)
git diff --name-only origin/integration...HEAD \
  | grep -vE '^(schemas/registry/|schemas/product/|registries/|validators/registry/)' \
  && echo "FAIL: conventions-lane-paths" || echo "PASS: conventions-lane-paths"

# 8. Identifiers cited in changed Markdown exist in the spec (§2.1)
SPEC="C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md"
FAILURES=0
while read -r f; do
  while read -r id; do
    grep -q "$id" "$SPEC" || { echo "FAIL: conventions-citations: unknown $id in $f"; FAILURES=$((FAILURES + 1)); }
  done < <(grep -oE '\b(AT-[0-9]{3}|SIG-[0-9]{2}|EC-[0-9]{1,3})\b' "$f" | sort -u)
done < <(git diff --name-only origin/integration...HEAD -- '*.md')
if [ $FAILURES -eq 0 ]; then echo "PASS: conventions-citations"; else echo "FAIL: $FAILURES citations broken"; exit 1; fi
```

A PR that fails any of the eight is not reviewed; it is returned. There is no discretion here and none is wanted: five agents writing to one set of conventions is the only reason the merge train can run.
