# 09 — Cost and Context Discipline

**Audience:** you, the AI developer executing one task on one lane branch.
**Status:** binding. These rules are not advice. A task that violates them is rejected at review even if the code is correct.

---

## 9.0 The one-paragraph version

You are cheap and fast and you have no memory. That is the design, not a defect. The system compensates for it by handing you a task card that already contains everything you need. Your job is to read **the task card and the files you will touch — nothing else** — make the smallest change that satisfies the acceptance criteria, run the self-verify command, and report. You do not explore. You do not survey. You do not read the specification to "get oriented." If the task card is not sufficient, you **stop and escalate**; you never close the gap by reading more or by guessing.

---

## 9.1 The numbers you are working against

These are measured, not estimated. Run the commands yourself if you doubt them.

```bash
wc -l  "C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md"
wc -c  "C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md"
```

| Fact | Value |
|---|---|
| Specification length | **10,256 lines** |
| Specification size | **1,178,771 bytes (~1.2 MB)** |
| Approximate tokens if read in full | **~290,000** |
| Your context window | smaller than that |
| Sections in the spec | 104, plus Appendix A (the Decision Register) at line 10071 |
| Lanes running in parallel | 5 (L1–L5), plus L0 the integrator |

**Consequence:** reading the specification in full is not "expensive." It is **impossible**. An attempt to do it ends with a truncated, silently-incomplete view of the document, and every conclusion you draw from that view is unsound. This is the single most dangerous thing you can do on this build, because it fails without an error message.

---

## 9.2 Rule 0 — The context budget

Per task, you are budgeted:

| Budget line | Limit |
|---|---|
| Files opened for **reading** | **≤ 8** |
| Total lines read from all sources | **≤ 1,500** |
| Files **written or modified** | **1** (see §9.6 for the narrow exceptions) |
| Spec lines read | **≤ 150**, and only a cited region (§9.5) |
| Repository-wide searches | **≤ 3**, each with a path filter |

Check yourself before you read anything large:

```bash
# ALWAYS do this before opening a file you have not opened before.
# If it prints more than 400, do not open it whole — locate first (§9.4).
wc -l "<absolute/path/to/file>"
```

If you are about to exceed a budget line, that is not a reason to exceed it. It is the signal described in §9.9: **stop and escalate.**

---

## 9.3 What you are allowed to read

Exactly four categories. Nothing else.

1. **Your task card.** The prompt you were given. It is the authority. It contains the exact paths, the literal commands, the acceptance criteria, the self-verify command, and the STOP rule.
2. **The files your task card names as the files you will touch.**
3. **`contracts/**`** — but only the specific contract file your task card cites, and only to read. `contracts/**` is owned by L0 and is FROZEN. You never edit it (`PARTITION.md`, rule 2).
4. **One cited spec region**, and only when §9.5 permits it.

Everything else is out of bounds, including:

- the other lanes' source trees (`PARTITION.md`, rule 4: **no cross-lane imports**)
- `docs/**`, `CODEOWNERS`, `Makefile`, root files — L0 owns these
- the git history, other branches, other PRs
- "just checking how the neighbouring file does it"

**The path ownership table is in `C:/D_Drive/PS/MultiProduct/Code/implementation/PARTITION.md`.** If you cannot name your lane's owned path prefix from your task card, you have the wrong task card. Stop.

---

## 9.4 The read ladder — locate, bound, then read

Never open a file to find something. **Find it, bound it, then read only the bounded region.** Three rungs, in this order, always.

### Rung 1 — Prove the path exists before you use it

You are prone to inventing paths that look plausible. Kill that failure mode with a command, every time, before the path appears in any other command you run:

```bash
# Prints "EXISTS" or "MISSING: <path>". A MISSING result is a STOP condition (§9.9).
p="C:/D_Drive/PS/MultiProduct/Code/implementation/PARTITION.md"
[ -f "$p" ] && echo "EXISTS $p" || echo "MISSING: $p"
```

For a directory:

```bash
d="C:/D_Drive/PS/MultiProduct/Code/implementation/lanes"
[ -d "$d" ] && echo "EXISTS $d" || echo "MISSING: $d"
```

If a path your task card gave you is MISSING, **do not look for the file it probably meant.** Do not `find` for something with a similar name. Open a blocker (§9.10). A wrong path in a task card is a defect in the task card, and L0 fixes it — not you.

### Rung 2 — `grep -n` to locate

`grep -n` returns line numbers. Line numbers are what turn an unbounded read into a bounded one. Always `-n`.

```bash
# Locate a symbol inside ONE file. Cheap: prints only matching lines.
grep -n "^def load_registry_file" "C:/D_Drive/PS/MultiProduct/Code/implementation/validators/registry/loader.py"
```

```bash
# Locate across a lane's OWNED subtree only. Note the path argument — never bare "." .
grep -rn --include="*.sh" "emit_record" \
  "C:/D_Drive/PS/MultiProduct/Code/implementation/tools/records/lib/"
```

```bash
# Count first, read second. If this prints a big number, refine the pattern; do not read the hits.
grep -rc --include="*.json" "required" \
  "C:/D_Drive/PS/MultiProduct/Code/implementation/schemas/registry/" | grep -v ":0$"
```

```bash
# List only the FILES that match, with no content. Use this to decide which single file to open.
grep -rl --include="*.json" "capability" \
  "C:/D_Drive/PS/MultiProduct/Code/implementation/schemas/registry/"
```

### Rung 3 — `sed -n` to read the bounded region

```bash
# Read exactly the region you located. Substitute the real line numbers from Rung 2.
sed -n '105,157p' "C:/D_Drive/PS/MultiProduct/Code/implementation/validators/registry/loader.py"
```

```bash
# Read a match with 20 lines of context on each side, without opening the file.
f="C:/D_Drive/PS/MultiProduct/Code/implementation/validators/registry/loader.py"
grep -n -C 20 "def load_registry_file" "$f"
```

```bash
# Read just the head of a file to see its imports and module docstring.
sed -n '1,40p' "<absolute/path/to/file>"
```

```bash
# Read just the tail.
tail -n 40 "<absolute/path/to/file>"
```

### Banned reads

Do not run these. Each one is a budget breach and, on the spec, a silent-truncation trap.

```bash
set -euo pipefail
# BANNED — every one of these lines is a rejection at review.
cat  "C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md"
head -n 10256 "C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md"
grep -rn "config" .          # bare "." — searches the entire repository
find . -type f               # enumerating the repo is exploration, not work
ls -R "C:/D_Drive/PS/MultiProduct/Code/"
git log -p                   # unbounded history read
```

---

## 9.5 The specification: quoted first, cited second, never whole

**The task card quotes what you need.** The quote in your task card is the operative text. Work from it.

You may read the spec **only** when both of these are true:

1. Your task card cites a section (for example "§53.2" or "Section 97.1" or "Appendix A, D89"), **and**
2. the quoted excerpt in your card is genuinely insufficient to satisfy an acceptance criterion.

"I would like more background" is not insufficiency. Curiosity is not a permission.

When both conditions hold, read **only the cited region**, using one of the following. These are verified against the real file; copy them verbatim and change only the section number.

### Read exactly one numbered section (e.g. Section 53)

```bash
set -euo pipefail
SPEC="C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md"
S=53
start=$(grep -n "^## Section ${S}\." "$SPEC" | cut -d: -f1)
end=$(awk -v s="$start" 'NR>s && (/^## Section /||/^# Appendix/){print NR-1; found=1; exit} END{if (!found) print NR}' "$SPEC")
echo "Section ${S}: lines ${start}-${end} ($((end-start+1)) lines)"
sed -n "${start},${end}p" "$SPEC"
```

Before you print it, look at the reported line count. **If it is over 150 lines, do not print the whole section — read the subsection instead.**

### Read exactly one subsection (e.g. §53.2)

```bash
set -euo pipefail
SPEC="C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md"
SUB="53.2"
start=$(grep -n "^### ${SUB} " "$SPEC" | cut -d: -f1)
end=$(awk -v s="$start" 'NR>s && (/^#{2,3} /||/^# Appendix/){print NR-1; found=1; exit} END{if (!found) print NR}' "$SPEC")
echo "§${SUB}: lines ${start}-${end} ($((end-start+1)) lines)"
sed -n "${start},${end}p" "$SPEC"
```

### Look up one Decision Register entry (Appendix A)

The register is a table starting at line 10071. One decision is one row. Read the row, not the appendix.

```bash
set -euo pipefail
SPEC="C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md"
D="D89"
grep -n "^| ${D} " "$SPEC"
```

### Look up one numbered invariant (Section 101)

```bash
set -euo pipefail
SPEC="C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md"
N=47
grep -n "^${N}\. " "$SPEC" | head -1
```

### Find which section covers a term, without reading any of it

```bash
SPEC="C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md"
grep -n "^## Section " "$SPEC" | grep -i "reconcil"
```

### Size a region before you read it

```bash
SPEC="C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md"
sed -n '4649,4745p' "$SPEC" | wc -c   # bytes in the region — sanity-check before printing
```

**If the cited section does not answer your question:** that is a defect in the citation. Escalate (§9.10). Do not widen the read to the neighbouring sections, do not grep the whole spec for the concept, and above all do not decide the answer yourself.

---

## 9.6 The one-file rule

**Default task shape: one task changes one file.**

The partition is built to make this possible. From `PARTITION.md`, rule 3 — *No shared mutable file, ever. Directory-per-item only (one file per event, per record, per schema)* — and rule 5 — *Additive-only within a lane. Prefer new files over editing existing ones.*

So the normal, correct move is: **create one new file inside your lane's owned path.** Not edit three. Not refactor two and add one.

Permitted multi-file shapes, and only when the task card explicitly names every path:

| Shape | Allowed when |
|---|---|
| 1 source file + 1 test file | The card names both paths |
| 1 new file + 1 registration line in an owned index the card names | The card quotes the exact line to add and its exact location |

Anything beyond that: the card is wrong, or the task is too big. Escalate.

If you find yourself opening a fourth file with intent to edit it, you have already left your task. Stop mid-work and escalate — a half-done task honestly reported is recoverable; a scope-crept task quietly merged is not.

---

## 9.7 What a task is NOT allowed to grow into

This is the explicit list. It is not illustrative. **Each line below is a hard prohibition, and each is a STOP-and-escalate trigger, not a judgment call.**

A task is **NOT** allowed to grow into:

1. **A refactor.** You do not rename, restructure, extract, deduplicate, or "clean up" anything the task card did not name. Ugly code that works is out of scope.
2. **A second file's problem.** A bug, typo, or bad pattern you can see in an adjacent file is not yours. Report it in your completion note (§9.11); do not fix it.
3. **A cross-lane change.** If the fix lives in a path another lane owns, you are forbidden to touch it — CODEOWNERS and the lane-guard CI check will fail the PR anyway, and a foreign-path PR wastes a full review cycle. See `PARTITION.md`, rule 1: *One owner per path… No exceptions.*
4. **A contract change.** `contracts/**` is FROZEN and L0-owned. If your task cannot be done without changing a contract, you file a Contract Change Request and stop. You never edit `contracts/**` (`PARTITION.md`, rule 2).
5. **A design decision.** If the task requires choosing between two valid implementations, it is not your task. From `PARTITION.md`: *No task may require designing, choosing, or interpreting. If a task needs judgment, it belongs to L0.*
6. **A dependency addition.** No new package, module, action, or external service unless the task card names it and pins its version.
7. **A schema or interface change.** If satisfying the task changes a shape another lane consumes, stop. That is a contract-level event.
8. **A CI or workflow change** — unless you are L2 and `.github/workflows/**` is your task card's named path.
9. **A "while I'm here" test addition.** Add the tests the acceptance criteria require. Not more.
10. **A documentation sweep.** `docs/**` and root files are L0's. Do not update a README to match your change; note it instead.
11. **A migration, backfill, or data fix.** Never.
12. **An investigation.** "I could not make it work so I started reading the codebase to understand the system" is the failure this whole chapter exists to prevent. Time-box yourself to the budget in §9.2 and escalate.
13. **A second attempt at a different approach.** If the approach the card specifies does not work, the card is wrong. Escalate with the evidence. Do not substitute your own approach and report success.

**The rule behind all thirteen:** a task delivers exactly its acceptance criteria, or it delivers a blocker. There is no third outcome. Partial silent completion is the worst outcome available to you and is treated as a failed task, not a partial one.

---

## 9.8 Verification is not optional and is not inferable

You may not report a test as passing unless you ran the command and read its output in this session.

```bash
# Run the self-verify command EXACTLY as the task card gives it, then capture the exit code.
<paste the self-verify command from your task card here>
echo "EXIT_CODE=$?"
```

Rules:

- `EXIT_CODE=0` and the expected output present → PASS.
- Any other exit code, or missing/ambiguous output → **FAIL**. Report FAIL. Do not retry with a modified command to make it go green.
- If the self-verify command itself errors (command not found, path missing), that is a **blocker**, not a fail. Escalate with the literal error text.
- **Never** write "tests pass" from reasoning about the code. Never write it from a previous run before your last edit.
- Do not invent a verification command. If the card has no self-verify command, the card is incomplete — escalate.

---

## 9.9 Tripwires — stop the moment any of these fire

Stop working. Do not investigate. Escalate using §9.10.

| # | Tripwire |
|---|---|
| T1 | A path from the task card is MISSING (§9.4 Rung 1). |
| T2 | The task card is ambiguous, or two of its statements conflict. |
| T3 | Satisfying the acceptance criteria requires touching a path your lane does not own. |
| T4 | You need information that is neither quoted in the card nor in the cited spec region. |
| T5 | You have opened 8 files, or read 1,500 lines, and the task is not done. |
| T6 | The self-verify command does not exist, does not run, or its output is ambiguous. |
| T7 | You are about to choose between two reasonable implementations. |
| T8 | The change would require editing `contracts/**`, `CODEOWNERS`, `docs/**`, `Makefile`, or a root file. |
| T9 | You suspect another lane has already implemented this. |
| T10 | You are about to write "I assume", "probably", "it seems", or "should be" in your reasoning about what to build. |

**T10 deserves emphasis.** The moment you catch yourself guessing to resolve ambiguity, the guess is the defect — regardless of whether it happens to be right. Escalation costs one review cycle. A wrong guess merged into `integration` costs five lanes a merge train.

**Escalation taxonomy note (B3).** `T1`…`T10` are this file's own local names for the moment to stop — they are not a second escalation taxonomy. `manual/03-guardrails-and-stop-rules.md`'s `STOP-01`…`STOP-08` is the one canonical set of escalation categories every blocker files under, corpus-wide. When you escalate on a tripwire, the blocker you file (§9.10) additionally carries the matching `STOP-0N`:

| Tripwire | Files as (`manual/03`) |
|---|---|
| T1 | `STOP-02` if the missing path is under `contracts/**`; otherwise `STOP-01` |
| T2 | `STOP-01` — ambiguous or self-contradicting task spec |
| T3 | `STOP-03` — a file you do not own |
| T4 | `STOP-01` — the delivery (card + cited spec) is incomplete; there is no analogue for "go look elsewhere," because `manual/03` never permits that |
| T5 | No `manual/03` analogue — this is a file-local cost control, not an escalation category. Report it as `T5` alone |
| T6 | `STOP-05` if the command errors; `STOP-01` if it was never provided |
| T7 | `STOP-08` — a judgment call |
| T8 | `STOP-02` (a Contract Change Request, if the path is under `contracts/**`) or `STOP-03` (any other frozen/foreign path) |
| T9 | `STOP-06` — the task appears already done |
| T10 | `STOP-08` — you were about to make the judgment call yourself instead of asking |

Escalating is a **successful** outcome for you. It is cheaper than every alternative. You are not penalised for it, and you are penalised for the alternative.

---

## 9.10 Escalation templates — use verbatim

Copy one of these, fill only the bracketed fields, and post it as your task output. Change nothing else.

### Blocker: bad or missing path

```text
STATUS: BLOCKED
TASK: [task id from the card]
LANE: [L1|L2|L3|L4|L5]
BRANCH: [lane/N/phase-task]
TRIPWIRE: T1 — path from the task card does not exist.

The task card instructs me to modify:
  [exact path as written in the card]

Verification run:
  [ -f "[exact path]" ] && echo EXISTS || echo MISSING
Output:
  MISSING: [exact path]

I have not searched for a substitute path and I have not created the file.
I have made no edits. Working tree is clean.

REQUEST FOR L0: confirm the correct absolute path, or confirm the file is to be
created new. I will not proceed until one of those two is stated explicitly.
```

### Blocker: ambiguity — two readings of the card

```text
STATUS: BLOCKED
TASK: [task id from the card]
LANE: [L1|L2|L3|L4|L5]
BRANCH: [lane/N/phase-task]
TRIPWIRE: T2/T7 — the task admits two implementations and I have no authority to choose.

Card text in question, quoted exactly:
  "[verbatim quote from the task card]"

Reading A: [one sentence]
Reading B: [one sentence]
They differ in observable behaviour: [one sentence on how the acceptance criteria
or a consumer would see the difference].

Spec region I checked, if any: [§X.Y, lines N-M] — it does not disambiguate because
  [one sentence].

I have not chosen. I have made no edits. Working tree is clean.

REQUEST FOR L0: state A or B. I will implement the stated one and nothing else.
```

### Blocker: information gap — neither the card nor the cited spec region answers this

```text
STATUS: BLOCKED
TASK: [task id from the card]
LANE: [L1|L2|L3|L4|L5]
BRANCH: [lane/N/phase-task]
TRIPWIRE: T4 — required information is neither quoted in the card nor in the
cited spec region.

Information needed: [one sentence — the specific fact required to satisfy an
  acceptance criterion]
Card text checked, quoted exactly:
  "[verbatim quote from the task card]"
Spec region checked, if any: [§X.Y, lines N-M] — it does not supply this
  because: [one sentence].

I have not widened the read beyond the cited region and I have not guessed.
I have made no edits. Working tree is clean.

REQUEST FOR L0: supply the missing information, or cite the region that
contains it.
```

### Blocker: the change requires a foreign path

```text
STATUS: BLOCKED
TASK: [task id from the card]
LANE: [L1|L2|L3|L4|L5]
BRANCH: [lane/N/phase-task]
TRIPWIRE: T3/T8 — the acceptance criteria cannot be met inside my owned paths.

My lane owns: [owned path prefixes, copied from PARTITION.md]
The change also requires: [foreign path]
That path is owned by: [lane or L0, per PARTITION.md]

Per PARTITION.md rule 1 (one owner per path) I have not touched it, and per rule 4
I have not imported from it.

I have made no edits outside my owned paths. Work completed inside my lane so far:
  [either "none" or a one-line list of files created/modified]

REQUEST FOR L0: split this task, or file the cross-lane dependency. I am stopping here.
```

### Blocker: contract change required

```text
STATUS: BLOCKED — CONTRACT CHANGE REQUEST
TASK: [task id from the card]
LANE: [L1|L2|L3|L4|L5]
BRANCH: [lane/N/phase-task]
TRIPWIRE: T8 — cannot satisfy acceptance criteria without changing frozen contracts/**.

Contract file: [path under contracts/**]
Current shape, quoted exactly:
  [verbatim excerpt]
What the task requires instead:
  [one or two sentences, concrete]
Consumers this would affect, to my knowledge from the task card only:
  [list, or "unknown — I did not survey other lanes"]

Per PARTITION.md rule 2 I have not edited contracts/**. Working tree is clean.

REQUEST FOR L0: accept, amend, or reject this Contract Change Request.
```

### Blocker: self-verify command will not run

```text
STATUS: BLOCKED
TASK: [task id from the card]
LANE: [L1|L2|L3|L4|L5]
BRANCH: [lane/N/phase-task]
TRIPWIRE: T6 — the self-verify command from the card does not execute.

Command as given in the card, verbatim:
  [exact command]
Literal output:
  [paste the complete stderr/stdout, unedited]
Exit code: [n]

This is a card defect, not a test failure. I am NOT reporting the task as passing
and I have NOT substituted a different verification command.

Implementation state: [either "complete, unverified" or "not started"]

REQUEST FOR L0: supply a runnable self-verify command.
```

### Blocker: budget exhausted

```text
STATUS: BLOCKED
TASK: [task id from the card]
LANE: [L1|L2|L3|L4|L5]
BRANCH: [lane/N/phase-task]
TRIPWIRE: T5 — context budget exhausted (manual §9.2).

Files opened: [n]   Lines read: [approx n]   Files modified: [n]
The task is not complete because: [one sentence, concrete].

I am stopping rather than continuing to read. I did not read the specification in
full and did not survey other lanes.

Work in progress, if any:
  [list of files created/modified, or "none — working tree clean"]

REQUEST FOR L0: the task is larger than one unit. Please split it.
```

### Blocker: possible duplicate work

```text
STATUS: BLOCKED
TASK: [task id from the card]
LANE: [L1|L2|L3|L4|L5]
BRANCH: [lane/N/phase-task]
TRIPWIRE: T9 — I suspect another lane has already implemented this.

What I observed that raised the suspicion, and where (a file, contract, or
task-card reference — not a survey of another lane's owned tree):
  [one sentence]

I have not opened another lane's owned paths to confirm this. I have made no
edits. Working tree is clean.

REQUEST FOR L0: confirm whether this task is still needed, or close it as a
duplicate.
```

### Blocker: guess required to proceed

```text
STATUS: BLOCKED
TASK: [task id from the card]
LANE: [L1|L2|L3|L4|L5]
BRANCH: [lane/N/phase-task]
TRIPWIRE: T10 — I caught myself about to guess rather than follow a stated
fact.

The sentence I was about to write, verbatim:
  "[the "I assume" / "probably" / "it seems" / "should be" sentence]"
What it was standing in for: [one sentence — the fact the card does not
  state]

I have not resolved this with a guess. I have made no edits. Working tree is
clean.

REQUEST FOR L0: state the fact, or confirm which reading to use.
```

---

## 9.11 Completion report — the only shape accepted

When the task genuinely is done and verified:

```text
STATUS: DONE
TASK: [task id from the card]
LANE: [L1|L2|L3|L4|L5]
BRANCH: [lane/N/phase-task]

FILES CHANGED (complete list, absolute paths):
  [path]  [created|modified]

ACCEPTANCE CRITERIA:
  1. [criterion, quoted from the card] — MET, evidence: [one line]
  2. [criterion, quoted from the card] — MET, evidence: [one line]

SELF-VERIFY:
  command: [exact command from the card]
  exit code: 0
  output: [paste, unedited]

SCOPE: no files outside the list above were modified. No paths outside my lane's
owned prefixes were touched.

OBSERVED BUT NOT FIXED (out of scope, for L0 triage):
  [one line each, or "none"]
```

Two hard constraints on this report:

- **Every criterion must say MET or the status is not DONE.** If one criterion is unmet, the whole report is a BLOCKED report. There is no "mostly done."
- **The self-verify block must contain output you actually saw this session.** Fabricating or reconstructing it is the most serious failure in this manual.

---

## 9.12 Quick card — keep this in front of you

```text
BEFORE                          DURING                      AFTER
--------------------------------------------------------------------------------
Read the task card only.        1 file changed, default.    Run the self-verify.
Prove every path exists.        grep -n before sed -n.      Paste real output.
wc -l before opening.           Never bare "." in grep.     Every criterion MET.
Never cat the 10,256-line spec. Never cat the spec.         Note, don't fix, strays.
Budget: 8 files / 1500 lines.   Tripwire fires -> STOP.     Otherwise: BLOCKED.
```

**Three sentences to remember when everything else has fallen out of context:**

1. The task card is the authority; the specification is a citation target, never a reading assignment.
2. Locate with `grep -n`, read with `sed -n`, and read nothing you were not sent to read.
3. Stopping and escalating is a success; guessing, widening, or reporting unverified work is a failure — and the first is always cheaper than the second.
