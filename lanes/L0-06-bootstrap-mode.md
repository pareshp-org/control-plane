# L0-06 — BOOTSTRAP MODE OPERATION

**Lane:** L0 Integrator · **Branches:** `main`, `integration` (PARTITION.md §"Branch & merge model")
**Executor:** the human lead, acting as the Founder. Every command below is run by a person, not by an AI developer.
**Owns exclusively:** `contracts/**`, `CODEOWNERS`, `docs/**`, root files, `Makefile` (PARTITION.md §"The five build lanes")
**Spec:** `C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md` (v4.0)
**Frozen partition:** `C:/D_Drive/PS/MultiProduct/Code/implementation/PARTITION.md` — nothing here contradicts it.
**Upstream in this lane:** `L0-00-charter.md` §5.4 reserves **L0D-19** — *"Opening and closing every bootstrap exception,
with expiry, owner and deactivation trigger"*. `L0-03-merge-train.md` §5 routes *"the bootstrap exception when no second
human can approve"* to L0D-19. This file is L0D-19 turned into an operational procedure with literal commands.

> **Reading rule for lanes L1–L5.** Only §3 and §9 bind you. §3 is the list of things that stay binding **even in
> bootstrap** — a lane that writes code relaxing any of them has hit a STOP condition regardless of what mode the
> programme is in. §9 says which artifacts here are yours and which are not. Everything else is work the human lead
> performs. **No lane opens, edits, renews or closes a bootstrap exception**; a lane that believes it needs one files a
> blocker naming L0D-19 (`docs/escalation/BLOCKER.md`, `L0-00-charter.md` §7.1).

---

## 1. Shell and repository conventions

POSIX `sh` / Git Bash, run from the control-plane repository root. Identical to `L0-00-charter.md` §1, with the one
extra alias `master/08-progress-tracking.md` §2.1 uses for the programme ledger generators.

**Commands**

```bash
export CP_ROOT="$HOME/src/control-plane"
export CPR_ROOT="$HOME/src/control-plane-records"
export CP="$CP_ROOT"          # the name docs/plan/bin/*.sh read (master/08 §2.1)
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org
cd "$CP_ROOT"
git rev-parse --show-toplevel
gh auth status
for t in git gh jq; do command -v "$t" >/dev/null || echo "MISSING $t"; done; echo TOOLING-CHECKED
```

| Symbol | Meaning | Set by |
|---|---|---|
| `$CP_ROOT` / `$CP` | local clone of `control-plane` | you, once per shell |
| `$CPR_ROOT` | local clone of `control-plane-records` | you, once per shell |
| `$BOOT_TODAY` | ISO date the checker compares expiries against; unset means `date -u +%F` | only in tests |
| `T2W`, `T3H`, `TQA`, `T4P` | the four §95.4 headcount thresholds, in the order the table states them | fixed, §95.4 |
| `FCC` | the founder-capability-concentration threshold of §95.2 (spec L8681) — not a §95.4 row | fixed |

**No task in this file writes to `control-plane-records`** until L0-06-08's cutover step, and that step is a human
record write on the normal path of §97.1 (spec L8843) — a direct push to a repository that carries no review
protection and a no-bypass ruleset (PARTITION.md §"Repositories"; D107, spec L10205). It is not a lane deliverable
and it never rides the merge train.

---

## 2. The scoping rule — per repository, never per company

§95.1 (spec L8642) is explicit and this file never softens it:

> *"Bootstrap Mode makes the shortfall explicit instead of silent — and it is scoped **per repository**, never per
> company. … Product repositories whose existing teams hold Write satisfy gate independence immediately, run fully
> armed from day one, and never enter bootstrap."*

§95.2 (spec L8678) states the same rule as a prohibition: *"A bootstrap exception never covers a repository whose
existing team already satisfies the gate — the product repositories arrive with their teams and are armed
immediately."* D57 (spec L10125) records the decision.

| Repository | Mode | Basis |
|---|---|---|
| `control-plane` | **bootstrap** | §95.1 L8642 — no second context-holding human holds Write during the solo build |
| `product-template` | **bootstrap** | §95.1 L8642 — an operating-system tooling repository ("os-tooling" in the §95.2 exhibit, spec L8654); same shortfall, same solo builder |
| `control-plane-records` | **no-review-gates** | D107 L10205 + PARTITION.md §"Repositories" — this repository carries **no review protection by design**; its no-bypass ruleset blocking force-push and delete is armed from day one. No review gate is relaxed here, so **no bootstrap exception covers it**. An exception naming it would carry a deactivation trigger that can never fire, because arming review on it is not the intended end state |
| every product repository | **armed** | §95.1 L8642, §95.2 L8678 — the team already holds Write; gate independence is satisfied on day one; the repository never enters bootstrap |

**The default is `armed`.** A repository absent from `docs/bootstrap/repo-scope.tsv` is armed and may never appear in
a bootstrap exception. `docs/plan/bin/bootstrap-check.sh` enforces that mechanically (rule **B6**). This is also why
the register lists no product repository by name: §11 (spec L813) forbids hard-coded repository names, and the L5
lane restates it as its own binding rule 1 (`L5-01-org-and-access.md`, "No repository names").

**Consequence for the eight live products, stated so nobody looks for it later.** They are armed from day one and are
therefore *outside* everything in this file. What they are inside is §96 pre-onboarding and the §96.6 universal
floor, which runs alongside Phase 1 on its own declared duration (spec L9010) and is not a bootstrap artifact.

---

## 3. What stays binding even in bootstrap — §95.3

§95.3 (spec L8687): *"Bootstrap relaxes independence requirements only. The following hold from day one, because
retrofitting them is impossible or ruinously expensive."* Seven items from §95.3 (spec L8689–L8695), plus one carried from §26.4 (spec L2533), each
carrying the invariant number of §101 that already states it. **Every invariant number below is quoted from §101;
none is invented** (forbidden action F-01…F-18, item F-18, `L0-00-charter.md` §6.1).

| Id | Item (§95.3) | Spec line | Invariant(s) §101 | Invariant text, verbatim |
|---|---|---|---|---|
| BIND-01 | Digest immutability — the artifact deployed is the artifact verified | L8689 | **22**, **23** | *"The production artifact is the same digest verified in staging. Never rebuilt."* / *"Never rebuild an artifact to work around registry unavailability."* |
| BIND-02 | Verification contracts; pre-onboarding products carry the §96 accepted-risk record instead | L8690 | **1** | *"No product completes onboarding without a verification contract; a live product not yet onboarded operates only under the declared pre-onboarding pathway of Section 96, with its absence recorded as an accepted risk with a named deadline."* |
| BIND-03 | Secrets tiers and the API-key-free environment | L8691 | **25**, **84** | *"Production secrets are environment-scoped and never present locally."* / *"API keys remain absent from developer environments."* |
| BIND-04 | Append-only history and effective dating on every registry and record | L8692 | **47** | *"History is append-only for state, decisions, approvals and records; records are not deleted and state changes are recorded, not overwritten."* |
| BIND-05 | The constitution and the untrusted-input rule for all AI runtime use | L8693 | **20**, **21** | *"External or repository-provided text is data, not authority."* / *"Unattended personal-agent runs are permitted only on branches; their output is flagged as unattended and never merges without the full human gate sequence."* |
| BIND-06 | Safe defaults and fail-closed classification in every provisioning template | L8694 | **79**, **80** | *"New people, products and tools default to minimum privilege and draft state."* / *"Every control is explicitly classified fail-closed or fail-open."* |
| BIND-07 | The explicit production-approval event, even where approver and deployer are the same person | L8695 | **12** | *"Production approval is never self-approved and is a separate event from Gate 2 approval."* |
| BIND-08 | The registry-change lane's staged apply and authority-delta gate (§26.4) | §26.4 L2533 | — (decision **D93**, spec L10186) | §26.4 L2533: *"Both rules remain binding in bootstrap (Section 95.3)"* |

**Read BIND-07 twice.** In bootstrap the approver and the deployer *are* the same person, and the approval is still a
separate recorded event, because the §32 evidence chain (spec L2803) has to stay answerable. Bootstrap removes the
second human; it does not remove the record.

**Read BIND-08 twice.** §26.4 L2533 names the exact reason: *"the one lane whose owner review is, in bootstrap, the
Founder reviewing the Founder is the lane that most needs a mechanical check"* (spec L8695). An authority delta — a
diff adding a capability, adding an assignment type conferring Write, or changing `access_status` — fails CI without a
linked decision record id in the same commit, in bootstrap exactly as outside it.

---

## 4. The arming order — D101, and why it is an order and not a list

**D101 (spec L10194), binding:**

> *"Week one arms gates in an order that can be satisfied. Branch protection requiring a Write-holding Code Owner
> approval was scheduled before any Team granted Write, and required status checks before any workflow emitted them.
> Teams are derived and granted first, from an interim assignment set that Phase 3 replaces, and the bootstrap arming
> pattern of §95.2 — configured but not yet binding, with the armed configuration recorded beside it — is reused
> rather than a second approach invented."*

§98.2 Phase 1 (spec L9017) states the same correction in the deliverable itself: *"Organisation base permission Read;
Teams grant Write per the permission model — **within Week 1 and before branch protection is armed** … Arming a
Code-Owner-and-approval gate while no Team grants Write leaves nobody whose approval counts, and Section 95.4 names
the result exactly: a team that experiences its merges mysteriously breaking."*

**The order, numbered. Step N may not start until step N−1 is recorded.**

| # | Step | Spec line | Recorded where |
|---|---|---|---|
| 1 | Organisation base permission set to **Read** | §98.2 L9017 | L5 `access/org/`, L5-01-03 |
| 2 | **Teams created and granting Write**, from the interim assignment set Phase 3 replaces | §98.2 L9017; D101 L10194 | L5 `access/teams/`, L5-01-05 |
| 3 | Branch protection applied in the **unarmed** profile | §95.2 L8680 | L5 `access/branch-protection/`, L5-01-07 |
| 4 | Required-status-check list **starts empty, per repository** | §98.2 L9018 | L5-01-07; a lane adding one is forbidden action **F-07** |
| 5 | Checks added only as each comes into existence, named by the phase that adds them | §98.2 L9018 | each phase's completion check |
| 6 | The Code-Owner-and-approval gate **armed** at threshold `T2W` | §95.4 L8703 | this file, L0-06-09 |
| 7 | The workflow-identity gate **armed on production deploys** at threshold `T3H` | §95.2 L8680; §27.2 L2571; §95.4 L8704 | this file, L0-06-10 |

Steps 1–5 are L5's declared state and L5's apply runbooks (`L5-01-org-and-access.md` T03, T05, T07, T10, T12).
**L0 never edits `access/**`.** Steps 6 and 7 are L0's arming decisions, and they are decisions only about *when* —
the *what* was recorded beside the unarmed value in step 3, which is the whole point of §95.2 L8680:

> *"The gates are **configured but not yet binding** on covered repositories. The unarmed configuration is defined
> exactly: require-PR and direct-push blocking stay on; required approving reviews is set to 0; the workflow-identity
> gate is not yet enforcing. The armed configuration — required approving reviews at the specified count, the
> workflow-identity gate active on production deploys — is recorded beside the unarmed one, so arming a gate is a
> configuration flip, not a build project."*

`docs/bootstrap/arming-matrix.tsv` (task L0-06-05) is L0's governance record of that pair. The machine-readable
payloads that GitHub actually receives are L5's, and where the two ever disagree **the matrix is not corrected by L0
unilaterally** — see T05's STOP rule.

---

## 5. DECISION REQUIRED — items this file cannot close by itself

Written in the house form of `L1-00-charter.md` §12. **No executor resolves any of them.** Each names what this file
does in the meantime, so no task in §7 is blocked on an answer.

---

> ### DECISION REQUIRED #1 — the write path from an L0-authored bootstrap exception into `registries/exceptions.yaml`
>
> **Facts.** §95.2 (spec L8649) and §54.5 (spec L8828) place bootstrap exceptions in `exceptions.yaml`, the unified
> exception registry. PARTITION.md line 17 assigns `registries/**` to **L1, exclusively**. `L1-05-tasks.md` task
> **L1-108** creates `registries/exceptions.yaml` containing `exceptions: []` with the comment *"entries are authored
> by their owner, not by Lane 1"*. The owner of a bootstrap exception is the Founder (§54.3 L4814: `bootstrap` →
> `exceptional-approval`), which in this programme is L0. So the authoring party and the path owner are different
> lanes, and PARTITION.md rule 3 forbids two writers on one file.
> **Question for L0.** Which of these is it: (a) L1 lands the rendered block in one L1 task, taking
> `docs/bootstrap/exceptions/` as its input, or (b) L0 is granted `registries/exceptions.yaml` by an L0D-04 extension
> of `lane-paths.tsv`, or (c) the exception entries move to a directory-per-item store that L1 assembles?
> **Blocks.** Nothing in this file. It changes only where the rendered YAML finally lands.
> **This file's behaviour pending the answer.** `docs/bootstrap/exceptions/EXC-BOOT-NNN.yaml` — one file per
> exception, inside L0's exclusively-owned `docs/**`, directory-per-item per PARTITION.md rule 3 — is the authored
> source and the thing L0's checker validates. **L0 does not edit `registries/**`,** and the weekly bootstrap log
> carries the un-landed state as an open item until the answer lands.

---

> ### DECISION REQUIRED #2 — Gate 1's compensating control is itself relaxed during bootstrap
>
> **Facts.** §26.1 (spec L2497) states Gate 1's bootstrap handling verbatim: *"Where neither exists — the bootstrap
> case — the self-approval runs under a recorded bootstrap exception (Section 95), with Gate 2 independent review as
> the compensating control."* But Gate 2 independent review is itself relaxed in bootstrap, under the §95.2 exhibit's
> own `EXC-BOOT-001` (spec L8652, `scope: gate-2-independent-review`). During the solo build both exceptions are open
> at once, so Gate 1's named compensating control is not in force.
> **Question for L0.** What compensating control does `EXC-BOOT-012` (`gate-1-plan-approval`) carry while
> `EXC-BOOT-001` is open? A bootstrap exception without a real compensating control is a silent policy breach —
> §54.2 (spec L4793): *"the compensating control is the entire reason an exception is acceptable"*.
> **Blocks.** Nothing. `EXC-BOOT-012` renders and validates; only its `compensating_control` line is provisional.
> **This file's behaviour pending the answer.** `EXC-BOOT-012` carries the common compensating-control set plus the
> literal sentence naming this gap, so the record states the fact rather than implying a control that is not running.
> The gap is a standing line in the weekly bootstrap log until L0 answers.

---

> ### DECISION REQUIRED #3 — the calibrated values this file consumes
>
> **Facts.** Three numbers here are calibrated configuration and therefore **L0D-17** (`L0-00-charter.md` §5.1), not
> an executor's choice: the bootstrap-log staleness window (§95.4 L8708 states the initial value, 7 days, *"changed
> only by a recorded decision"*); the bootstrap exception lifetime; and the review-date offset. §95.2's exhibit (spec
> L8666–L8668) exhibits `start: 2026-09-01`, `expiry: 2026-12-01`, `review_date: 2026-11-01` — 91 days and 30 days.
> **Question for L0.** Confirm 7 / 91 / 30 as the initial values, or record different ones.
> **Blocks.** Nothing. Task L0-06-03 transcribes the exhibit's own intervals and records the transcription as a
> decision file; §54.2 (spec L4797) independently requires a bounded expiry whatever the number turns out to be —
> *"An unknowable end date is bounded, not omitted."*

---

## 6. Where every artifact in this file lives — and the three that are not L0's

| Artifact | Path | Owner | Authority |
|---|---|---|---|
| Bootstrap-mode operating note | `docs/bootstrap/README.md` | **L0** | PARTITION.md line 22, `docs/**` |
| Repository scope register | `docs/bootstrap/repo-scope.tsv` | **L0** | §95.1 L8642 |
| Binding-in-bootstrap register | `docs/bootstrap/binding.tsv` | **L0** | §95.3 L8687 |
| Gate register (the exception source of truth) | `docs/bootstrap/gate-register.tsv` | **L0** | §95.2 L8646, L0D-19 |
| Activation checklist | `docs/bootstrap/activation-checklist.tsv` | **L0** | §95.4 L8701 |
| Arming matrix (unarmed beside armed) | `docs/bootstrap/arming-matrix.tsv` | **L0** | §95.2 L8680, D101 |
| Rendered exceptions, one file each | `docs/bootstrap/exceptions/EXC-BOOT-NNN.yaml` | **L0** | PARTITION.md rule 3 |
| Threshold evidence | `docs/bootstrap/activation/<threshold>-<date>.md` | **L0** | §95.4 L8699 |
| Renderer / checker / log generator / freshness | `docs/plan/bin/bootstrap-*.sh` | **L0** | master/08 §2.1 |
| Weekly bootstrap log entry | `docs/plan/bootstrap-log/<YYYY-MM-DD>.md`, then `records/bootstrap-log/` | **L0** writes; **L4** owns the store after cutover | §95.4 L8708; master/08 §7.4 |
| Closure / renewal / re-affirmation decisions | `docs/plan/decisions/<date>-<slug>.md`, then `records/decisions/` | **L0** | §97.2; master/08 §8.3 |

**Not L0's, and never written here:**

| Artifact | Owner | This file's relationship to it |
|---|---|---|
| `registries/exceptions.yaml` and the minimal week-one validator (expiry, owner, deactivation trigger) | **L1** — `L1-05-tasks.md` **L1-108**; rule `r_exc_min` in `validators/registry/rules/` | L0-06-06 executes the Phase 1 negative test against it. L0 never edits it (DECISION REQUIRED #1) |
| `access/branch-protection/` unarmed and armed profiles; `access/arming/` and the arming-order gate; the negative-test register; the per-repository transition note | **L5** — `L5-01-org-and-access.md` T07, T10, T13, T14 | L0-06-05 records the governance pair and cites them. L0 never edits `access/**` |
| `records/bootstrap-log/` store, and the pre-fill generator that supersedes `docs/plan/bin/bootstrap-log-gen.sh` at cutover | **L4** — `control-plane-records` is L4's entirely (PARTITION.md line 20); `master/06-v1-scope.md` R-6 | L0-06-08 cuts over and stops using the interim generator |
| The **SIG-39** detector and the bootstrap-log staleness drift rule | **L3** `validators/drift/**` (detector) and **L1** `validators/registry/**` (the CI staleness rule, `master/06` R-6) | L0-06-12 runs the manual sweep until the detector exists, then verifies the detector instead |

---

## 7. Tasks in this file

| Task id | Title | Size | Depends on |
|---|---|---|---|
| L0-06-01 | The bootstrap tree and the per-repository scope register | S | L0-00-02 |
| L0-06-02 | The binding-in-bootstrap register (§95.3) | S | L0-06-01 |
| L0-06-03 | The gate register — one row per relaxed gate, with expiry and deactivation trigger | M | L0-06-01 |
| L0-06-04 | The renderer and the fail-closed checker | L | L0-06-03 |
| L0-06-05 | The arming matrix — unarmed beside armed, in D101 order | M | L0-06-01 |
| L0-06-06 | Execute the Phase 1 negative test of the minimal `exceptions.yaml` validator | M | L0-06-04, L1-108 |
| L0-06-07 | The weekly bootstrap log — template, generator, freshness check | M | L0-06-04, L0-06-05 |
| L0-06-08 | Write the first entry; prove the staleness detector; cut over to the records repository | M | L0-06-07 |
| L0-06-09 | Threshold `T2W` — execute the activation checklist for real, negative tests included | L | L0-06-05, L0-06-07 |
| L0-06-10 | Thresholds `T3H`, `TQA`, `T4P` — the same procedure, three more times | L | L0-06-09 |
| L0-06-11 | Close a bootstrap exception as `trigger_satisfied`, by recorded decision | M | L0-06-09 |
| L0-06-12 | Renewal, the third-renewal re-affirmation branch, and the SIG-39 unclosed sweep | M | L0-06-03, L0-06-07 |

Dependency graph:

```
L0-00-02 ── L0-06-01 ─┬── L0-06-02
                        ├── L0-06-03 ── L0-06-04 ─┬── L0-06-06 ◄── L1-108 (cross-lane)
                        │                           └── L0-06-07 ─┬── L0-06-08
                        └── L0-06-05 ──────────────────────────────┤
                                                                    ├── L0-06-09 ─┬── L0-06-10
                                                                    │              └── L0-06-11
                                                                    └── L0-06-12
```

---

### L0-06-01 — The bootstrap tree and the per-repository scope register

**Size:** S · **Dependencies:** L0-00-02

The register exists so that "which repositories are in bootstrap" is a file rather than a memory. It is TSV, not
YAML, for the same reason `lane-paths.tsv` is (`L0-02-lane-guard.md` §5): the checker that reads it needs no parser
and no dependency, so it cannot fail for a reason unrelated to what it is checking.

**Commands**

```bash
cd "$CP_ROOT"
git checkout integration
git pull --ff-only
mkdir -p docs/bootstrap/exceptions docs/bootstrap/activation docs/plan/bin docs/plan/bootstrap-log docs/plan/decisions

printf '%s\n' \
'# repo-scope.tsv — L0-owned (L0D-19). Machine-readable form of MasterSpec v4.0 Section 95.1.' \
'# Format: <repository><TAB><mode><TAB><basis>.  Modes: bootstrap | armed | no-review-gates.' \
'# THE DEFAULT IS armed. A repository absent from this file is armed and may never appear in a' \
'# bootstrap exception (Section 95.2, spec L8678). Product repositories are never listed by name:' \
'# Section 11 forbids hard-coded repository names.' > docs/bootstrap/repo-scope.tsv
printf 'control-plane\tbootstrap\tSection 95.1 L8642 - no second context-holding human holds Write during the solo build\n' >> docs/bootstrap/repo-scope.tsv
printf 'product-template\tbootstrap\tSection 95.1 L8642 - operating-system tooling repository (os-tooling in the Section 95.2 exhibit, spec L8654)\n' >> docs/bootstrap/repo-scope.tsv
printf 'control-plane-records\tno-review-gates\tD107 L10205 - no review protection by design; no-bypass ruleset armed day one; no review gate is relaxed so no exception covers it\n' >> docs/bootstrap/repo-scope.tsv

cat > docs/bootstrap/README.md <<'BOOT'
# Bootstrap Mode — how this programme operates while one person holds the context

Authority: MasterSpec v4.0 Section 95 (spec L8636-L8712); decisions D57 (L10125) and D101 (L10194);
invariant 77 (L9554); signal SIG-39 (L4568); acceptance test AT-039 (L9361).
Owner: L0, under reserved decision L0D-19 (docs/charter/L0-00-charter.md Section 5.4).

## The one sentence that governs the scope

Bootstrap Mode is scoped PER REPOSITORY, never per company (Section 95.1, spec L8642). Product
repositories whose existing teams hold Write satisfy gate independence immediately, run fully armed
from day one, and never enter bootstrap. See docs/bootstrap/repo-scope.tsv.

## What bootstrap does NOT relax

Independence requirements only (Section 95.3, spec L8687). See docs/bootstrap/binding.tsv — eight
items that hold from day one, each carrying the Section 101 invariant number that states it.

## The files

| File | What it is |
|---|---|
| repo-scope.tsv          | which repositories are in bootstrap, and why |
| binding.tsv             | Section 95.3 — what stays binding even in bootstrap |
| gate-register.tsv       | one row per relaxed gate: expiry, owner, deactivation trigger |
| activation-checklist.tsv| Section 95.4 — the headcount thresholds and their verifications |
| arming-matrix.tsv       | the unarmed configuration recorded beside the armed one (Section 95.2 L8680) |
| exceptions/             | the rendered exception records, one file per exception |
| activation/             | evidence from each threshold's checklist run, negative tests included |

## The commands

    make bootstrap-render     # regenerate exceptions/ from gate-register.tsv
    make bootstrap-check      # fail-closed validation; last line BOOTSTRAP-CHECK OK
    make bootstrap-log        # write this week's log entry, two fields generated
    make bootstrap-fresh      # staleness detector; Blocking past the calibrated window

## The rule nobody may relax

A bootstrap exception is opened, renewed and closed by L0 alone (L0D-19). No lane opens one. A lane
that believes it needs one files a blocker (docs/escalation/BLOCKER.md) naming L0D-19.
BOOT

git add docs/bootstrap docs/plan
git commit -m "L0-06-01: bootstrap tree and per-repository scope register (L0D-19)"
git push origin integration
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | All seven directories exist | `for d in docs/bootstrap docs/bootstrap/exceptions docs/bootstrap/activation docs/plan/bin docs/plan/bootstrap-log docs/plan/decisions; do test -d "$d" \|\| echo "MISSING $d"; done; echo DONE` | `DONE` alone |
| 2 | The register has exactly three data rows | `grep -vc '^#' docs/bootstrap/repo-scope.tsv` | `3` |
| 3 | Every row is exactly three tab-separated fields | `awk -F'\t' '!/^#/ && NF!=3' docs/bootstrap/repo-scope.tsv \| wc -l` | `0` |
| 4 | Exactly two repositories are in bootstrap mode | `awk -F'\t' '!/^#/ && $2=="bootstrap"{n++} END{print n+0}' docs/bootstrap/repo-scope.tsv` | `2` |
| 5 | No product repository is named | `awk -F'\t' '!/^#/{print $1}' docs/bootstrap/repo-scope.tsv \| grep -c '^control-plane$\|^control-plane-records$\|^product-template$'` | `3` |
| 6 | The records repository is not in bootstrap | `awk -F'\t' '$1=="control-plane-records"{print $2}' docs/bootstrap/repo-scope.tsv` | `no-review-gates` |
| 7 | The operating note names the per-repository rule | `grep -c 'PER REPOSITORY, never per company' docs/bootstrap/README.md` | `1` |

**SELF-VERIFY**

```bash
cd "$CP_ROOT"
printf 'dirs=%s rows=%s malformed=%s bootstrap=%s records_mode=%s note=%s\n' \
  "$(for d in docs/bootstrap docs/bootstrap/exceptions docs/bootstrap/activation docs/plan/bin docs/plan/bootstrap-log docs/plan/decisions; do test -d "$d" && echo x; done | wc -l | tr -d ' ')" \
  "$(grep -vc '^#' docs/bootstrap/repo-scope.tsv)" \
  "$(awk -F'\t' '!/^#/ && NF!=3' docs/bootstrap/repo-scope.tsv | wc -l | tr -d ' ')" \
  "$(awk -F'\t' '!/^#/ && $2=="bootstrap"{n++} END{print n+0}' docs/bootstrap/repo-scope.tsv)" \
  "$(awk -F'\t' '$1=="control-plane-records"{print $2}' docs/bootstrap/repo-scope.tsv)" \
  "$(grep -c 'PER REPOSITORY, never per company' docs/bootstrap/README.md)"
```

Expected output, exactly:

```
dirs=6 rows=3 malformed=0 bootstrap=2 records_mode=no-review-gates note=1
```

**STOP rule** — if `bootstrap` is anything other than `2`, stop. Adding a repository to bootstrap mode is a claim that
it has no second context-holding human holding Write, and that claim is L0D-19, not an executor's reading of a team
roster. If a fourth operating-system tooling repository exists and you believe it belongs here, open
`BLOCKER L0-06-01: repository <name> claims bootstrap scope` and do not add the row. Adding a **product**
repository is forbidden outright: §95.2 L8678 says a bootstrap exception never covers a repository whose existing
team already satisfies the gate, and a row here is the first half of doing exactly that.

---

### L0-06-02 — The binding-in-bootstrap register (§95.3)

**Size:** S · **Dependencies:** L0-06-01

The eight items of §3 above, as data. The register exists so that "is this relaxed in bootstrap?" is answered by
`grep`, not by argument, at the moment somebody is under pressure to relax it.

**Commands**

```bash
cd "$CP_ROOT"
printf '%s\n' \
'# binding.tsv — L0-owned. MasterSpec v4.0 Section 95.3 (spec L8687-L8695), transcribed.' \
'# Format: <id><TAB><item><TAB><spec_line><TAB><invariants><TAB><proof>' \
'# Bootstrap relaxes INDEPENDENCE REQUIREMENTS ONLY. Every row below holds from day one.' \
'# Invariant numbers are quoted from Section 101. Inventing one is forbidden action F-18.' > docs/bootstrap/binding.tsv
printf 'BIND-01\tDigest immutability - the artifact deployed is the artifact verified\tL8689\t22,23\tL2 tools/evidence: production deploy rejected when digest differs from the staging-verified digest\n' >> docs/bootstrap/binding.tsv
printf 'BIND-02\tVerification contracts; pre-onboarding products carry the Section 96 accepted-risk record instead\tL8690\t1\tL1 product contract validation; Section 98.2 Phase 5 completion check\n' >> docs/bootstrap/binding.tsv
printf 'BIND-03\tSecrets tiers and the API-key-free environment\tL8691\t25,84\tenv | grep -i api_key returns empty on every machine (Section 98.2 Phase 1)\n' >> docs/bootstrap/binding.tsv
printf 'BIND-04\tAppend-only history and effective dating on every registry and record\tL8692\t47\tD107 no-bypass ruleset on control-plane-records; L4 record write paths\n' >> docs/bootstrap/binding.tsv
printf 'BIND-05\tThe constitution and the untrusted-input rule for all AI runtime use\tL8693\t20,21\tconstitution file authored at Section 98.2 Phase 3; unattended runs branch-only\n' >> docs/bootstrap/binding.tsv
printf 'BIND-06\tSafe defaults and fail-closed classification in every provisioning template\tL8694\t79,80\tL3 tools/provision templates; fail-closed classification L0D-18\n' >> docs/bootstrap/binding.tsv
printf 'BIND-07\tThe explicit production-approval event even where approver and deployer are one person\tL8695\t12\tL4 records: a production-approval record exists per deploy; Section 32 evidence chain answerable\n' >> docs/bootstrap/binding.tsv
printf 'BIND-08\tThe registry-change lane staged apply and the authority-delta gate\tL8695\t-\tSection 26.4 L2533 and D93 L10186: authority delta fails CI without a linked decision record id in the same commit\n' >> docs/bootstrap/binding.tsv

git add docs/bootstrap/binding.tsv
git commit -m "L0-06-02: what stays binding even in bootstrap (Section 95.3)"
git push origin integration
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Eight rows, one per §95.3 item | `grep -vc '^#' docs/bootstrap/binding.tsv` | `8` |
| 2 | Every row is exactly five tab-separated fields | `awk -F'\t' '!/^#/ && NF!=5' docs/bootstrap/binding.tsv \| wc -l` | `0` |
| 3 | Ids are contiguous `BIND-01`…`BIND-08` | `awk -F'\t' '!/^#/{print $1}' docs/bootstrap/binding.tsv \| tr '\n' ' '` | `BIND-01 BIND-02 BIND-03 BIND-04 BIND-05 BIND-06 BIND-07 BIND-08 ` |
| 4 | Every cited invariant number is within the closed catalogue of 111 | `awk -F'\t' '!/^#/{print $4}' docs/bootstrap/binding.tsv \| tr ',' '\n' \| grep -v '^-$' \| awk '$1<1 \|\| $1>111' \| wc -l` | `0` |
| 5 | Every row names a proof | `awk -F'\t' '!/^#/ && ($5=="" \|\| $5=="-")' docs/bootstrap/binding.tsv \| wc -l` | `0` |
| 6 | The API-key row is present and executable today | `env \| grep -i api_key \| wc -l` | `0` |

**SELF-VERIFY**

```bash
cd "$CP_ROOT"
printf 'rows=%s malformed=%s ids=[%s] bad_invariants=%s no_proof=%s apikeys=%s\n' \
  "$(grep -vc '^#' docs/bootstrap/binding.tsv)" \
  "$(awk -F'\t' '!/^#/ && NF!=5' docs/bootstrap/binding.tsv | wc -l | tr -d ' ')" \
  "$(awk -F'\t' '!/^#/{print $1}' docs/bootstrap/binding.tsv | tr '\n' ' ' | sed 's/ $//')" \
  "$(awk -F'\t' '!/^#/{print $4}' docs/bootstrap/binding.tsv | tr ',' '\n' | grep -v '^-$' | awk '$1<1 || $1>111' | wc -l | tr -d ' ')" \
  "$(awk -F'\t' '!/^#/ && ($5=="" || $5=="-")' docs/bootstrap/binding.tsv | wc -l | tr -d ' ')" \
  "$(env | grep -ci api_key)"
```

Expected output, exactly:

```
rows=8 malformed=0 ids=[BIND-01 BIND-02 BIND-03 BIND-04 BIND-05 BIND-06 BIND-07 BIND-08] bad_invariants=0 no_proof=0 apikeys=0
```

**STOP rule** — if `apikeys` is anything other than `0`, **stop the entire bootstrap programme, not just this task.**
BIND-03 is invariant 84 and is a §98.2 Phase 1 completion check (spec L9013, L9024); §95.3 L8691 puts it in the
day-one set precisely because it is not retrofittable. Remove the key, rotate it, and re-run before any other task.
If `bad_invariants` is non-zero you have written an invariant number outside 1–111, which is forbidden action **F-18**
(*"Inventing a spec section number, AT id, invariant number, SIG id or D id"*) — the catalogue is closed at 111
(§101, spec L9445). Re-read §101 and correct the row; do not "adjust" the range check.

---

### L0-06-03 — The gate register: one row per relaxed gate, with expiry and deactivation trigger

**Size:** M · **Dependencies:** L0-06-01

§95.2 (spec L8646): *"One exception per relaxed gate, in the standard exception schema, naming the repositories it
covers."* The relaxed gates are not chosen here — they are read off two places in the spec and nowhere else:

* the **Gates armed** column of the §95.4 checklist table (spec L8703–L8706), split on `;` — eleven gates;
* the two §95.2 bullets that name a gate the checklist table does not: Gate 1 plan approval under §26.1 (spec L2497)
  and the Founder's operational-capability holding (spec L8681) — two more.

Thirteen rows. `EXC-BOOT-001` keeps the id, scope, `policy`, `reason`, `risk_accepted` and `deactivation_trigger`
values of the §95.2 exhibit verbatim (spec L8650–L8671) so that the register's first row is the specification's own.

**`risk_accepted` is the gate's own guarantee, negated.** No new judgment is exercised anywhere in the table below:
the risk of relaxing "no self-approval" is that an author's own approval satisfies the gate, and so on. Where the
spec supplies the sentence it is used verbatim.

**Dates.** `start` is today; `expiry` is `start + 91 days`; `review_date` is `expiry - 30 days` — the intervals of the
§95.2 exhibit (spec L8666–L8668), transcribed, not chosen. See DECISION REQUIRED #3.

**Commands**

```bash
cd "$CP_ROOT"
S=$(date -u +%F)
E=$(date -u -d "$S +91 days" +%F)
R=$(date -u -d "$E -30 days" +%F)
echo "start=$S expiry=$E review=$R"

{
printf '%s\n' \
'# gate-register.tsv — L0-owned (L0D-19). THE source of truth for bootstrap exceptions.' \
'# docs/bootstrap/exceptions/*.yaml are RENDERED from this file; never hand-edit them.' \
'# 14 tab-separated fields, in this order:' \
'#  1 id  2 threshold  3 scope  4 policy  5 risk_accepted  6 compensating_extra' \
'#  7 deactivation_trigger  8 start  9 expiry  10 review_date  11 renewals  12 closure' \
'#  13 closed_on  14 spec_line' \
'# expiry is MANDATORY (invariant 77, spec L9554; Section 54.2 L4789).' \
'# deactivation_trigger is MANDATORY (Section 95.2, spec L8676).' \
'# closure and closed_on are "-" while the exception is open. Records are never deleted' \
'# (Section 54.2, spec L4796); a closed row stays here with closure: trigger_satisfied.'
while IFS='|' read -r id thr scope pol risk extra trig line; do
  [ -n "$id" ] || continue
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t0\t-\t-\t%s\n' \
    "$id" "$thr" "$scope" "$pol" "$risk" "$extra" "$trig" "$S" "$E" "$R" "$line"
done <<'ROWS'
EXC-BOOT-001|T2W|gate-2-independent-review|no-self-approval|unreviewed changes reach the default branches of the named repositories|-|second context-holding engineer with Write onboarded to the named repositories|L8650-8671
EXC-BOOT-002|T2W|no-self-approval|no-self-approval|an author's own approval satisfies the merge gate on the named repositories|-|a second human with Write who can approve on the named repositories|L8703
EXC-BOOT-003|T2W|most-recent-push-approval|no-self-approval|commits pushed after an approval reach the default branch without re-approval|-|a second human with Write who can approve the most recent reviewable push|L8703
EXC-BOOT-004|T3H|production-approver-not-deploying-actor|production-approval-separation|the approving identity and the deploying identity are the same person|the explicit production-approval event remains a distinct recorded event (Section 95.3 L8695)|a third human holding production-approval who is not the deploying actor|L8704
EXC-BOOT-005|T3H|cross-review-matrix-real-routing|reviewer-matrix|the review-routing table resolves to the author of the change|-|a third human, so the routing table resolves to a person who is not the author|L8704
EXC-BOOT-006|TQA|independent-verification-authority|verification-authority|verification judgments are exercised by the author of the change under test|the Founder exercises QA-judgment calls under this record (Section 95.2 L8683)|the QA role is filled|L8705
EXC-BOOT-007|TQA|release-readiness-signoff|verification-authority|release readiness is signed off by the releasing party|-|the QA role is filled|L8705
EXC-BOOT-008|TQA|uat-ownership|verification-authority|UAT is owned by the author of the change under test|-|the QA role is filled|L8705
EXC-BOOT-009|T4P|backup-owner-coverage|ownership-slot-orphan-checks|products carry an empty Backup Owner slot|the empty slots are declared, not silent (Section 95.2 L8682)|a fourth human, so every product has a backup owner|L8682
EXC-BOOT-010|T4P|knowledge-redundancy-floor|ownership-slot-orphan-checks|single-person knowledge dependencies exist with no measured floor|-|a fourth human, so the knowledge-redundancy floor is measurable|L8706
EXC-BOOT-011|T4P|responder-rotation|ownership-slot-orphan-checks|one person is the responder for every product|-|a fourth human, so a responder rotation exists|L8706
EXC-BOOT-012|T2W|gate-1-plan-approval|no-self-approval|a plan is approved by its own author on the named repositories|Section 26.1 L2497 names Gate 2 independent review as the compensating control; Gate 2 is itself relaxed by EXC-BOOT-001 during bootstrap - the control actually in force is the CI verification contract and the Section 26.4 authority-delta gate, pending the L0 ruling recorded as DECISION REQUIRED 2 in implementation/lanes/L0-06-bootstrap-mode.md|a second holder of plan-approval who is not the plan author|L2497
EXC-BOOT-013|FCC|founder-operational-capability-holding|capability-concentration|one person holds plan-approval, code-review, production-approval, incident-response and verification judgment on the named repositories|each capability is shed as the corresponding role fills, recorded in people.yaml and in the weekly bootstrap log (Section 95.2 L8681)|every listed operational capability is held by a role-holder other than the Founder|L8681
ROWS
} > docs/bootstrap/gate-register.tsv

printf '%s\n' \
'# activation-checklist.tsv — L0-owned. MasterSpec v4.0 Section 95.4 table (spec L8701-L8706),' \
'# transcribed. Row FCC is not from that table: its source is Section 95.2 (spec L8681).' \
'# Format: <threshold_id><TAB><headcount reached><TAB><gates armed><TAB><verification><TAB><verbatim><TAB><spec_line>' > docs/bootstrap/activation-checklist.tsv
printf 'T2W\t2 humans with Write\tNo self-approval; Gate 2 independent review; most-recent-push approval\tA self-approved PR fails branch protection; a Read-only approval does not satisfy it; a Write-holding cross-reviewer approval does\tyes\tL8703\n' >> docs/bootstrap/activation-checklist.tsv
printf 'T3H\t3 humans\tProduction approver != deploying actor; cross-review matrix with real routing\tA deploy attempted by its approver is rejected; the review-routing table resolves to a person who is not the author\tyes\tL8704\n' >> docs/bootstrap/activation-checklist.tsv
printf 'TQA\tQA role filled\tIndependent verification authority; release readiness sign-off; UAT ownership\tA release blocked by QA stays blocked; verification contracts reviewed and owned by QA\tyes\tL8705\n' >> docs/bootstrap/activation-checklist.tsv
printf 'T4P\t4+ humans\tBackup Owner coverage; knowledge-redundancy floor; responder rotation\tOrphan detection reports zero blocking orphans; every product has a non-author reviewer and a backup\tyes\tL8706\n' >> docs/bootstrap/activation-checklist.tsv
printf 'FCC\teach corresponding role filled\tFounder operational-capability holding\tEach capability is shed as its role fills and the shedding is recorded in people.yaml\tno\tL8681\n' >> docs/bootstrap/activation-checklist.tsv

# Record the transcription of the calibrated intervals (L0D-17; DECISION REQUIRED #3).
d=$(date -u +%F)
cat > "docs/plan/decisions/${d}-bootstrap-exception-intervals.md" <<EOF
# DECISION — bootstrap exception intervals — $d

decision_id: L0D-17 (calibrated configuration)
subject: bootstrap exception lifetime and review offset
value: expiry = start + 91 days; review_date = expiry - 30 days
basis: |
  Transcribed from the MasterSpec v4.0 Section 95.2 exhibit, spec L8666-L8668:
  start 2026-09-01, expiry 2026-12-01, review_date 2026-11-01. No value was chosen.
  Section 54.2 (spec L4797) independently requires a bounded expiry whatever the number is.
open: |
  L0 confirms or replaces these initial values. See DECISION REQUIRED #3 in
  implementation/lanes/L0-06-bootstrap-mode.md. Until then these are the values in force.
EOF

git add docs/bootstrap/gate-register.tsv docs/bootstrap/activation-checklist.tsv "docs/plan/decisions/${d}-bootstrap-exception-intervals.md"
git commit -m "L0-06-03: gate register, activation checklist, interval decision (L0D-19)"
git push origin integration
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Thirteen gate rows | `grep -vc '^#' docs/bootstrap/gate-register.tsv` | `13` |
| 2 | Every row is exactly 14 tab-separated fields | `awk -F'\t' '!/^#/ && NF!=14' docs/bootstrap/gate-register.tsv \| wc -l` | `0` |
| 3 | Ids are contiguous `EXC-BOOT-001`…`EXC-BOOT-013` | `awk -F'\t' '!/^#/{print $1}' docs/bootstrap/gate-register.tsv \| sed 's/EXC-BOOT-//' \| tr '\n' ' '` | `001 002 003 004 005 006 007 008 009 010 011 012 013 ` |
| 4 | No scope appears twice — one exception per relaxed gate | `awk -F'\t' '!/^#/{print $3}' docs/bootstrap/gate-register.tsv \| sort \| uniq -d \| wc -l` | `0` |
| 5 | Every row carries an expiry in `YYYY-MM-DD` (invariant 77) | `awk -F'\t' '!/^#/ && $9 !~ /^[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]$/' docs/bootstrap/gate-register.tsv \| wc -l` | `0` |
| 6 | Every row carries a non-empty deactivation trigger | `awk -F'\t' '!/^#/ && ($7=="" \|\| $7=="-")' docs/bootstrap/gate-register.tsv \| wc -l` | `0` |
| 7 | Every threshold used exists in the checklist | `join -v1 <(awk -F'\t' '!/^#/{print $2}' docs/bootstrap/gate-register.tsv \| sort -u) <(awk -F'\t' '!/^#/{print $1}' docs/bootstrap/activation-checklist.tsv \| sort -u) \| wc -l` | `0` |
| 8 | The checklist has the four §95.4 rows plus FCC | `awk -F'\t' '!/^#/{print $1}' docs/bootstrap/activation-checklist.tsv \| tr '\n' ' '` | `T2W T3H TQA T4P FCC ` |
| 9 | `EXC-BOOT-001` carries the exhibit's own scope | `awk -F'\t' '$1=="EXC-BOOT-001"{print $3}' docs/bootstrap/gate-register.tsv` | `gate-2-independent-review` |

**SELF-VERIFY**

```bash
cd "$CP_ROOT"
printf 'rows=%s malformed=%s dupscope=%s no_expiry=%s no_trigger=%s thresholds=[%s] orphan_thr=%s first=%s\n' \
  "$(grep -vc '^#' docs/bootstrap/gate-register.tsv)" \
  "$(awk -F'\t' '!/^#/ && NF!=14' docs/bootstrap/gate-register.tsv | wc -l | tr -d ' ')" \
  "$(awk -F'\t' '!/^#/{print $3}' docs/bootstrap/gate-register.tsv | sort | uniq -d | wc -l | tr -d ' ')" \
  "$(awk -F'\t' '!/^#/ && $9 !~ /^[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]$/' docs/bootstrap/gate-register.tsv | wc -l | tr -d ' ')" \
  "$(awk -F'\t' '!/^#/ && ($7=="" || $7=="-")' docs/bootstrap/gate-register.tsv | wc -l | tr -d ' ')" \
  "$(awk -F'\t' '!/^#/{print $1}' docs/bootstrap/activation-checklist.tsv | tr '\n' ' ' | sed 's/ $//')" \
  "$(join -v1 <(awk -F'\t' '!/^#/{print $2}' docs/bootstrap/gate-register.tsv | sort -u) <(awk -F'\t' '!/^#/{print $1}' docs/bootstrap/activation-checklist.tsv | sort -u) | wc -l | tr -d ' ')" \
  "$(awk -F'\t' '$1=="EXC-BOOT-001"{print $3}' docs/bootstrap/gate-register.tsv)"
```

Expected output, exactly:

```
rows=13 malformed=0 dupscope=0 no_expiry=0 no_trigger=0 thresholds=[T2W T3H TQA T4P FCC] orphan_thr=0 first=gate-2-independent-review
```

**STOP rule** — if `no_expiry` or `no_trigger` is non-zero, **do not commit.** An exception without an expiry is not
an exception; invariant 77 (spec L9554) says it *"is invalid and fails CI"* and §54.2 (spec L4789) adds *"it is
undocumented policy"*. An exception without a deactivation trigger cannot ever close as `trigger_satisfied`
(§54.2, spec L4796) and becomes exactly the failure §95.4 L8712 names: *"stubbed gates have a habit of staying
stubbed"*. If `dupscope` is non-zero you have written two exceptions for one gate, which breaks §95.2 L8646 and
defeats the same-scope renewal rule of invariant 77 — merge the rows, do not renumber them. If you believe a
fourteenth relaxed gate exists, open `BLOCKER L0-06-03: gate <scope> is relaxed and unregistered`; enumerating the
relaxed gates beyond the two spec sources above is L0D-19, not an executor's reading.

---

### L0-06-04 — The renderer and the fail-closed checker

**Size:** L · **Dependencies:** L0-06-03

Two scripts. The renderer turns one TSV row into one exception record in the §95.2 field order. The checker re-runs
the renderer into a temporary tree and compares, so a hand-edit to a rendered file is a violation rather than a
silent divergence — the same reason `lane-guard.sh` hard-codes its guard-critical list rather than reading it from
something a change could propose to alter (`L0-02-lane-guard.md` §5.2).

**Commands**

```bash
cd "$CP_ROOT"
cat > docs/plan/bin/bootstrap-render.sh <<'REND'
#!/usr/bin/env sh
# =============================================================================
# bootstrap-render.sh — L0-owned (docs/plan/bin, master/08 Section 2.1).
# Renders docs/bootstrap/exceptions/EXC-BOOT-NNN.yaml from gate-register.tsv.
# Field names and order: MasterSpec v4.0 Section 54.1 (spec L4752-4785) as used
# by the Section 95.2 bootstrap exhibit (spec L8648-8672).
# Exit 0 rendered / 2 configuration error — FAIL CLOSED (Section 64).
# Env: CP  repository root (default: $PWD)
# =============================================================================
set -u
CP="${CP:-$PWD}"
REG="$CP/docs/bootstrap/gate-register.tsv"
SCOPE="$CP/docs/bootstrap/repo-scope.tsv"
OUT="$CP/docs/bootstrap/exceptions"
TAB=$(printf '\t')
cfgfail() { printf 'BOOTSTRAP-RENDER FAIL: configuration error — %s\n' "$1"; exit 2; }
[ -f "$REG" ]   || cfgfail "gate-register.tsv not found at $REG"
[ -f "$SCOPE" ] || cfgfail "repo-scope.tsv not found at $SCOPE"
awk -F"$TAB" '!/^#/ && NF>0 && NF!=14 {bad++} END{exit(bad?1:0)}' "$REG" \
  || cfgfail "gate-register.tsv has a row that is not exactly 14 tab-separated fields"
REPOS=$(awk -F"$TAB" '!/^#/ && $2=="bootstrap" {printf "%s%s", sep, $1; sep=", "}' "$SCOPE")
[ -n "$REPOS" ] || cfgfail "no repository is in bootstrap mode; there is nothing to except"
mkdir -p "$OUT" || cfgfail "cannot create $OUT"
COMMON='full CI verification contract on every push; append-only history, nothing rewritten; production deploys still require the explicit approval event'
n=0
while IFS="$TAB" read -r id thr scope policy risk extra trig start expiry review renewals closure closed line; do
  case "${id:-}" in ''|\#*) continue ;; esac
  comp="$COMMON"
  [ "$extra" = "-" ] || comp="$comp; $extra"
  if [ "$closure" = "-" ]; then clo="null"; else clo="$closure"; fi
  {
    printf '# %s — RENDERED by docs/plan/bin/bootstrap-render.sh from docs/bootstrap/gate-register.tsv.\n' "$id"
    printf '# DO NOT HAND-EDIT. Edit the register and re-render; docs/plan/bin/bootstrap-check.sh compares.\n'
    printf '# Fields: MasterSpec v4.0 Section 54.1 (spec L4752-4785). Bootstrap shape: Section 95.2 (spec L8648-8672).\n'
    printf '# Gate source: spec %s. Threshold: %s (docs/bootstrap/activation-checklist.tsv).\n' "$line" "$thr"
    printf -- '- id: %s\n' "$id"
    printf '  type: bootstrap\n'
    printf '  scope: %s\n' "$scope"
    printf '  affected:\n'
    printf '    repositories: [%s]\n' "$REPOS"
    printf '  policy: %s\n' "$policy"
    printf '  reason: no second context-holding human holds Write on these repositories during the solo build\n'
    printf '  risk_accepted: %s\n' "$risk"
    printf '  compensating_control: %s\n' "$comp"
    printf '  compensating_control_record: CI run history on the named repositories\n'
    printf '  compensating_control_cadence: per-push\n'
    printf '  requester: founder\n'
    printf '  authority: founder\n'
    printf '  owner: founder\n'
    printf '  start: %s\n' "$start"
    printf '  expiry: %s\n' "$expiry"
    printf '  review_date: %s\n' "$review"
    printf '  renewals: %s\n' "$renewals"
    printf '  deactivation_trigger: %s\n' "$trig"
    printf '  closure: %s\n' "$clo"
  } > "$OUT/$id.yaml" || cfgfail "cannot write $OUT/$id.yaml"
  n=$((n + 1))
done < "$REG"
printf 'BOOTSTRAP-RENDER OK: %s exception(s) into %s\n' "$n" "$OUT"
exit 0
REND
chmod +x docs/plan/bin/bootstrap-render.sh

cat > docs/plan/bin/bootstrap-check.sh <<'CHK'
#!/usr/bin/env sh
# =============================================================================
# bootstrap-check.sh — L0-owned. The pre-flight L0 runs before CI does.
# Implements the Phase 1 minimal rule set (expiry, owner, deactivation trigger —
# MasterSpec v4.0 Section 95.2, spec L8677) plus the bootstrap-specific rules of
# Section 95.1/95.2 and the renewal rule of Section 54.2 (spec L4791).
# It does NOT replace L1's registry validator; it catches the same class of fault
# one step earlier, on L0's authored source.
# Exit 0 BOOTSTRAP-CHECK OK / 1 violations / 2 configuration error — FAIL CLOSED.
# Env: CP repository root; BOOT_TODAY ISO date for expiry comparison (tests only).
# =============================================================================
set -u
CP="${CP:-$PWD}"
REG="$CP/docs/bootstrap/gate-register.tsv"
SCOPE="$CP/docs/bootstrap/repo-scope.tsv"
DIR="$CP/docs/bootstrap/exceptions"
DEC="$CP/docs/plan/decisions"
TODAY="${BOOT_TODAY:-$(date -u +%F)}"
TAB=$(printf '\t')
V=0
cfgfail() { printf 'BOOTSTRAP-CHECK FAIL: configuration error — %s\n' "$1"; exit 2; }
viol()    { printf 'BOOTSTRAP-VIOLATION [%s] %s: %s\n' "$1" "$2" "$3"; V=$((V + 1)); }

[ -f "$REG" ]   || cfgfail "gate-register.tsv not found at $REG"
[ -f "$SCOPE" ] || cfgfail "repo-scope.tsv not found at $SCOPE"
[ -d "$DIR" ]   || cfgfail "exceptions directory not found at $DIR"
awk -F"$TAB" '!/^#/ && NF>0 && NF!=14 {bad++} END{exit(bad?1:0)}' "$REG" \
  || cfgfail "gate-register.tsv has a row that is not exactly 14 tab-separated fields"
awk -F"$TAB" '!/^#/ && NF>0 && NF!=3 {bad++} END{exit(bad?1:0)}' "$SCOPE" \
  || cfgfail "repo-scope.tsv has a row that is not exactly 3 tab-separated fields"
command -v diff >/dev/null || cfgfail "diff not available; the render comparison cannot run"

# B9 — one exception per relaxed gate (Section 95.2 L8646; invariant 77 same-scope rule)
for s in $(awk -F"$TAB" '!/^#/{print $3}' "$REG" | sort | uniq -d); do
  viol SCOPE-DUPLICATE "$s" "two exceptions name one gate; Section 95.2 L8646 says one per relaxed gate"
done

TD=$(printf '%s' "$TODAY" | tr -d '-')
while IFS="$TAB" read -r id thr scope policy risk extra trig start expiry review renewals closure closed line; do
  case "${id:-}" in ''|\#*) continue ;; esac
  case "$id" in EXC-BOOT-[0-9][0-9][0-9]) : ;; *) viol ID-SHAPE "$id" "id must match EXC-BOOT-NNN" ;; esac
  [ -f "$DIR/$id.yaml" ] || viol NOT-RENDERED "$id" "no rendered record at docs/bootstrap/exceptions/$id.yaml"
  # B3 — expiry mandatory (invariant 77, spec L9554)
  case "$expiry" in
    [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]) : ;;
    *) viol NO-EXPIRY "$id" "expiry must be YYYY-MM-DD; invariant 77 rejects an exception without one" ;;
  esac
  # B5 — deactivation trigger mandatory (Section 95.2, spec L8676)
  case "${trig:-}" in ''|-|null) viol NO-TRIGGER "$id" "deactivation_trigger is mandatory (Section 95.2 L8676)" ;; esac
  # B10 — renewals numeric
  case "$renewals" in ''|*[!0-9]*) viol RENEWALS "$id" "renewals must be a non-negative integer" ;; esac
  # B7 — an expiry in the past with the gate still unarmed is SIG-39 (spec L4568)
  if [ "$closure" = "-" ]; then
    _e=$(printf '%s' "$expiry" | tr -d '-')
    case "$_e" in
      [0-9]*) [ "$_e" -ge "$TD" ] || viol SIG-39 "$id" "expired $expiry with the gate still unarmed; Red on the Founder view" ;;
    esac
  else
    case "$closure" in
      expired|remediated|promoted_to_policy|trigger_satisfied) : ;;
      *) viol CLOSURE "$id" "closure must be one of expired|remediated|promoted_to_policy|trigger_satisfied (Section 54.1 L4782)" ;;
    esac
    case "$closed" in
      [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]) : ;;
      *) viol CLOSURE-DATE "$id" "a closed exception carries closed_on as YYYY-MM-DD" ;;
    esac
  fi
  # B11 — third renewal requires the re-affirmation record (Section 54.2, spec L4791)
  if [ "$closure" = "-" ] && [ "${renewals:-0}" -ge 3 ] 2>/dev/null; then
    ls "$DEC"/*reaffirm-"$id".md >/dev/null 2>&1 \
      || viol REAFFIRM "$id" "renewals=$renewals with no docs/plan/decisions/*reaffirm-$id.md; Section 54.2 L4791 forces remediate, promote or re-affirm"
  fi
done < "$REG"

# B4/B6 — owner present, and every named repository is in bootstrap mode (Section 95.2 L8678)
for f in "$DIR"/*.yaml; do
  [ -e "$f" ] || continue
  b=$(basename "$f" .yaml)
  [ "$(grep -c '^  owner: ' "$f")" = "1" ] || viol NO-OWNER "$b" "exactly one owner line is required (Section 95.2 L8676)"
  reps=$(sed -n 's/^    repositories: \[\(.*\)\]$/\1/p' "$f" | tr ',' '\n' | sed 's/^ *//; s/ *$//')
  [ -n "$reps" ] || viol NO-REPOS "$b" "the exception names no repository; Section 95.2 L8676 requires it"
  for r in $reps; do
    m=$(awk -F"$TAB" -v r="$r" '!/^#/ && $1==r {print $2}' "$SCOPE")
    [ "$m" = "bootstrap" ] || viol FOREIGN-REPO "$b" "repository '$r' has mode '${m:-armed}'; Section 95.2 L8678 forbids covering it"
  done
done

# B1 — the rendered tree must be exactly what the register renders (no hand-edits)
TMP=$(mktemp -d 2>/dev/null || mktemp -d -t bck) || cfgfail "mktemp failed"
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/docs/bootstrap" "$TMP/docs/plan/bin"
cp "$REG" "$SCOPE" "$TMP/docs/bootstrap/" || cfgfail "cannot stage the register"
CP="$TMP" sh "$CP/docs/plan/bin/bootstrap-render.sh" >/dev/null || cfgfail "bootstrap-render.sh failed on the staged copy"
if ! diff -r "$DIR" "$TMP/docs/bootstrap/exceptions" >/dev/null 2>&1; then
  diff -r "$DIR" "$TMP/docs/bootstrap/exceptions" 2>&1 | sed 's/^/  /'
  viol HAND-EDITED "docs/bootstrap/exceptions" "a rendered record differs from what the register renders; re-render, do not edit"
fi

printf '\n'
if [ "$V" -eq 0 ]; then printf 'BOOTSTRAP-CHECK OK\n'; exit 0; fi
printf 'BOOTSTRAP-CHECK FAIL: %s violation(s)\n' "$V"
exit 1
CHK
chmod +x docs/plan/bin/bootstrap-check.sh

grep -q '^bootstrap-render:' Makefile || cat >> Makefile <<'MK'

bootstrap-render:
	@CP=$(CURDIR) sh docs/plan/bin/bootstrap-render.sh

bootstrap-check:
	@CP=$(CURDIR) sh docs/plan/bin/bootstrap-check.sh
MK

make bootstrap-render
make bootstrap-check

git add docs/plan/bin/bootstrap-render.sh docs/plan/bin/bootstrap-check.sh docs/bootstrap/exceptions Makefile
git commit -m "L0-06-04: bootstrap renderer and fail-closed checker"
git push origin integration
```

**The adversarial proof — run it, do not assume it.** A checker that has never failed is not known to work
(§53.1 seeded-canary reasoning, spec L4680). Four deliberate faults, each reverted immediately.

**Commands**

```bash
cd "$CP_ROOT"
cp docs/bootstrap/gate-register.tsv /tmp/gr.bak

# F1 — remove an expiry (invariant 77)
awk -F'\t' -v OFS='\t' '$1=="EXC-BOOT-002"{$9=""}1' /tmp/gr.bak > docs/bootstrap/gate-register.tsv
make bootstrap-check | grep -c 'NO-EXPIRY'          # expect 1

# F2 — remove a deactivation trigger (Section 95.2 L8676)
awk -F'\t' -v OFS='\t' '$1=="EXC-BOOT-002"{$7="-"}1' /tmp/gr.bak > docs/bootstrap/gate-register.tsv
make bootstrap-check | grep -c 'NO-TRIGGER'         # expect 1

# F3 — cover a repository that is not in bootstrap mode (Section 95.2 L8678)
cp docs/bootstrap/repo-scope.tsv /tmp/rs.bak
printf 'product-alpha\tarmed\tdeliberate self-test row\n' >> docs/bootstrap/repo-scope.tsv
cp /tmp/gr.bak docs/bootstrap/gate-register.tsv
sed -i 's/^    repositories: \[.*\]$/    repositories: [product-alpha]/' docs/bootstrap/exceptions/EXC-BOOT-001.yaml
make bootstrap-check | grep -c 'FOREIGN-REPO'       # expect 1
cp /tmp/rs.bak docs/bootstrap/repo-scope.tsv

# F4 — hand-edit a rendered record
cp /tmp/gr.bak docs/bootstrap/gate-register.tsv
make bootstrap-render >/dev/null
sed -i 's/^  owner: founder$/  owner: nobody/' docs/bootstrap/exceptions/EXC-BOOT-003.yaml
make bootstrap-check | grep -c 'HAND-EDITED'        # expect 1

# restore and prove clean
cp /tmp/gr.bak docs/bootstrap/gate-register.tsv
make bootstrap-render >/dev/null
make bootstrap-check | tail -1                      # expect BOOTSTRAP-CHECK OK
git checkout -- docs/bootstrap
rm -f /tmp/gr.bak /tmp/rs.bak
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Thirteen records rendered | `ls docs/bootstrap/exceptions/*.yaml \| wc -l` | `13` |
| 2 | Every record carries the three minimal fields (§95.2 L8677) | `for f in docs/bootstrap/exceptions/*.yaml; do for k in expiry owner deactivation_trigger; do grep -q "^  $k: " "$f" \|\| echo "MISSING $k $f"; done; done; echo DONE` | `DONE` alone |
| 3 | Every record is `type: bootstrap` | `grep -c '^  type: bootstrap$' docs/bootstrap/exceptions/*.yaml \| grep -vc ':1$'` | `0` |
| 4 | `EXC-BOOT-001` reproduces the exhibit's scope, policy and trigger | `sed -n 's/^  \(scope\|policy\|deactivation_trigger\): //p' docs/bootstrap/exceptions/EXC-BOOT-001.yaml \| tr '\n' '\|'` | `gate-2-independent-review\|no-self-approval\|second context-holding engineer with Write onboarded to the named repositories\|` |
| 5 | The checker passes on the committed tree | `make bootstrap-check \| tail -1` | `BOOTSTRAP-CHECK OK` |
| 6 | The checker fails closed with no register | `CP=/nonexistent sh docs/plan/bin/bootstrap-check.sh; echo "exit=$?"` | last two lines: a `configuration error` line, then `exit=2` |
| 7 | All four adversarial faults are caught | the four `grep -c` commands above | `1`, `1`, `1`, `1` |

**SELF-VERIFY**

```bash
cd "$CP_ROOT"
make bootstrap-render >/dev/null
printf 'rendered=%s minimal=%s type=%s check=%s failclosed=%s\n' \
  "$(ls docs/bootstrap/exceptions/*.yaml | wc -l | tr -d ' ')" \
  "$(for f in docs/bootstrap/exceptions/*.yaml; do for k in expiry owner deactivation_trigger; do grep -q "^  $k: " "$f" || echo x; done; done | wc -l | tr -d ' ')" \
  "$(grep -l '^  type: bootstrap$' docs/bootstrap/exceptions/*.yaml | wc -l | tr -d ' ')" \
  "$(make bootstrap-check | tail -1)" \
  "$(CP=/nonexistent sh docs/plan/bin/bootstrap-check.sh >/dev/null 2>&1; echo $?)"
```

Expected output, exactly:

```
rendered=13 minimal=0 type=13 check=BOOTSTRAP-CHECK OK failclosed=2
```

**STOP rule** — if `failclosed` is anything other than `2`, the checker fails **open**, and a control that passes when
it cannot read its own inputs is not a control (§53.1, spec L4680; fail-closed classification is invariant 80 and
L0D-18). Fix the `cfgfail` path before committing; do not proceed with a checker whose green output cannot be
trusted. If any of the four adversarial faults prints `0`, the corresponding rule is not enforced — that is the exact
failure mode §95.1 L8640 warns about, *"a gate that appears to be working and is not"*. Do not weaken the fault to
make the test pass.

---

### L0-06-05 — The arming matrix: unarmed beside armed, in D101 order

**Size:** M · **Dependencies:** L0-06-01

§95.2 L8680 requires the pair to be recorded together *"so arming a gate is a configuration flip, not a build
project"*. This task records the pair as L0's governance artifact. The payloads GitHub receives are L5's
(`access/branch-protection/`, `L5-01-07`) and the arming-order gate is L5's (`access/arming/`, `L5-01-10`).

**The unarmed configuration is defined exhaustively by four facts** and nothing else — spec L8680: require-PR stays
on; direct-push blocking stays on; required approving reviews is 0; the workflow-identity gate is not yet enforcing.
§95.3 L8687 then closes the question for every other §11.3 row: *"Bootstrap relaxes independence requirements
only."* So every other row of the §11.3 checklist is armed from day one, and the matrix says so with its spec line.
The Code-Owner requirement is not a fifth fact: §98.2 L9017 names it and the approval count as one thing — the
*"Code-Owner-and-approval gate"* — and they arm together at `T2W`.

**Commands**

```bash
cd "$CP_ROOT"
printf '%s\n' \
'# arming-matrix.tsv — L0-owned. The unarmed configuration recorded BESIDE the armed one,' \
'# per MasterSpec v4.0 Section 95.2 (spec L8680), so arming is a flip and not a project.' \
'# D101 (spec L10194) fixes the ORDER: Teams grant Write BEFORE branch protection is armed.' \
'# Format: <n><TAB><setting><TAB><unarmed><TAB><armed><TAB><arms_at><TAB><spec_line><TAB><declared_by>' \
'# arms_at: day-one | T2W | T3H | per-phase. declared_by names the L5 artifact that renders it.' \
'# L0 NEVER edits access/**. This file is the governance record, not the payload.' > docs/bootstrap/arming-matrix.tsv
printf '1\torganisation_base_permission\tRead\tRead\tday-one\tL9017\tL5 access/org (L5-01-03)\n'                                          >> docs/bootstrap/arming-matrix.tsv
printf '2\tteams_grant_write\tgranted from the interim assignment set\tgranted from the registry-derived set at Phase 3\tday-one\tL9017 D101 L10194\tL5 access/teams (L5-01-05)\n' >> docs/bootstrap/arming-matrix.tsv
printf '3\trequire_pull_request\ttrue\ttrue\tday-one\tL8680 L862\tL5 access/branch-protection (L5-01-07)\n'                               >> docs/bootstrap/arming-matrix.tsv
printf '4\tblock_direct_push_to_default\ttrue\ttrue\tday-one\tL8680 L869\tL5 access/branch-protection (L5-01-07)\n'                       >> docs/bootstrap/arming-matrix.tsv
printf '5\trequired_approving_review_count\t0\t1\tT2W\tL8680 L863\tL5 access/branch-protection (L5-01-07)\n'                              >> docs/bootstrap/arming-matrix.tsv
printf '6\trequire_code_owner_review\tinert while count is 0\ttrue\tT2W\tL9017 L864\tL5 access/branch-protection (L5-01-07)\n'            >> docs/bootstrap/arming-matrix.tsv
printf '7\trequire_approval_of_most_recent_push\ttrue\ttrue\tday-one\tL865 L8687\tL5 access/branch-protection (L5-01-07)\n'               >> docs/bootstrap/arming-matrix.tsv
printf '8\tdismiss_stale_approvals\ttrue\ttrue\tday-one\tL866 L8687\tL5 access/branch-protection (L5-01-07)\n'                            >> docs/bootstrap/arming-matrix.tsv
printf '9\trequired_status_checks\tEMPTY LIST per repository\tone context added per phase as each check comes into existence\tper-phase\tL9018\tL5 access/branch-protection (L5-01-07); a lane adding one is F-07\n' >> docs/bootstrap/arming-matrix.tsv
printf '10\trequire_branches_up_to_date\ttrue\ttrue\tday-one\tL867 L8687\tL5 access/branch-protection (L5-01-07)\n'                       >> docs/bootstrap/arming-matrix.tsv
printf '11\tblock_force_push_and_deletion\ttrue\ttrue\tday-one\tL869 L8687\tL5 access/branch-protection (L5-01-07)\n'                     >> docs/bootstrap/arming-matrix.tsv
printf '12\tenforce_admins\ttrue\ttrue\tday-one\tL870 L8687\tL5 access/branch-protection (L5-01-07)\n'                                    >> docs/bootstrap/arming-matrix.tsv
printf '13\tdeployment_branch_and_tag_policy\tapplied from the template on every environment\tapplied from the template on every environment\tday-one\tL871 L9024\tL5 access/environments (L5-01-08)\n' >> docs/bootstrap/arming-matrix.tsv
printf '14\tworkflow_identity_gate_production\tnot enforcing\tactive on production deploys\tT3H\tL8680 L2571\tL5 access/branch-protection (L5-01-07); Section 27.2\n' >> docs/bootstrap/arming-matrix.tsv

cat > docs/bootstrap/arming-order.md <<'ORD'
# The D101 arming order — step N may not start until step N-1 is recorded

Authority: D101 (spec L10194); Section 98.2 Phase 1 (spec L9017-L9018); Section 95.2 (spec L8680).
The gate that mechanically refuses an unsatisfiable arming is L5's (access/arming/, L5-01-10).
This file is L0's record of the order and of the evidence for each step.

| # | Step | Evidence recorded at | Done? |
|---|---|---|---|
| 1 | Organisation base permission = Read | L5-01-03 apply runbook output | |
| 2 | Teams created and GRANTING WRITE, interim assignment set | L5-01-05 + L5-01-12 runbook output | |
| 3 | Branch protection applied in the UNARMED profile | L5-01-07 + L5-01-12 runbook output | |
| 4 | Required-status-check list EMPTY per repository | L5-01-13 Phase 1 access completion check | |
| 5 | Checks added per phase, named by that phase's completion check | each phase's completion check | |
| 6 | Code-Owner-and-approval gate ARMED (rows 5 and 6 of arming-matrix.tsv) | docs/bootstrap/activation/T2W-<date>.md (L0-06-09) | |
| 7 | Workflow-identity gate ARMED on production deploys (row 14) | docs/bootstrap/activation/T3H-<date>.md (L0-06-10) | |

## Why the order and not the list

Section 98.2 L9017, verbatim: "Arming a Code-Owner-and-approval gate while no Team grants Write leaves
nobody whose approval counts, and Section 95.4 names the result exactly: a team that experiences its
merges mysteriously breaking." Section 98.2 L9018 states the second half: "A required check no workflow
emits blocks every pull request indefinitely; a list that silently stays empty is a gate that reads armed
and is not."

Step 2 BEFORE step 3. This is the D101 correction and it is not negotiable.
ORD

git add docs/bootstrap/arming-matrix.tsv docs/bootstrap/arming-order.md
git commit -m "L0-06-05: arming matrix and the D101 arming order (Section 95.2 L8680)"
git push origin integration
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Fourteen settings, each with both values | `grep -vc '^#' docs/bootstrap/arming-matrix.tsv` | `14` |
| 2 | Every row is exactly seven tab-separated fields | `awk -F'\t' '!/^#/ && NF!=7' docs/bootstrap/arming-matrix.tsv \| wc -l` | `0` |
| 3 | No row has an empty unarmed or armed value | `awk -F'\t' '!/^#/ && ($3=="" \|\| $4=="")' docs/bootstrap/arming-matrix.tsv \| wc -l` | `0` |
| 4 | Exactly the four §95.2 L8680 facts are non-day-one or stay-on relaxations | `awk -F'\t' '!/^#/ && $5!="day-one"{print $2}' docs/bootstrap/arming-matrix.tsv \| tr '\n' ' '` | `required_approving_review_count require_code_owner_review required_status_checks workflow_identity_gate_production ` |
| 5 | Teams-grant-Write is ordered before branch protection | `awk -F'\t' '$2=="teams_grant_write"{t=$1} $2=="require_pull_request"{p=$1} END{print (t<p)?"ORDER-OK":"ORDER-WRONG"}' docs/bootstrap/arming-matrix.tsv` | `ORDER-OK` |
| 6 | The required-check list starts empty | `awk -F'\t' '$2=="required_status_checks"{print $3}' docs/bootstrap/arming-matrix.tsv` | `EMPTY LIST per repository` |
| 7 | The order document has seven steps in D101 order | `grep -c '^| [1-7] |' docs/bootstrap/arming-order.md` | `7` |
| 8 | Every row names the L5 artifact that renders it | `awk -F'\t' '!/^#/ && $7 !~ /^L5 /' docs/bootstrap/arming-matrix.tsv \| wc -l` | `0` |

**SELF-VERIFY**

```bash
cd "$CP_ROOT"
printf 'rows=%s malformed=%s empty=%s deferred=[%s] order=%s checks=%s steps=%s l5=%s\n' \
  "$(grep -vc '^#' docs/bootstrap/arming-matrix.tsv)" \
  "$(awk -F'\t' '!/^#/ && NF!=7' docs/bootstrap/arming-matrix.tsv | wc -l | tr -d ' ')" \
  "$(awk -F'\t' '!/^#/ && ($3=="" || $4=="")' docs/bootstrap/arming-matrix.tsv | wc -l | tr -d ' ')" \
  "$(awk -F'\t' '!/^#/ && $5!="day-one"{print $2}' docs/bootstrap/arming-matrix.tsv | tr '\n' ' ' | sed 's/ $//')" \
  "$(awk -F'\t' '$2=="teams_grant_write"{t=$1} $2=="require_pull_request"{p=$1} END{print (t<p)?"ORDER-OK":"ORDER-WRONG"}' docs/bootstrap/arming-matrix.tsv)" \
  "$(awk -F'\t' '$2=="required_status_checks"{print $3}' docs/bootstrap/arming-matrix.tsv)" \
  "$(grep -c '^| [1-7] |' docs/bootstrap/arming-order.md)" \
  "$(awk -F'\t' '!/^#/ && $7 !~ /^L5 /' docs/bootstrap/arming-matrix.tsv | wc -l | tr -d ' ')"
```

Expected output, exactly:

```
rows=14 malformed=0 empty=0 deferred=[required_approving_review_count require_code_owner_review required_status_checks workflow_identity_gate_production] order=ORDER-OK checks=EMPTY LIST per repository steps=7 l5=0
```

**STOP rule** — if `order` prints `ORDER-WRONG`, stop and fix the row numbers before committing: you have recorded
the exact ordering D101 exists to correct (spec L10194 — *"Branch protection requiring a Write-holding Code Owner
approval was scheduled before any Team granted Write"*), and §98.2 L9017 names the consequence. If a value in this
matrix contradicts L5's `access/branch-protection/` profiles, **do not edit either file.** L0 does not write
`access/**` (forbidden action F-03 in reverse: the partition is symmetric) and L5 does not write `docs/**`. Open
`BLOCKER L0-06-05: arming matrix disagrees with access/branch-protection on <setting>` and let L0 rule; §11.1 (spec
L817) makes GitHub's permission semantics *"verified, not assumed"*, and L5's verified table is the one that wins on
platform behaviour.

---

### L0-06-06 — Execute the Phase 1 negative test of the minimal `exceptions.yaml` validator

**Size:** M · **Dependencies:** L0-06-04; L1 task **L1-108** (the minimal validator) must have merged

§95.2 L8677: *"Phase 1 (Section 98.2) ships a **minimal `exceptions.yaml` schema validator** in control-plane CI —
expiry present, owner present, deactivation trigger present — so bootstrap exceptions have mechanical teeth from week
one. The full exception-lifecycle validation of Phase G2 extends this validator; it never replaces the week-one
check."* The §98.2 Phase 1 completion check (spec L9024) requires it to be *"active in control-plane CI and
[to reject] a deliberately malformed exception"*.

The check has two halves and they belong to two lanes. **L0 executes both proofs; L0 writes neither validator.**

| Half | What is proved | Whose artifact | How L0 proves it |
|---|---|---|---|
| Local | the validator rejects a malformed exception | L1 `validators/registry/` | run it against L1's own negative fixtures |
| CI | the validator is *active* on every pull request | L2 `.github/workflows/` invoking L1's engine | read the workflow and the check run; this is L1 DoD-8, and the invocation boundary is `L1-00-charter.md` §12 DECISION REQUIRED #4 |

**Commands**

```bash
cd "$CP_ROOT"
git checkout integration && git pull --ff-only

# --- Half 1: local. L1's own negative fixtures, run against L1's own validator. ---
ls validators/registry/fixtures/r09/fail-no-expiry/registries/exceptions.yaml
ls validators/registry/fixtures/r09/fail-bootstrap-no-trigger/registries/exceptions.yaml

python -m validators.registry.cli validate \
  --file validators/registry/fixtures/r09/fail-no-expiry/registries/exceptions.yaml; echo "exit=$?"
python -m validators.registry.cli validate \
  --file validators/registry/fixtures/r09/fail-bootstrap-no-trigger/registries/exceptions.yaml; echo "exit=$?"

# The positive control: the shipped registry must PASS, or the negatives prove nothing.
python -m validators.registry.cli validate --file registries/exceptions.yaml; echo "exit=$?"

# --- Half 2: CI. Read-only. L0 never edits .github/** (L2) or validators/** (L1). ---
grep -rl 'validators.registry' .github/workflows/ || echo "NO-CI-INVOCATION"
gh api "repos/$ORG/control-plane/commits/$(git rev-parse origin/integration)/check-runs" \
  --jq '.check_runs[].name' | sort -u

# --- Record the evidence. This file is cited by the Phase 1 completion check. ---
d=$(date -u +%F)
mkdir -p docs/bootstrap/activation
cat > "docs/bootstrap/activation/phase1-exceptions-validator-$d.md" <<EOF
# Phase 1 completion-check evidence — minimal exceptions.yaml validator — $d

Requirement, MasterSpec v4.0 Section 98.2 Phase 1 (spec L9024): "the minimal exceptions.yaml
schema validator (expiry, owner, deactivation trigger present) is active in control-plane CI
and rejects a deliberately malformed exception". Shipping rule: Section 95.2 (spec L8677).

## Half 1 — local rejection (L1 artifact, executed by L0)
fixture: validators/registry/fixtures/r09/fail-no-expiry/            exit: <paste>  expected: non-zero
fixture: validators/registry/fixtures/r09/fail-bootstrap-no-trigger/ exit: <paste>  expected: non-zero
positive control: registries/exceptions.yaml                          exit: <paste>  expected: 0

## Half 2 — active in CI (L2 invokes L1; L1 DoD-8)
workflow file invoking the validator: <paste path, or NO-CI-INVOCATION>
check-run name observed on origin/integration: <paste, or PENDING-L1>

## L0 pre-flight on its own authored source
make bootstrap-check last line: <paste — must be BOOTSTRAP-CHECK OK>

## Disposition
<PASS | PENDING-L1 — carried as an open line in the weekly bootstrap log until it passes>
EOF

git add "docs/bootstrap/activation/phase1-exceptions-validator-$d.md"
git commit -m "L0-06-06: Phase 1 negative test of the minimal exceptions.yaml validator"
git push origin integration
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | The no-expiry fixture is rejected | `python -m validators.registry.cli validate --file validators/registry/fixtures/r09/fail-no-expiry/registries/exceptions.yaml >/dev/null 2>&1; echo $?` | any value other than `0` |
| 2 | The no-trigger fixture is rejected | `python -m validators.registry.cli validate --file validators/registry/fixtures/r09/fail-bootstrap-no-trigger/registries/exceptions.yaml >/dev/null 2>&1; echo $?` | any value other than `0` |
| 3 | The shipped registry passes — the positive control | `python -m validators.registry.cli validate --file registries/exceptions.yaml >/dev/null 2>&1; echo $?` | `0` |
| 4 | L0's own source passes its pre-flight | `make bootstrap-check \| tail -1` | `BOOTSTRAP-CHECK OK` |
| 5 | The evidence file exists and states a disposition | `grep -c '^<PASS \| ^PASS\|^PENDING-L1' "docs/bootstrap/activation/phase1-exceptions-validator-$(date -u +%F).md"` | `1` |
| 6 | L0 touched no foreign path | `git diff --name-only origin/integration~1 origin/integration \| grep -cv '^docs/'` | `0` |

**SELF-VERIFY**

```bash
cd "$CP_ROOT"
n1=$(python -m validators.registry.cli validate --file validators/registry/fixtures/r09/fail-no-expiry/registries/exceptions.yaml >/dev/null 2>&1; echo $?)
n2=$(python -m validators.registry.cli validate --file validators/registry/fixtures/r09/fail-bootstrap-no-trigger/registries/exceptions.yaml >/dev/null 2>&1; echo $?)
p1=$(python -m validators.registry.cli validate --file registries/exceptions.yaml >/dev/null 2>&1; echo $?)
printf 'no_expiry=%s no_trigger=%s positive=%s preflight=%s foreign=%s\n' \
  "$([ "$n1" -ne 0 ] && echo REJECTED || echo ACCEPTED)" \
  "$([ "$n2" -ne 0 ] && echo REJECTED || echo ACCEPTED)" \
  "$([ "$p1" -eq 0 ] && echo PASSED || echo FAILED)" \
  "$(make bootstrap-check | tail -1)" \
  "$(git diff --name-only origin/integration~1 origin/integration | grep -cv '^docs/')"
```

Expected output, exactly:

```
no_expiry=REJECTED no_trigger=REJECTED positive=PASSED preflight=BOOTSTRAP-CHECK OK foreign=0
```

**STOP rule** — if either negative prints `ACCEPTED`, **stop and do not record a PASS.** A validator that accepts an
exception with no expiry makes invariant 77 (spec L9554) unenforced and turns every bootstrap exception into
undocumented policy (§54.2, spec L4789). This is L1's artifact: open
`BLOCKER L0-06-06: minimal exceptions validator accepts a malformed exception` against lane 1, quote the exact
command and output, and **do not** fix it yourself — `validators/registry/**` is L1's exclusively (PARTITION.md line
17) and editing it is forbidden action F-03. If `positive` prints `FAILED`, the negatives prove nothing: a validator
that rejects everything is not a validator. If half 2 prints `NO-CI-INVOCATION`, record the disposition as
`PENDING-L1`, carry it as an open line in every weekly bootstrap log entry until it clears, and do not create a
workflow — `.github/workflows/**` is L2's (PARTITION.md line 18) and adding a required check is forbidden action
**F-07**.

---

### L0-06-07 — The weekly bootstrap log: template, generator, freshness check

**Size:** M · **Dependencies:** L0-06-04, L0-06-05

§95.4 L8708 specifies the entry exactly: three fields; the Founder writes it; *"the generator pre-fills two of the
three from `exceptions.yaml` and the CI run history, so the Founder writes only the judgment lines — that is what
keeps it to minutes rather than assuming it"*; and it has a detector — Blocking drift when the newest entry is older
than the calibrated staleness window, initial value 7 days.

**Where the entry lives.** §95.4 says `records/bootstrap-log/`. The record stores live in `control-plane-records`
(§40.1, D89 spec L10182; PARTITION.md line 20 gives that repository entirely to L4). Until L4 has stood that store
up, the entry is written to `docs/plan/bootstrap-log/<YYYY-MM-DD>.md` and moves at cutover — the convention
`master/08-progress-tracking.md` §7.4 already fixes. T08 performs the cutover.

Fields 1 and 2 are fully generated. Field 3 is seeded with the week's CI runs; L0 writes the result line for each.

**Commands**

```bash
cd "$CP_ROOT"
cat > docs/plan/bin/bootstrap-log-gen.sh <<'GEN'
#!/usr/bin/env sh
# =============================================================================
# bootstrap-log-gen.sh — L0-owned. The weekly bootstrap log entry of
# MasterSpec v4.0 Section 95.4 (spec L8708). Three fields; two generated.
# Usage: bootstrap-log-gen.sh [YYYY-MM-DD]   (default: today, UTC)
# Exit 0 written / 2 configuration error — FAIL CLOSED.
# =============================================================================
set -u
CP="${CP:-$PWD}"
D="${1:-$(date -u +%F)}"
REG="$CP/docs/bootstrap/gate-register.tsv"
MTX="$CP/docs/bootstrap/arming-matrix.tsv"
DIR="$CP/docs/plan/bootstrap-log"
OUT="$DIR/$D.md"
TAB=$(printf '\t')
cfgfail() { printf 'BOOTSTRAP-LOG FAIL: configuration error — %s\n' "$1"; exit 2; }
[ -f "$REG" ] || cfgfail "gate-register.tsv not found at $REG"
[ -f "$MTX" ] || cfgfail "arming-matrix.tsv not found at $MTX"
case "$D" in [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]) : ;; *) cfgfail "date must be YYYY-MM-DD — got '$D'" ;; esac
mkdir -p "$DIR" || cfgfail "cannot create $DIR"
SINCE=$(date -u -d "$D -7 days" +%F) || cfgfail "date arithmetic failed"
{
  printf '# BOOTSTRAP LOG — week ending %s\n\n' "$D"
  printf 'Template: MasterSpec v4.0 Section 95.4 (spec L8708). Fields 1 and 2 are generated;\n'
  printf 'field 3 is seeded and L0 writes the result lines. Detector: Blocking drift when the\n'
  printf 'newest entry is older than the calibrated staleness window, initial value 7 days.\n\n'

  printf '## Field 1 — gates stubbed and armed  (GENERATED from docs/bootstrap/gate-register.tsv)\n\n'
  printf '| gate scope | threshold | state | expiry | renewals | closure |\n|---|---|---|---|---|---|\n'
  awk -F"$TAB" '!/^#/ && NF==14 { st = ($12=="-") ? "STUBBED" : "ARMED";
    printf "| %s | %s | %s | %s | %s | %s |\n", $3, $2, st, $9, $11, $12 }' "$REG"
  printf '\n'
  printf '| branch-protection setting | unarmed | armed | arms at |\n|---|---|---|---|\n'
  awk -F"$TAB" '!/^#/ && NF==7 && $5!="day-one" { printf "| %s | %s | %s | %s |\n", $2, $3, $4, $5 }' "$MTX"

  printf '\n## Field 2 — bootstrap exceptions opened and closed this week  (GENERATED)\n\n'
  printf '```\n'
  git -C "$CP" log --since="$SINCE" --date=short --format='%h %ad %s' \
      --name-status -- docs/bootstrap/exceptions/ docs/bootstrap/gate-register.tsv 2>/dev/null \
    || printf 'git log unavailable\n'
  printf '```\n'
  printf '\nOpen exceptions past their review_date, needing an L0 look this week:\n\n```\n'
  awk -F"$TAB" -v d="$D" '!/^#/ && NF==14 && $12=="-" && $10 <= d { printf "%s  %s  review_date %s  expiry %s\n", $1, $3, $10, $9 }' "$REG"
  printf '```\n'

  printf '\n## Field 3 — phase completion checks run this week, and their results  (SEEDED — L0 writes the result lines)\n\n'
  printf '```\n'
  gh run list --limit 100 --json name,headBranch,conclusion,createdAt \
     --jq ".[] | select(.createdAt >= \"$SINCE\") | [.createdAt, .name, .headBranch, .conclusion] | @tsv" 2>/dev/null \
    || printf 'gh unavailable — list the runs by hand\n'
  printf '```\n\n'
  printf 'RESULT LINES — one per completion check actually run this week. L0 writes these.\n\n'
  printf -- '- check: <the Section 98.2 phase and the named completion check>\n'
  printf -- '  evidence: <workflow run URL, or the command and its output>\n'
  printf -- '  result: <PASS | FAIL | NOT-RUN>\n'
  printf -- '  judgment: <one line. Automation writes state; humans write meaning (Section 94.9)>\n\n'
  printf 'OPEN ITEMS CARRIED (delete the line when it clears):\n\n'
  printf -- '- <e.g. Phase 1 exceptions-validator CI half: PENDING-L1 (L0-06-06)>\n'
} > "$OUT" || cfgfail "cannot write $OUT"
printf 'BOOTSTRAP-LOG WRITTEN %s\n' "$OUT"
exit 0
GEN
chmod +x docs/plan/bin/bootstrap-log-gen.sh

cat > docs/plan/bin/bootstrap-log-fresh.sh <<'FRESH'
#!/usr/bin/env sh
# =============================================================================
# bootstrap-log-fresh.sh — L0-owned. The Section 95.4 staleness detector, run
# locally until the control-plane CI rule exists (L1, master/06 R-6) and the
# drift classification lands (L3 validators/drift/**).
# Window: 7 days, the initial calibrated value of Section 95.4 (spec L8708),
# changed only by a recorded decision (L0D-17). Override for tests only.
# Exit 0 fresh / 1 stale — Blocking / 2 configuration error — FAIL CLOSED.
# =============================================================================
set -u
CP="${CP:-$PWD}"
WIN="${BOOT_LOG_WINDOW_DAYS:-7}"
DIR="$CP/docs/plan/bootstrap-log"
TODAY="${BOOT_TODAY:-$(date -u +%F)}"
cfgfail() { printf 'BOOTSTRAP-LOG FAIL: configuration error — %s\n' "$1"; exit 2; }
[ -d "$DIR" ] || cfgfail "bootstrap-log directory not found at $DIR"
NEW=$(ls "$DIR"/*.md 2>/dev/null | sed 's#.*/##; s#\.md$##' | LC_ALL=C sort | tail -1)
[ -n "$NEW" ] || { printf 'BOOTSTRAP-LOG STALE age=INFINITE (no entry exists) — Blocking, Section 95.4\n'; exit 1; }
A=$(date -u -d "$TODAY" +%s) || cfgfail "cannot parse today '$TODAY'"
B=$(date -u -d "$NEW" +%s)   || cfgfail "newest entry name '$NEW' is not a date"
AGE=$(( (A - B) / 86400 ))
if [ "$AGE" -le "$WIN" ]; then
  printf 'BOOTSTRAP-LOG FRESH age=%s window=%s newest=%s\n' "$AGE" "$WIN" "$NEW"; exit 0
fi
printf 'BOOTSTRAP-LOG STALE age=%s window=%s newest=%s — Blocking, Section 95.4\n' "$AGE" "$WIN" "$NEW"
exit 1
FRESH
chmod +x docs/plan/bin/bootstrap-log-fresh.sh

grep -q '^bootstrap-log:' Makefile || cat >> Makefile <<'MK'

bootstrap-log:
	@CP=$(CURDIR) sh docs/plan/bin/bootstrap-log-gen.sh

bootstrap-fresh:
	@CP=$(CURDIR) sh docs/plan/bin/bootstrap-log-fresh.sh
MK

git add docs/plan/bin/bootstrap-log-gen.sh docs/plan/bin/bootstrap-log-fresh.sh Makefile
git commit -m "L0-06-07: weekly bootstrap log generator and staleness detector (Section 95.4)"
git push origin integration
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | The generator writes an entry | `make bootstrap-log \| tail -1` | `BOOTSTRAP-LOG WRITTEN <path>` |
| 2 | The entry carries exactly the three §95.4 fields | `grep -c '^## Field ' "docs/plan/bootstrap-log/$(date -u +%F).md"` | `3` |
| 3 | Field 1 is populated, not a placeholder | `awk '/^## Field 1/,/^## Field 2/' "docs/plan/bootstrap-log/$(date -u +%F).md" \| grep -c '^| EXC\|^| gate-\|^| no-self'` | a number greater than `0` |
| 4 | Field 3 asks for a judgment line | `grep -c 'judgment:' "docs/plan/bootstrap-log/$(date -u +%F).md"` | `1` |
| 5 | The freshness detector reports fresh today | `make bootstrap-fresh \| cut -d' ' -f1-2` | `BOOTSTRAP-LOG FRESH` |
| 6 | The detector is Blocking at window+1 days | `BOOT_TODAY=$(date -u -d "+8 days" +%F) sh docs/plan/bin/bootstrap-log-fresh.sh; echo "exit=$?"` | a `STALE` line, then `exit=1` |
| 7 | The detector fails closed with no directory | `CP=/nonexistent sh docs/plan/bin/bootstrap-log-fresh.sh; echo "exit=$?"` | a `configuration error` line, then `exit=2` |

**SELF-VERIFY**

```bash
cd "$CP_ROOT"
make bootstrap-log >/dev/null
F="docs/plan/bootstrap-log/$(date -u +%F).md"
printf 'fields=%s gates=%s judgment=%s fresh=%s stale8=%s failclosed=%s\n' \
  "$(grep -c '^## Field ' "$F")" \
  "$(awk '/^## Field 1/,/^## Field 2/' "$F" | grep -c '^| [a-z0-9-]* | T\|^| [a-z0-9-]* | FCC')" \
  "$(grep -c 'judgment:' "$F")" \
  "$(make bootstrap-fresh | cut -d' ' -f2)" \
  "$(BOOT_TODAY=$(date -u -d '+8 days' +%F) sh docs/plan/bin/bootstrap-log-fresh.sh >/dev/null 2>&1; echo $?)" \
  "$(CP=/nonexistent sh docs/plan/bin/bootstrap-log-fresh.sh >/dev/null 2>&1; echo $?)"
```

Expected output, exactly:

```
fields=3 gates=13 judgment=1 fresh=FRESH stale8=1 failclosed=2
```

**STOP rule** — if `fields` is not `3`, the template has drifted from §95.4 L8708, which names exactly three:
*"which gates are stubbed and which are armed, which bootstrap exceptions opened or closed that week, and which
phase completion checks were run with their results"*. Restore the three; do not add a fourth. If `stale8` is not
`1`, the detector does not fire and the log has no teeth — §95.4 L8708 is explicit that it *"has a detector"* and
the whole paragraph exists because *"An evidence base that nothing makes happen is reconstructed from memory at
exactly the moment the closure discipline exists to prevent that."* If you want to change the 7-day window, you may
not: it is calibrated configuration, **L0D-17**, *"changed only by a recorded decision"* (§95.4 L8708). Open the
decision first.

---

### L0-06-08 — Write the first entry, prove the detector, cut over to the records repository

**Size:** M · **Dependencies:** L0-06-07

Two things happen here. First, the log becomes a real weekly habit with a Friday slot (§94.8, spec L8590; the L0
cadence row already exists at `L0-00-charter.md` §8.2, Friday 17:00). Second, once L4 has stood up
`control-plane-records`, the store moves to where §95.4 says it lives.

**Commands**

```bash
cd "$CP_ROOT"
# --- 1. This week's entry, with the judgment lines actually written. ---
make bootstrap-log
F="docs/plan/bootstrap-log/$(date -u +%F).md"
"${EDITOR:-vi}" "$F"     # replace every <...> placeholder in Field 3 and OPEN ITEMS
grep -c '<' "$F"          # expect 0 — no placeholder survives into a committed entry

make bootstrap-fresh
git add "$F"
git commit -m "L0-06-08: bootstrap log entry $(date -u +%F)"
git push origin integration

# --- 2. Cutover. Run ONLY when control-plane-records exists and L4 has created the store. ---
cd "$CPR_ROOT"
git pull --ff-only
if [ -d records/bootstrap-log ]; then
  cp "$CP_ROOT"/docs/plan/bootstrap-log/*.md records/bootstrap-log/
  git add records/bootstrap-log
  git commit -m "L0-06-08: bootstrap log cutover from docs/plan/bootstrap-log (Section 95.4)"
  git push origin main
  ls records/bootstrap-log/*.md | wc -l
else
  echo "CUTOVER-DEFERRED: records/bootstrap-log/ does not exist yet (L4 owns it)"
fi

# --- 3. After cutover, the interim location keeps its history and stops growing. ---
cd "$CP_ROOT"
if [ -d "$CPR_ROOT/records/bootstrap-log" ]; then
  printf '%s\n' \
'# CUT OVER on '"$(date -u +%F)"'. New entries are written to records/bootstrap-log/ in the' \
'# control-plane-records repository (MasterSpec v4.0 Section 95.4; PARTITION.md line 20: that' \
'# repository is L4'"'"'s entirely). The files here are retained: history is append-only' \
'# (invariant 47) and records are never deleted (Section 54.2, spec L4796).' > docs/plan/bootstrap-log/README.md
  git add docs/plan/bootstrap-log/README.md
  git commit -m "L0-06-08: mark docs/plan/bootstrap-log as cut over"
  git push origin integration
fi
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | This week's entry exists and is committed | `git log --oneline -1 -- "docs/plan/bootstrap-log/$(date -u +%F).md" \| wc -l` | `1` |
| 2 | No placeholder survives | `grep -c '<' "docs/plan/bootstrap-log/$(date -u +%F).md"` | `0` |
| 3 | Field 3 carries at least one result line | `grep -c '^  result: \(PASS\|FAIL\|NOT-RUN\)$' "docs/plan/bootstrap-log/$(date -u +%F).md"` | a number greater than `0` |
| 4 | The detector reports fresh | `make bootstrap-fresh \| cut -d' ' -f2` | `FRESH` |
| 5 | Cutover either completed or is explicitly deferred | `test -d "$CPR_ROOT/records/bootstrap-log" && echo CUTOVER \|\| echo DEFERRED` | `CUTOVER` or `DEFERRED` — never empty |
| 6 | After cutover, no entry was lost | `ls "$CPR_ROOT"/records/bootstrap-log/*.md \| wc -l` vs `ls docs/plan/bootstrap-log/*.md \| grep -vc README \| wc -l` | the first is ≥ the second |
| 7 | The entry never entered a lane path | `git diff --name-only HEAD~1 HEAD \| grep -cv '^docs/'` | `0` |

**SELF-VERIFY**

```bash
cd "$CP_ROOT"
F="docs/plan/bootstrap-log/$(date -u +%F).md"
printf 'committed=%s placeholders=%s results=%s fresh=%s cutover=%s foreign=%s\n' \
  "$(git log --oneline -1 -- "$F" | wc -l | tr -d ' ')" \
  "$(grep -c '<' "$F")" \
  "$(grep -c '^  result: \(PASS\|FAIL\|NOT-RUN\)$' "$F")" \
  "$(make bootstrap-fresh | cut -d' ' -f2)" \
  "$(test -d "$CPR_ROOT/records/bootstrap-log" && echo CUTOVER || echo DEFERRED)" \
  "$(git diff --name-only HEAD~1 HEAD | grep -cv '^docs/')"
```

Expected output (`results` is the number of completion checks you actually ran this week, at least 1;
`cutover` is `DEFERRED` until L4 has stood the store up):

```
committed=1 placeholders=0 results=1 fresh=FRESH cutover=DEFERRED foreign=0
```

**STOP rule** — if `placeholders` is non-zero, do not commit. A log entry with `<...>` in it is the reconstructed-from-
memory artifact §95.4 L8708 exists to prevent, and the activation checklist later *cites* these entries: *"a closure
decision references log entries, never memory."* If `results=0`, you ran no completion check this week — that is
allowed, but write `result: NOT-RUN` against the check you expected to run rather than leaving Field 3 empty; an
empty field and a genuinely quiet week must not produce the same entry. If the cutover copy fails because
`control-plane-records` rejects the push, **do not** relax the ruleset: that repository's no-bypass ruleset blocking
force-push and delete is D107 (spec L10205) and is armed from day one — see §2's table, it is `no-review-gates`, not
`bootstrap`. Open `BLOCKER L0-06-08: records repository rejects the bootstrap-log write`.

---

### L0-06-09 — Threshold `T2W`: execute the activation checklist for real, negative tests included

**Size:** L · **Dependencies:** L0-06-05, L0-06-07

§95.4 L8699, binding: *"Each gate arms as headcount allows. The checklist is executed for real — including the
negative tests — at each threshold, not assumed."* §98.2 L9024 says the same of the Phase 1 completion check:
*"an approval from a Read-only account does **not** satisfy branch protection while an approval from a Write-holding
Cross-Reviewer does (executed for real once headcount permits, per the activation checklist)"*.

**Trigger:** a second human holds Write on a bootstrap-mode repository. **Gates armed:** rows 5 and 6 of
`arming-matrix.tsv` — the Code-Owner-and-approval gate. **Exceptions closed:** `EXC-BOOT-001`, `EXC-BOOT-002`,
`EXC-BOOT-003`, `EXC-BOOT-012` (every row whose `threshold` is `T2W`).

**Order, and it is D101's order.** The Team grant must already be in place — step 2 of `arming-order.md` — before
row 5 is flipped. Verify it first; do not assume it from week one.

**Commands**

```bash
cd "$CP_ROOT"
export REPO="$ORG/control-plane"
D=$(date -u +%F)

# --- Step A. Prove the predecessor step: a Team grants Write. (D101, spec L10194) ---
gh api "repos/$REPO/teams" --jq '.[] | [.slug, .permission] | @tsv'
gh api "repos/$REPO/collaborators?affiliation=direct" --jq '.[] | [.login, .permissions.push] | @tsv'

# --- Step B. Negative test 1 — a self-approved PR fails branch protection. ---
git checkout -b l0/t2w-negative-selfapprove
printf 'T2W activation probe %s\n' "$D" > docs/bootstrap/activation/.probe
git add docs/bootstrap/activation/.probe
git commit -m "L0-06-09: T2W activation probe"
git push -u origin l0/t2w-negative-selfapprove
PR=$(gh pr create --base integration --head l0/t2w-negative-selfapprove \
      --title "L0-06-09 T2W activation probe" --body "Negative test. Do not merge." \
      --json number --jq .number 2>/dev/null || gh pr list --head l0/t2w-negative-selfapprove --json number --jq '.[0].number')
echo "PR=$PR"
gh pr review "$PR" --approve || echo "SELF-APPROVAL-REFUSED"
gh pr view "$PR" --json reviewDecision  --jq .reviewDecision      # expect REVIEW_REQUIRED
gh pr view "$PR" --json mergeStateStatus --jq .mergeStateStatus   # expect BLOCKED

# --- Step C. Negative test 2 — a Read-only approval does not satisfy the gate. ---
# The Read-only account approves the PR, then:
gh pr view "$PR" --json reviewDecision  --jq .reviewDecision      # expect REVIEW_REQUIRED (unchanged)
gh pr view "$PR" --json mergeStateStatus --jq .mergeStateStatus   # expect BLOCKED (unchanged)

# --- Step D. Positive test — a Write-holding cross-reviewer approval does satisfy it. ---
# The second human with Write approves the PR, then:
gh pr view "$PR" --json reviewDecision  --jq .reviewDecision      # expect APPROVED
gh pr view "$PR" --json mergeStateStatus --jq .mergeStateStatus   # expect CLEAN

# --- Step E. Record the evidence BEFORE arming anything. ---
cat > "docs/bootstrap/activation/T2W-$D.md" <<EOF
# ACTIVATION CHECKLIST — threshold T2W — $D

Checklist row, MasterSpec v4.0 Section 95.4 (spec L8703), verbatim:
  headcount: 2 humans with Write
  gates armed: No self-approval; Gate 2 independent review; most-recent-push approval
  verification: A self-approved PR fails branch protection; a Read-only approval does not
                satisfy it; a Write-holding cross-reviewer approval does

Executed for real (Section 95.4 L8699). Probe pull request: #$PR on $REPO

## Predecessor step — D101 arming order, step 2 (spec L10194, Section 98.2 L9017)
Teams granting Write, observed:      <paste the gh api teams output>
Second human with Write, observed:   <login>
Teams grant Write BEFORE protection is armed: <YES — required; if NO, STOP>

## Negative test 1 — self-approval
command: gh pr review #$PR --approve  (as the PR author)
observed: <paste — either the API refusal, or reviewDecision REVIEW_REQUIRED>
mergeStateStatus: <paste — expected BLOCKED>
verdict: <FAILS-AS-REQUIRED | GATE-NOT-HOLDING>

## Negative test 2 — Read-only approval
approver: <login>, permission Read
observed reviewDecision: <paste — expected REVIEW_REQUIRED>
observed mergeStateStatus: <paste — expected BLOCKED>
verdict: <FAILS-AS-REQUIRED | GATE-NOT-HOLDING>

## Positive test — Write-holding cross-reviewer approval
approver: <login>, permission Write, Code Owner for the touched path
observed reviewDecision: <paste — expected APPROVED>
observed mergeStateStatus: <paste — expected CLEAN>
verdict: <SATISFIES | DOES-NOT-SATISFY>

## Arming performed (arming-matrix.tsv rows 5 and 6, executed by L5's apply runbook)
required_approving_review_count: 0 -> 1
require_code_owner_review:       inert -> true
runbook: access/runbooks/ (L5-01-12), executed by <who> at <time UTC>

## Exceptions closed by this threshold
EXC-BOOT-001, EXC-BOOT-002, EXC-BOOT-003, EXC-BOOT-012 — closed as trigger_satisfied by L0-06-11,
referencing this file and the weekly bootstrap log entries for the period.
EOF
"${EDITOR:-vi}" "docs/bootstrap/activation/T2W-$D.md"

# --- Step F. Clean up the probe. The evidence file is the record, not the branch. ---
gh pr close "$PR" --delete-branch
git checkout integration
git add "docs/bootstrap/activation/T2W-$D.md"
git commit -m "L0-06-09: T2W activation checklist executed for real"
git push origin integration
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | The predecessor step is proved, not assumed | `grep -c 'Teams grant Write BEFORE protection is armed: YES' "docs/bootstrap/activation/T2W-$(date -u +%F).md"` | `1` |
| 2 | Both negative tests recorded a verdict | `grep -c '^verdict: FAILS-AS-REQUIRED$' "docs/bootstrap/activation/T2W-$(date -u +%F).md"` | `2` |
| 3 | The positive test recorded a verdict | `grep -c '^verdict: SATISFIES$' "docs/bootstrap/activation/T2W-$(date -u +%F).md"` | `1` |
| 4 | No placeholder survives | `grep -c '<' "docs/bootstrap/activation/T2W-$(date -u +%F).md"` | `0` |
| 5 | The probe branch is gone | `git ls-remote --heads origin l0/t2w-negative-selfapprove \| wc -l` | `0` |
| 6 | The arming actually happened | `gh api "repos/$ORG/control-plane/branches/$(gh api repos/$ORG/control-plane --jq .default_branch)/protection" --jq '.required_pull_request_reviews.required_approving_review_count'` | `1` |
| 7 | Code-Owner review is now required | `gh api "repos/$ORG/control-plane/branches/$(gh api repos/$ORG/control-plane --jq .default_branch)/protection" --jq '.required_pull_request_reviews.require_code_owner_reviews'` | `true` |
| 8 | The four `T2W` exceptions are still open at this point (T11 closes them) | `awk -F'\t' '$2=="T2W" && $12=="-"' docs/bootstrap/gate-register.tsv \| wc -l` | `4` |

**SELF-VERIFY**

```bash
cd "$CP_ROOT"
E="docs/bootstrap/activation/T2W-$(date -u +%F).md"
DEF=$(gh api "repos/$ORG/control-plane" --jq .default_branch)
printf 'predecessor=%s negatives=%s positive=%s placeholders=%s probe=%s count=%s codeowner=%s open_t2w=%s\n' \
  "$(grep -c 'Teams grant Write BEFORE protection is armed: YES' "$E")" \
  "$(grep -c '^verdict: FAILS-AS-REQUIRED$' "$E")" \
  "$(grep -c '^verdict: SATISFIES$' "$E")" \
  "$(grep -c '<' "$E")" \
  "$(git ls-remote --heads origin l0/t2w-negative-selfapprove | wc -l | tr -d ' ')" \
  "$(gh api "repos/$ORG/control-plane/branches/$DEF/protection" --jq '.required_pull_request_reviews.required_approving_review_count')" \
  "$(gh api "repos/$ORG/control-plane/branches/$DEF/protection" --jq '.required_pull_request_reviews.require_code_owner_reviews')" \
  "$(awk -F'\t' '$2=="T2W" && $12=="-"' docs/bootstrap/gate-register.tsv | wc -l | tr -d ' ')"
```

Expected output, exactly:

```
predecessor=1 negatives=2 positive=1 placeholders=0 probe=0 count=1 codeowner=true open_t2w=4
```

**STOP rule** — if the predecessor line is anything other than `YES`, **do not arm.** You are about to reproduce the
exact defect D101 corrects (spec L10194) and §98.2 L9017 names: a Code-Owner-and-approval gate with no Team granting
Write, and *"a team that experiences its merges mysteriously breaking"*. Arm nothing; execute
`arming-order.md` step 2 first, through L5's runbook, and re-run this task. If either negative prints
`GATE-NOT-HOLDING`, **do not close any exception and do not record the threshold as reached.** A gate that admits a
self-approval or a Read-only approval is §95.1 L8640's *"gate that appears to be working and is not"*, and closing an
exception against it would replace a declared relaxation with an undeclared one — strictly worse than bootstrap.
Open `BLOCKER L0-06-09: T2W negative test did not fail` and route the protection fix to L5 (`access/**`); L0 does
not edit branch protection payloads.

---

### L0-06-10 — Thresholds `T3H`, `TQA`, `T4P`: the same procedure, three more times

**Size:** L · **Dependencies:** L0-06-09

Same shape as T09, three more times, with the verification column of §95.4 (spec L8704–L8706) transcribed verbatim
into each evidence file. Nothing here is a new procedure; only the tests differ.

| Threshold | Trigger | Gates armed (§95.4) | The tests, verbatim | Exceptions closed |
|---|---|---|---|---|
| `T3H` | 3 humans | Production approver ≠ deploying actor; cross-review matrix with real routing | *"A deploy attempted by its approver is rejected; the review-routing table resolves to a person who is not the author"* | `EXC-BOOT-004`, `EXC-BOOT-005` |
| `TQA` | QA role filled | Independent verification authority; release readiness sign-off; UAT ownership | *"A release blocked by QA stays blocked; verification contracts reviewed and owned by QA"* | `EXC-BOOT-006`, `EXC-BOOT-007`, `EXC-BOOT-008` |
| `T4P` | 4+ humans | Backup Owner coverage; knowledge-redundancy floor; responder rotation | *"Orphan detection reports zero blocking orphans; every product has a non-author reviewer and a backup"* | `EXC-BOOT-009`, `EXC-BOOT-010`, `EXC-BOOT-011` |

**Commands**

```bash
cd "$CP_ROOT"
D=$(date -u +%F)
THR=T3H     # set to T3H, TQA or T4P — run this task once per threshold

# The checklist row is copied out of the register, not retyped.
awk -F'\t' -v t="$THR" '!/^#/ && $1==t {printf "headcount: %s\ngates armed: %s\nverification: %s\nspec: %s\n", $2, $3, $4, $6}' \
  docs/bootstrap/activation-checklist.tsv | tee /tmp/row.txt

{
  printf '# ACTIVATION CHECKLIST — threshold %s — %s\n\n' "$THR" "$D"
  printf 'Checklist row, MasterSpec v4.0 Section 95.4, transcribed from docs/bootstrap/activation-checklist.tsv:\n\n'
  sed 's/^/  /' /tmp/row.txt
  printf '\nExecuted for real (Section 95.4 L8699), including the negative tests.\n\n'
  printf '## Predecessor step\n'
  printf 'arming-order.md step satisfied: <step number and its evidence>\n\n'
  printf '## Negative test 1\n'
  printf 'command: <the exact command run>\n'
  printf 'observed: <paste the literal output>\n'
  printf 'verdict: <FAILS-AS-REQUIRED | GATE-NOT-HOLDING>\n\n'
  printf '## Negative test 2\n'
  printf 'command: <the exact command run>\n'
  printf 'observed: <paste the literal output>\n'
  printf 'verdict: <FAILS-AS-REQUIRED | GATE-NOT-HOLDING>\n\n'
  printf '## Positive test\n'
  printf 'command: <the exact command run>\n'
  printf 'observed: <paste the literal output>\n'
  printf 'verdict: <SATISFIES | DOES-NOT-SATISFY>\n\n'
  printf '## Arming performed\n'
  printf 'arming-matrix.tsv row(s): <n>\n'
  printf 'runbook: access/runbooks/ (L5-01-12), executed by <who> at <time UTC>\n\n'
  printf '## Exceptions closed by this threshold\n'
  awk -F'\t' -v t="$THR" '!/^#/ && $2==t {printf "%s  %s\n", $1, $3}' docs/bootstrap/gate-register.tsv
  printf '\nClosed by L0-06-11 as trigger_satisfied, referencing this file and the weekly log entries.\n'
} > "docs/bootstrap/activation/$THR-$D.md"
"${EDITOR:-vi}" "docs/bootstrap/activation/$THR-$D.md"

git add "docs/bootstrap/activation/$THR-$D.md"
git commit -m "L0-06-10: $THR activation checklist executed for real"
git push origin integration
```

**The tests, spelled out per threshold so nothing is invented at the keyboard.**

**Commands**

```bash
# ---- T3H, negative 1: a deploy attempted by its approver is rejected (Section 27.2 L2571) ----
# The person who recorded the production approval triggers the deploy. The workflow-identity gate
# must fail closed. Expected: the deploy job concludes 'failure' with the identity check as the
# failing step, and no environment secret is issued.
gh run list --workflow deploy-production.yml --limit 1 --json conclusion,databaseId --jq '.[0]'
gh run view <id> --log | grep -i 'approver\|identity\|self'      # paste into the evidence file

# ---- T3H, negative 2: the routing table resolves to someone who is not the author ----
# Run the reviewer-matrix resolution for a change authored by <login>; the result must differ.
python -m validators.registry.cli resolve-reviewer --product <product> --author <login>

# ---- TQA, negative 1: a release blocked by QA stays blocked ----
# QA sets the release-readiness state to blocked; attempt the release; it must not proceed.
gh run list --workflow release.yml --limit 1 --json conclusion --jq '.[0].conclusion'   # expect failure

# ---- T4P, negative 1: orphan detection reports zero blocking orphans ----
python -m reconciler.cli orphans --severity blocking --format count    # expect 0
```

**Acceptance criteria** (run once per threshold, with `THR` set)

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | The evidence file exists for the threshold | `test -f "docs/bootstrap/activation/$THR-$(date -u +%F).md" && echo PRESENT` | `PRESENT` |
| 2 | The checklist row was copied, not retyped | `grep -c "$(awk -F'\t' -v t=$THR '$1==t{print $4}' docs/bootstrap/activation-checklist.tsv \| cut -c1-40)" "docs/bootstrap/activation/$THR-$(date -u +%F).md"` | `1` |
| 3 | Two negatives and one positive carry verdicts | `grep -c '^verdict: ' "docs/bootstrap/activation/$THR-$(date -u +%F).md"` | `3` |
| 4 | No negative reports `GATE-NOT-HOLDING` | `grep -c 'GATE-NOT-HOLDING' "docs/bootstrap/activation/$THR-$(date -u +%F).md"` | `0` |
| 5 | No placeholder survives | `grep -c '<' "docs/bootstrap/activation/$THR-$(date -u +%F).md"` | `0` |
| 6 | Every exception at this threshold is listed | `grep -c '^EXC-BOOT-' "docs/bootstrap/activation/$THR-$(date -u +%F).md"` | `2` for `T3H`, `3` for `TQA`, `3` for `T4P` |
| 7 | All four thresholds have evidence once the programme reaches 4+ humans | `ls docs/bootstrap/activation/T2W-*.md docs/bootstrap/activation/T3H-*.md docs/bootstrap/activation/TQA-*.md docs/bootstrap/activation/T4P-*.md 2>/dev/null \| wc -l` | `4` |

**SELF-VERIFY**

```bash
cd "$CP_ROOT"
E="docs/bootstrap/activation/$THR-$(date -u +%F).md"
printf 'file=%s verdicts=%s notholding=%s placeholders=%s exceptions=%s thresholds_done=%s\n' \
  "$(test -f "$E" && echo PRESENT || echo MISSING)" \
  "$(grep -c '^verdict: ' "$E")" \
  "$(grep -c 'GATE-NOT-HOLDING' "$E")" \
  "$(grep -c '<' "$E")" \
  "$(grep -c '^EXC-BOOT-' "$E")" \
  "$(ls docs/bootstrap/activation/T2W-*.md docs/bootstrap/activation/T3H-*.md docs/bootstrap/activation/TQA-*.md docs/bootstrap/activation/T4P-*.md 2>/dev/null | wc -l | tr -d ' ')"
```

Expected output for `THR=T3H`, exactly (`thresholds_done` grows to `4` as the later thresholds are reached):

```
file=PRESENT verdicts=3 notholding=0 placeholders=0 exceptions=2 thresholds_done=2
```

**STOP rule** — if `notholding` is non-zero, the threshold is **not** reached, whatever the headcount says. §95.4
L8699 makes the checklist the test, not the headcount: *"The checklist is executed for real — including the negative
tests — at each threshold, not assumed."* Do not close the exception, do not arm the gate, and record the failure in
this week's bootstrap log Field 3 with `result: FAIL`. If you cannot run one of the negative tests because the
subject system does not exist yet — no production deploy workflow at `T3H`, no verification contract at `TQA` — that
is not a pass: record `result: NOT-RUN`, leave the exception open, and note the phase that must land first. An
untested gate closes no exception, because §95.4 L8712 states the closing rule: *"Closing a bootstrap exception is a
recorded decision referencing the verification evidence."*

---

### L0-06-11 — Close a bootstrap exception as `trigger_satisfied`, by recorded decision

**Size:** M · **Dependencies:** L0-06-09

§95.4 L8712: *"Closing a bootstrap exception is a recorded decision referencing the verification evidence."* §54.2
L4796: *"Exception records are never deleted. They close with an outcome … `trigger_satisfied` is available only to
types that declare a `deactivation_trigger` — `bootstrap` and `founder_standing_delegation_activation` — and it
records that the stated precondition was met, which `remediated` does not, because nothing was remediated."*

So: the record stays, the closure is `trigger_satisfied`, and a decision file cites the evidence.

**Commands**

```bash
cd "$CP_ROOT"
D=$(date -u +%F)
THR=T2W
EVIDENCE="docs/bootstrap/activation/$THR-$D.md"
test -f "$EVIDENCE" || { echo "NO-EVIDENCE — run L0-06-09 first"; exit 1; }

# 1. The decision record, one file, citing the evidence and the log entries. (master/08 Section 8.3)
IDS=$(awk -F'\t' -v t="$THR" '!/^#/ && $2==t {printf "%s ", $1}' docs/bootstrap/gate-register.tsv)
cat > "docs/plan/decisions/${D}-close-bootstrap-${THR}.md" <<EOF
# DECISION — close bootstrap exceptions at threshold $THR — $D

decision_id: L0D-19
exceptions: [$(echo "$IDS" | sed 's/ $//; s/ /, /g')]
outcome: trigger_satisfied
deactivation_trigger_met: |
  $(awk -F'\t' -v t="$THR" '!/^#/ && $2==t {print $7; exit}' docs/bootstrap/gate-register.tsv)
verification_evidence: |
  $EVIDENCE — the Section 95.4 checklist executed for real, negative tests included.
  Weekly bootstrap log entries for the period: $(ls docs/plan/bootstrap-log/*.md | tail -4 | tr '\n' ' ')
authority: |
  Section 54.3 (spec L4814) maps exception type bootstrap to the exceptional-approval capability.
  Section 95.4 (spec L8712): closing a bootstrap exception is a recorded decision referencing the
  verification evidence. Section 54.2 (spec L4796): records are never deleted; they close with an
  outcome, and trigger_satisfied is available to type bootstrap.
gates_now_armed: |
  $(awk -F'\t' -v t="$THR" '!/^#/ && $5==t {printf "%s: %s -> %s\n  ", $2, $3, $4}' docs/bootstrap/arming-matrix.tsv)
EOF

# 2. Close the rows in the register. The record is not deleted; it gains an outcome.
cp docs/bootstrap/gate-register.tsv /tmp/gr.work
awk -F'\t' -v OFS='\t' -v t="$THR" -v d="$D" '!/^#/ && $2==t {$12="trigger_satisfied"; $13=d} 1' \
  /tmp/gr.work > docs/bootstrap/gate-register.tsv
rm -f /tmp/gr.work

# 3. Re-render and re-check.
make bootstrap-render
make bootstrap-check

# 4. The closure appears in this week's log Field 2 automatically, from the git history.
make bootstrap-log

git add docs/bootstrap/gate-register.tsv docs/bootstrap/exceptions \
        "docs/plan/decisions/${D}-close-bootstrap-${THR}.md" "docs/plan/bootstrap-log/$D.md"
git commit -m "L0-06-11: close $THR bootstrap exceptions as trigger_satisfied (L0D-19)"
git push origin integration
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Every `T2W` row is closed | `awk -F'\t' '$2=="T2W" && $12!="trigger_satisfied"' docs/bootstrap/gate-register.tsv \| wc -l` | `0` |
| 2 | Every closed row carries a closure date | `awk -F'\t' '$12!="-" && $13 !~ /^[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]$/' docs/bootstrap/gate-register.tsv \| wc -l` | `0` |
| 3 | No record was deleted (§54.2 L4796) | `grep -vc '^#' docs/bootstrap/gate-register.tsv` | `13` |
| 4 | The rendered records show the closure | `grep -c '^  closure: trigger_satisfied$' docs/bootstrap/exceptions/*.yaml \| grep -c ':1$'` | `4` |
| 5 | The decision file cites the evidence file | `grep -c "docs/bootstrap/activation/T2W-" "docs/plan/decisions/$(date -u +%F)-close-bootstrap-T2W.md"` | `1` |
| 6 | The decision file names the outcome the type allows | `grep -c '^outcome: trigger_satisfied$' "docs/plan/decisions/$(date -u +%F)-close-bootstrap-T2W.md"` | `1` |
| 7 | The checker still passes | `make bootstrap-check \| tail -1` | `BOOTSTRAP-CHECK OK` |

**SELF-VERIFY**

```bash
cd "$CP_ROOT"
DEC="docs/plan/decisions/$(date -u +%F)-close-bootstrap-T2W.md"
printf 'open_t2w=%s bad_dates=%s rows=%s closed_records=%s cites=%s outcome=%s check=%s\n' \
  "$(awk -F'\t' '$2=="T2W" && $12!="trigger_satisfied"' docs/bootstrap/gate-register.tsv | wc -l | tr -d ' ')" \
  "$(awk -F'\t' '$12!="-" && $13 !~ /^[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]$/' docs/bootstrap/gate-register.tsv | grep -vc '^#')" \
  "$(grep -vc '^#' docs/bootstrap/gate-register.tsv)" \
  "$(grep -l '^  closure: trigger_satisfied$' docs/bootstrap/exceptions/*.yaml | wc -l | tr -d ' ')" \
  "$(grep -c 'docs/bootstrap/activation/T2W-' "$DEC")" \
  "$(sed -n 's/^outcome: //p' "$DEC")" \
  "$(make bootstrap-check | tail -1)"
```

Expected output, exactly:

```
open_t2w=0 bad_dates=0 rows=13 closed_records=4 cites=1 outcome=trigger_satisfied check=BOOTSTRAP-CHECK OK
```

**STOP rule** — if `rows` is anything other than `13`, a record was deleted. §54.2 L4796 is absolute:
*"Exception records are never deleted."* Restore it from git (`git checkout HEAD~1 -- docs/bootstrap/gate-register.tsv`)
and close it properly. If you are tempted to close an exception with outcome `remediated`, do not: §54.2 L4796 says
`trigger_satisfied` *"records that the stated precondition was met, which `remediated` does not, because nothing was
remediated"* — headcount arrived; no defect was repaired. If the deactivation trigger has **not** actually fired and
you are closing because the expiry is near, that is not a closure — go to L0-06-12, which is the renewal path, and
note that §95.4 L8712 makes an unclosed expiry a Red signal precisely so that this shortcut is visible rather than
convenient.

---

### L0-06-12 — Renewal, the third-renewal re-affirmation branch, and the SIG-39 unclosed sweep

**Size:** M · **Dependencies:** L0-06-03, L0-06-07

Three rules from §54.2, and one signal.

* **Renewal is visible and rate-limited** (spec L4791): *"A second renewal raises Amber. A third renewal raises Red
  and forces one of three outcomes at the next quarterly review: remediate; promote to a policy with an owner and a
  review date; or … **re-affirm by recorded Founder decision** naming the unmet precondition, the compensating
  controls now in force and the next review date. The third branch is available only to exception types whose
  `deactivation_trigger` is declared non-discretionary — `bootstrap` and `founder_standing_delegation_activation`."*
* **Same scope, new id, still a renewal** (spec L4794; invariant 77, spec L9554). The checker's `SCOPE-DUPLICATE`
  rule is what makes the fresh-id dodge impossible here.
* **An unknowable end date is bounded, not omitted** (spec L4798). Bootstrap's closing condition is headcount, so the
  renewal *is* the pressure — §54.5 L8828: *"at a third renewal they take the re-affirmation branch of Section 54.2,
  because their closing condition is headcount — a precondition, not work the owner could perform."*
* **SIG-39** (spec L4568): *"Bootstrap exception unclosed | A bootstrap-mode exception (Section 95) past its expiry
  with its gate still unarmed | Exception registry | Red | Founder"*. **AT-039** (spec L9361) is the acceptance test.

**Commands**

```bash
cd "$CP_ROOT"
D=$(date -u +%F)

# --- A. The weekly sweep. Run every Friday, before the log entry. ---
make bootstrap-check            # SIG-39 rows surface as BOOTSTRAP-VIOLATION [SIG-39]
awk -F'\t' -v d="$D" '!/^#/ && $12=="-" && $9 < d {printf "SIG-39 %s %s expired %s\n", $1, $3, $9}' \
  docs/bootstrap/gate-register.tsv
awk -F'\t' -v d="$D" '!/^#/ && $12=="-" && $10 <= d {printf "REVIEW-DUE %s %s review_date %s\n", $1, $3, $10}' \
  docs/bootstrap/gate-register.tsv

# --- B. Renew one exception. The trigger has not fired; the expiry has arrived. ---
ID=EXC-BOOT-001
OLDR=$(awk -F'\t' -v i="$ID" '$1==i{print $11}' docs/bootstrap/gate-register.tsv)
NEWR=$((OLDR + 1))
NEWE=$(date -u -d "$(awk -F'\t' -v i="$ID" '$1==i{print $9}' docs/bootstrap/gate-register.tsv) +91 days" +%F)
NEWV=$(date -u -d "$NEWE -30 days" +%F)
echo "renewing $ID: renewals $OLDR -> $NEWR, expiry -> $NEWE, review_date -> $NEWV"

cat > "docs/plan/decisions/${D}-renew-${ID}.md" <<EOF
# DECISION — renew bootstrap exception $ID — $D

decision_id: L0D-19
exception: $ID
renewals: $OLDR -> $NEWR
expiry: -> $NEWE
review_date: -> $NEWV
band: $( [ "$NEWR" -ge 3 ] && echo "RED — third renewal (Section 54.2 L4791)" || { [ "$NEWR" -ge 2 ] && echo "AMBER — second renewal (Section 54.2 L4791)" || echo "none"; } )
unmet_precondition: |
  $(awk -F'\t' -v i="$ID" '$1==i{print $7}' docs/bootstrap/gate-register.tsv)
compensating_controls_now_in_force: |
  <state them; Section 54.2 L4791 requires each re-affirmation to RAISE this bar>
next_review_date: $NEWV
basis: |
  Section 54.2 (spec L4797): an unknowable end date is bounded, not omitted; renewal is the
  pressure that is wanted. Section 54.5 (spec L8828): bootstrap exceptions take the
  re-affirmation branch at a third renewal because their closing condition is headcount.
EOF

cp docs/bootstrap/gate-register.tsv /tmp/gr.work
awk -F'\t' -v OFS='\t' -v i="$ID" -v r="$NEWR" -v e="$NEWE" -v v="$NEWV" \
  '!/^#/ && $1==i {$9=e; $10=v; $11=r} 1' /tmp/gr.work > docs/bootstrap/gate-register.tsv
rm -f /tmp/gr.work

# --- C. Third renewal: the re-affirmation record the checker requires. ---
if [ "$NEWR" -ge 3 ]; then
  cp "docs/plan/decisions/${D}-renew-${ID}.md" "docs/plan/decisions/${D}-reaffirm-${ID}.md"
  "${EDITOR:-vi}" "docs/plan/decisions/${D}-reaffirm-${ID}.md"
fi

make bootstrap-render
make bootstrap-check
make bootstrap-log

git add docs/bootstrap/gate-register.tsv docs/bootstrap/exceptions docs/plan/decisions "docs/plan/bootstrap-log/$D.md"
git commit -m "L0-06-12: renew $ID (renewals=$NEWR) with the recorded decision (L0D-19)"
git push origin integration
```

**The renewal-band self-test — run it once, at T12, and never assume it.**

**Commands**

```bash
cd "$CP_ROOT"
cp docs/bootstrap/gate-register.tsv /tmp/gr.bak

# Third renewal with no re-affirmation record must be a violation (Section 54.2 L4791).
rm -f docs/plan/decisions/*reaffirm-EXC-BOOT-002.md
awk -F'\t' -v OFS='\t' '$1=="EXC-BOOT-002"{$11=3}1' /tmp/gr.bak > docs/bootstrap/gate-register.tsv
make bootstrap-render >/dev/null
make bootstrap-check | grep -c 'REAFFIRM'                     # expect 1

# An expiry in the past with the gate unarmed must raise SIG-39 (spec L4568; AT-039 L9361).
awk -F'\t' -v OFS='\t' '$1=="EXC-BOOT-002"{$9="2000-01-01"; $11=0}1' /tmp/gr.bak > docs/bootstrap/gate-register.tsv
make bootstrap-render >/dev/null
make bootstrap-check | grep -c 'SIG-39'                       # expect 1

cp /tmp/gr.bak docs/bootstrap/gate-register.tsv
make bootstrap-render >/dev/null
make bootstrap-check | tail -1                                # expect BOOTSTRAP-CHECK OK
git checkout -- docs/bootstrap
rm -f /tmp/gr.bak
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | No open exception is past its expiry | `awk -F'\t' -v d="$(date -u +%F)" '!/^#/ && $12=="-" && $9 < d' docs/bootstrap/gate-register.tsv \| wc -l` | `0` |
| 2 | A renewal produced a decision file | `ls docs/plan/decisions/*-renew-EXC-BOOT-*.md \| wc -l` | at least `1` |
| 3 | Every open exception with `renewals >= 3` has a re-affirmation record | `for i in $(awk -F'\t' '!/^#/ && $12=="-" && $11>=3{print $1}' docs/bootstrap/gate-register.tsv); do ls docs/plan/decisions/*reaffirm-$i.md >/dev/null 2>&1 \|\| echo "MISSING $i"; done; echo DONE` | `DONE` alone |
| 4 | The third-renewal rule is enforced, not asserted | the `grep -c 'REAFFIRM'` self-test above | `1` |
| 5 | SIG-39 fires on a past expiry | the `grep -c 'SIG-39'` self-test above | `1` |
| 6 | No scope was re-opened under a new id | `awk -F'\t' '!/^#/{print $3}' docs/bootstrap/gate-register.tsv \| sort \| uniq -d \| wc -l` | `0` |
| 7 | The checker passes on the committed tree | `make bootstrap-check \| tail -1` | `BOOTSTRAP-CHECK OK` |

**SELF-VERIFY**

```bash
cd "$CP_ROOT"
printf 'expired_open=%s renewals_recorded=%s missing_reaffirm=%s dupscope=%s check=%s\n' \
  "$(awk -F'\t' -v d="$(date -u +%F)" '!/^#/ && $12=="-" && $9 < d' docs/bootstrap/gate-register.tsv | wc -l | tr -d ' ')" \
  "$(ls docs/plan/decisions/*-renew-EXC-BOOT-*.md 2>/dev/null | wc -l | tr -d ' ')" \
  "$(for i in $(awk -F'\t' '!/^#/ && $12=="-" && $11>=3{print $1}' docs/bootstrap/gate-register.tsv); do ls docs/plan/decisions/*reaffirm-$i.md >/dev/null 2>&1 || echo x; done | wc -l | tr -d ' ')" \
  "$(awk -F'\t' '!/^#/{print $3}' docs/bootstrap/gate-register.tsv | sort | uniq -d | wc -l | tr -d ' ')" \
  "$(make bootstrap-check | tail -1)"
```

Expected output, exactly (`renewals_recorded` is `1` after the first renewal and grows thereafter):

```
expired_open=0 renewals_recorded=1 missing_reaffirm=0 dupscope=0 check=BOOTSTRAP-CHECK OK
```

**STOP rule** — if `expired_open` is non-zero, that is **SIG-39, Red, owned by the Founder** (spec L4568), and it is
the failure §95.4 L8712 names: *"Any gate whose exception expires unclosed escalates to the Founder as a Red
operating-system health signal; stubbed gates have a habit of staying stubbed, and the expiry date exists precisely
to prevent that."* You may do exactly two things: close it under L0-06-11 if the trigger has fired, or renew it here
with a recorded decision. You may not extend an expiry without a decision file, you may not delete the row, and you
may not open a fresh id for the same scope — invariant 77 (spec L9554) makes that a renewal anyway and the checker's
`SCOPE-DUPLICATE` rule catches it. If `missing_reaffirm` is non-zero, §54.2 L4791 has been reached and not answered:
the exception is at Red, and the next quarterly review must remediate, promote to policy, or re-affirm. Promotion to
policy is **not** available here in the ordinary sense — §54.2 L4791 says so directly: *"neither is forcing a Founder
who cannot hire on demand to promote 'unreviewed changes reach the default branches' into standing policy, which is
the inversion Bootstrap Mode exists to prevent."*

---

## 8. Quick reference — one bootstrap week

**Commands**

```bash
cd "$CP_ROOT" && git checkout integration && git pull --ff-only

make bootstrap-check          # BOOTSTRAP-CHECK OK             [T04] — expiry/owner/trigger/SIG-39
make bootstrap-fresh          # BOOTSTRAP-LOG FRESH age=N       [T07] — Blocking past 7 days
make bootstrap-log            # writes docs/plan/bootstrap-log/<date>.md, two fields generated  [T07]
"${EDITOR:-vi}" "docs/plan/bootstrap-log/$(date -u +%F).md"   # Field 3 result lines + open items
git add docs/plan/bootstrap-log && git commit -m "bootstrap log $(date -u +%F)" && git push origin integration

# Friday sweep, in this order:
awk -F'\t' -v d="$(date -u +%F)" '!/^#/ && $12=="-" && $9 < d {print "SIG-39 " $1 " " $3}' docs/bootstrap/gate-register.tsv
awk -F'\t' -v d="$(date -u +%F)" '!/^#/ && $12=="-" && $10 <= d {print "REVIEW-DUE " $1 " " $3}' docs/bootstrap/gate-register.tsv
# expired  -> T11 close (trigger fired) or T12 renew (it has not). Never a silent extension.
# threshold reached -> T09 (T2W) / T10 (T3H, TQA, T4P): checklist EXECUTED, negatives included, then T11.
# arming   -> arming-matrix.tsv row flipped by L5's runbook, AFTER the D101 predecessor step is proved.
```

The four sentences worth keeping in the head, each quoted:

1. §95.1 L8642 — bootstrap is *"scoped **per repository**, never per company"*; product repositories *"run fully
   armed from day one, and never enter bootstrap"*.
2. §95.3 L8687 — *"Bootstrap relaxes independence requirements only."*
3. §95.2 L8680 — the armed configuration is *"recorded beside the unarmed one, so arming a gate is a configuration
   flip, not a build project"*.
4. D101 L10194 — *"Teams are derived and granted first"*, then branch protection.

---

## 9. What this file does not decide

| Matter | Owner |
|---|---|
| Opening, renewing or closing any bootstrap exception | **L0D-19**, this file; no lane, ever |
| The calibrated staleness window, exception lifetime and review offset | **L0D-17** (`L0-00-charter.md` §5.1); DECISION REQUIRED #3 |
| Where the rendered exception finally lands in `registries/exceptions.yaml` | **L0**; DECISION REQUIRED #1. `registries/**` is L1's exclusively (PARTITION.md line 17) |
| The compensating control for `EXC-BOOT-012` while `EXC-BOOT-001` is open | **L0**; DECISION REQUIRED #2 |
| The minimal `exceptions.yaml` schema validator and its rules | **L1** — `L1-05-tasks.md` L1-108; L0 executes the negative test, never the fix |
| The branch-protection payloads, the arming-order gate and the negative-test register | **L5** — `L5-01-org-and-access.md` T07, T10, T13 |
| The per-repository transition note template and generator (§95.4 L8710) | **L5** — `L5-01-org-and-access.md` T14; L0 authors the content and holds the same-day response commitment for the two weeks after protection lands |
| The `records/bootstrap-log/` store and the generator that supersedes the interim one | **L4** — `control-plane-records` is L4's entirely (PARTITION.md line 20) |
| The SIG-39 detector and the bootstrap-log Blocking-drift rule in CI | **L3** (`validators/drift/**`) and **L1** (`validators/registry/**`); `master/06-v1-scope.md` R-6 |
| Whether a repository is in bootstrap at all | **L0D-19**, from §95.1's test — fewer context-holding humans than gate independence requires. Never a roster reading by an executor |
| Adding a required status check to branch protection | Forbidden action **F-07** for every lane; the list starts empty and grows per phase (§98.2 L9018) |
| Any relaxation of a §95.3 item | Nobody. Bootstrap relaxes independence requirements only (spec L8687) |

Nothing in a lane PR description, a lane blocker issue, a lane comment or a lane's own plan file moves any row of
this table. A bootstrap exception is a declared, expiring, owned relaxation with a named trigger — and the moment it
becomes anything looser than that, it is the undocumented policy §54.2 L4789 says it is, and Bootstrap Mode has
become the thing it exists to prevent.
