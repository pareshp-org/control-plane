# 04 — Anti-Hallucination Protocol

**Audience:** the AI developer executing a single assigned task on a single lane branch.
**Status:** Mandatory. This file is not advice. Every rule here is a gate.
**Applies to:** every task, every lane (L1–L5), every PR into `integration`.

---

## 0. Why this file exists

You are a low-cost, fast model with **no repo context, no memory of the last task, and no
authority to decide anything**. You are good at producing text that looks correct. You are
bad at knowing whether it *is* correct.

Six specific failures account for almost every bad PR produced by a model like you:

| # | Failure | What it looks like | Defence |
|---|---|---|---|
| 1 | Invented path | You reference `validators/registry/validate_registry.py` because it *sounds* like it exists | **V1** |
| 2 | Invented citation | You write "per Section 42.3 of the spec" without ever opening the spec | **V2** |
| 3 | Claimed pass | You write "tests pass" without running them, or you ran a subtly wrong command | **V3** |
| 4 | Invented symbol | You call `load_schema()` in a module that has no such function | **V4** |
| 5 | Invented package | You add `yaml-schema-validator` to a manifest; no such package exists, or worse, one does now | **V5** |
| 6 | Partial completion | You did 4 of 6 acceptance criteria and reported "done" | **V6** |

Plus two scope failures covered in §7: **drifting outside your lane**, and **re-implementing
something another lane owns**. Together these are the two halves of the otherwise-undefined
**V7** referenced in the blocker template (§8's "Rule fired" line).

**Escalation taxonomy note (B3).** `V1`…`V7` name *verification disciplines* — the checks that
catch you about to assert something you never confirmed — not a second escalation taxonomy in
their own right. `manual/03-guardrails-and-stop-rules.md`'s `STOP-01`…`STOP-08` is the one
canonical set of categories a blocker escalates under, and this is where a `V`-rule failure lands
once you stop: `V1`/`V3` (a referenced path or a claimed pass turns out false) file as `STOP-02`
if the missing thing is a contract, otherwise `STOP-01`; `V2`/`V4`/`V5` (an invented citation,
symbol or package) have no fact to verify against and file as `STOP-01`; `V6` (partial completion
reported as done) is caught by you, not escalated — finish the work or, if you cannot, file
`STOP-08`; `V7` (scope drift or re-implementation) files as `STOP-03`. Every rule in this file
exists to make you catch the failure yourself, before it becomes any of these.

### The Prime Directive

> **If you did not run a command and read its output, you do not know it.**
> Anything you did not verify by command output is a guess. You never ship a guess, and you
> never write a guess into a PR body, a commit message, a comment, or a status report.

### The Second Directive

> **Ambiguity is a STOP, never a guess.**
> You have no authority to resolve ambiguity. If the task spec does not tell you, the answer
> is not "pick the sensible one". The answer is §8, Blocker.

---

## 1. Shell contract

Every command in this file is **bash**. On Windows, run them in **Git Bash**, not PowerShell
and not `cmd`. In CI they run on a Linux runner. Do not translate them. Do not "improve" them.
Copy them exactly.

Set your shell up once at the start of every task, verbatim:

```bash
set -euo pipefail
set -u
export EV="${TMPDIR:-/tmp}/evidence/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$EV"
echo "EVIDENCE_DIR=$EV"
```

`$EV` is your evidence directory. It lives **outside the repository** on purpose: writing
evidence files inside the repo would put files on paths your lane may not own, which fails the
lane-guard check (PARTITION.md, rule 1).

Every verification in this file writes its output into `$EV`. The PR body in §9 is assembled
from those files. **You never type evidence from memory. You paste it from `$EV`.**

---

## 2. V1 — Verify every file path before you reference it

**Rule:** you may not write a path — in code, in an import, in a config, in a command, in a
comment, in the PR body — until a command has told you it exists.

There are two kinds of path and they need different checks.

### V1a — A path that must already exist (you are reading, importing, or editing it)

Run this **before** you open it, and **before** you name it in any output:

```bash
set -euo pipefail
# Replace <PATH> with the exact path. Run once per path.
PATH_UNDER_TEST="<PATH>"
if [ -e "$PATH_UNDER_TEST" ]; then
  echo "PATH-OK       $PATH_UNDER_TEST"
else
  echo "PATH-MISSING  $PATH_UNDER_TEST"
fi
```

`PATH-MISSING` means **STOP** (§8). It does not mean "create it". It does not mean "try a
similar path". A missing path that the task spec told you would be there means the task spec
is wrong, and a wrong task spec is an L0 problem, not yours.

To check every path your task spec named, in one shot — build the list by copying the paths
**literally out of the task spec**, one per line, changing nothing:

```bash
set -euo pipefail
cat > "$EV/paths-claimed.txt" <<'EOF'
<PATH_1>
<PATH_2>
<PATH_3>
EOF

while IFS= read -r p; do
  [ -z "$p" ] && continue
  if [ -e "$p" ]; then echo "PATH-OK       $p"; else echo "PATH-MISSING  $p"; fi
done < "$EV/paths-claimed.txt" | tee "$EV/v1-paths.txt"

echo "---"
grep -c '^PATH-MISSING' "$EV/v1-paths.txt" || true
```

If the final count is anything other than `0`, **STOP**.

### V1b — Git is the authority, not the filesystem

An untracked file exists on disk and does not exist in the repo. A file you are told to import
must be **tracked**:

```bash
git ls-files --error-unmatch -- "<PATH>" && echo "TRACKED-OK <PATH>"
```

Non-zero exit means the file is not in the repository. **STOP.**

To see what actually exists under a directory instead of guessing at its contents:

```bash
git ls-files -- "<DIRECTORY>/" | head -50
```

If that prints nothing, the directory is empty or absent in git. That is a fact. Write the fact.
Do not write a plausible file list.

### V1c — A path you are creating

New files are the normal case (PARTITION.md, rule 5: additive-only). Before creating one,
prove the parent exists and the file does **not**:

```bash
set -euo pipefail
NEW="<NEW_FILE_PATH>"
mkdir -p "$(dirname "$NEW")"
if [ -e "$NEW" ]; then
  echo "COLLISION  $NEW already exists — do not overwrite"
else
  echo "CREATE-OK  $NEW"
fi
```

`COLLISION` means **STOP** unless your task spec explicitly names that file as one you edit.
Overwriting a file another task created is how parallel work is destroyed.

### V1d — The path is inside your lane

Owning the path is a hard precondition. See §7 before you write a single byte.

---

## 3. V2 — Never cite a spec section without grepping it first

**Rule:** you may not write "Section N", "per the spec", "the spec requires", or any paraphrase
of the spec, until `grep` has shown you the actual text and you have recorded the line number.

The spec is at:

```
C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md
```

Verify the spec file itself before citing anything from it:

```bash
SPEC="C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md"
[ -f "$SPEC" ] && wc -l "$SPEC" || echo "SPEC-MISSING $SPEC"
```

### V2a — Prove the section exists

```bash
set -euo pipefail
SPEC="C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md"
# Top-level section, e.g. 30:
grep -n "^## Section 30\." "$SPEC"
# Sub-section, e.g. 30.2:
grep -n "^### 30\.2" "$SPEC"
```

No output means **the section does not exist**. You invented it. Do not soften it to "roughly
Section 30". Delete the citation, and if the claim needed a citation, **STOP** (§8).

Known-good example, run it now to see what a real hit looks like:

```bash
SPEC="C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md"
grep -n "^### 30\.2 Plan-checker hard rejects" "$SPEC"
# → 2720:### 30.2 Plan-checker hard rejects
```

### V2b — Prove the section says what you claim

Existence is not enough. Read the body:

```bash
set -euo pipefail
SPEC="C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md"
START=$(grep -n "^### 30\.2" "$SPEC" | head -1 | cut -d: -f1)
sed -n "${START},$((START+40))p" "$SPEC" | tee "$EV/v2-section-30.2.txt"
```

Or search for the claim itself rather than the number:

```bash
grep -n -i "slopsquat" "C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md"
```

### V2c — Citation format is fixed

Every citation you write must carry the line number you actually saw:

```
Section 30.2 (spec line 2720)
```

A citation without a line number is an unverified citation, and an unverified citation is a
hallucination. The self-audit in §9 checks for this.

### V2d — The spec is for citation only

You do **not** implement from the spec. You implement from your task spec and from
`contracts/**`. The spec is a source of *quotations*, never a source of *requirements you
inferred*. If your task spec and the master spec appear to disagree, that is not yours to
reconcile — **STOP** (§8).

---

## 4. V3 — Never claim a test passed without pasting the actual output

**Rule:** the words "passes", "passing", "green", "works", "verified", and "confirmed" may not
appear in your output unless the exact command output that proves them is pasted next to them.

Two things go wrong here and both are lethal:

1. You never ran it.
2. You ran something *adjacent* — a different suite, a filtered subset, a command that
   printed a usage message and exited 0 — and read the absence of red as green.

### V3a — The literal run command

Never run a bare command. Always capture output **and** the true exit code:

```bash
set -euo pipefail
set -o pipefail
CMD="<EXACT_VERIFY_COMMAND_FROM_TASK_SPEC>"
echo "\$ $CMD" | tee "$EV/v3-verify.txt"
eval "$CMD" 2>&1 | tee -a "$EV/v3-verify.txt"
RC=${PIPESTATUS[0]}
echo "EXIT_CODE=$RC" | tee -a "$EV/v3-verify.txt"
```

`<EXACT_VERIFY_COMMAND_FROM_TASK_SPEC>` is copied **character for character** from your task
spec. You do not shorten it, add flags to it, drop a `--strict`, or swap `make verify` for
`pytest`. A command you modified is a command that proves nothing about the acceptance
criterion, which named the original.

If your task spec has no verify command: **STOP** (§8). Per Section 30.2 (spec line 2723), a
task lacking an automated verify command is auto-rejected — you must not invent one to
paper over the gap.

### V3b — `EXIT_CODE=0` is necessary, not sufficient

Check that the run did real work. A suite that collected zero tests exits 0 and is a failure,
not a pass:

```bash
grep -n -E "([0-9]+ (passed|failed|error|skipped))|no tests ran|collected 0 items|0 passing|Error|Traceback|FAIL" \
  "$EV/v3-verify.txt" | tee "$EV/v3-summary.txt"
```

Refuse to call it a pass if any of these is true:

- `EXIT_CODE` is not `0`
- the output contains `no tests ran`, `collected 0 items`, or `0 passed`
- the output contains `Traceback`, `FAIL`, or `error:` — even alongside exit 0
- the output is empty

Any of those: **STOP** if you cannot fix it inside your own owned paths; otherwise fix and rerun
from the top of V3a. You never rerun until it passes by changing the *test*. Changing an
assertion to make it green is falsifying evidence.

### V3c — Prove the check can fail

A check that cannot fail is not a check. This is the seeded-defect rule of Section 31.2 (spec
line 2792) applied to you personally. Before you trust a green run, break something trivially
and confirm it goes red:

```bash
set -euo pipefail
# 1. Capture the green run (already in $EV/v3-verify.txt).
# 2. Break one assertion or one input inside YOUR OWN owned path.
# 3. Re-run the identical command:
set -o pipefail
eval "$CMD" 2>&1 | tee "$EV/v3-seeded-defect.txt"
echo "SEEDED_EXIT_CODE=${PIPESTATUS[0]}" | tee -a "$EV/v3-seeded-defect.txt"
# 4. Revert the break:
git checkout -- "<THE_FILE_YOU_BROKE>"
# 5. Confirm the tree is clean again:
git status --porcelain -- "<THE_FILE_YOU_BROKE>"
```

`SEEDED_EXIT_CODE=0` means your verification is blind. **STOP** (§8) — do not report a pass
from an instrument that cannot report a failure.

Step 5 must print nothing. If it prints anything, your revert failed; fix it before continuing.

### V3d — Paste the tail, not a summary

In the PR body you paste the last lines verbatim. You do not paraphrase them.

```bash
tail -20 "$EV/v3-verify.txt"
```

"All tests pass" is a claim. The 20 lines above are evidence. Only evidence is permitted.

---

## 5. V4 — Check a symbol exists before you call it

**Rule:** every function, class, method, constant, CLI flag, YAML key, JSON Schema `$id`, and
`make` target you reference must be proven to exist first. This is a Section 30.2 hard reject
(spec line 2722): a plan referencing symbols that do not exist in source is rejected outright.

### V4a — Source-level check (works for every language)

```bash
set -euo pipefail
SYM="<SYMBOL_NAME>"
git grep -n -w -- "$SYM" | tee "$EV/v4-$SYM.txt"
echo "HITS=$(wc -l < "$EV/v4-$SYM.txt")"
```

`HITS=0` means the symbol does not exist anywhere in the repository. You invented it. **STOP.**

Narrow to a definition rather than any mention:

```bash
set -euo pipefail
# Python
git grep -n -E "^\s*(def|class)\s+<SYMBOL_NAME>\b" -- '*.py'
# JavaScript / TypeScript
git grep -n -E "(function|const|class|export)\s+<SYMBOL_NAME>\b" -- '*.ts' '*.js'
# Go
git grep -n -E "^func (\([^)]*\) )?<SYMBOL_NAME>\b" -- '*.go'
# Shell function
git grep -n -E "^\s*<SYMBOL_NAME>\s*\(\)" -- '*.sh'
# Makefile target
git grep -n -E "^<SYMBOL_NAME>:" -- Makefile 'Makefile*' '*.mk'
```

A mention with no definition means you found a *caller*, not the thing. Keep looking or **STOP**.

### V4b — Runtime check (the stronger proof)

Grep proves the text exists. Import proves the symbol is reachable:

```bash
# Python
python -c "import <MODULE>; print(getattr(<MODULE>, '<SYMBOL_NAME>'))"
# Node (CommonJS)
node -e "const m=require('<MODULE_PATH>'); console.log(typeof m['<SYMBOL_NAME>'])"
```

A traceback or `undefined` means the symbol is not callable the way you intend. **STOP.**

### V4c — Config keys, schema fields, CLI flags

These get invented as often as functions do.

```bash
set -euo pipefail
# YAML key exists (yq)
yq '.<KEY_PATH>' "<FILE>.yaml"
# JSON key exists (jq) — 'null' means MISSING
jq '.<KEY_PATH>' "<FILE>.json"
# JSON Schema: list the properties that actually exist
jq -r '.properties | keys[]' "<SCHEMA_FILE>.json"
# CLI flag really exists — grep the tool's own help, do not trust memory
<TOOL> --help 2>&1 | grep -n -- "--<FLAG>"
```

`jq` printing `null`, `yq` printing `null`, or the `--help` grep printing nothing all mean the
same thing: **it does not exist**. Do not use it.

### V4d — Cross-lane symbols are forbidden regardless of existence

A symbol proven to exist in another lane's source tree is still off-limits. PARTITION.md rule 4:
you consume another lane's output only through `contracts/**` or a published artifact.

```bash
# Is this symbol reachable through the frozen contract surface?
git grep -n -w -- "<SYMBOL_NAME>" -- 'contracts/**'
```

No hit under `contracts/**` means you may not call it, even though it exists. **STOP** and file a
Contract Change Request per PARTITION.md rule 2 — you do not edit `contracts/**` yourself.

---

## 6. V5 — Confirm a package is real before adding it (the slopsquat check)

**Rule:** you may not add, import, or name any third-party dependency until live registry API
output proves it exists and is the package you meant.

The spec calls this the **slopsquat legitimacy check**, Section 30.2 (spec line 2727):

> "a package name fails the slopsquat legitimacy check against live registry APIs"

is one of the plan-checker's automatic hard rejects. Section 33.2 (spec line 2859) states the
same check runs again in CI at execute time against lockfile and manifest diffs, so a dependency
you add during Execute cannot bypass it. **You will be caught. Check first.**

Why this matters more for you than for a human: models hallucinate plausible package names, and
attackers register those exact hallucinated names. The package you invent today may be real,
malicious, and installable tomorrow. "It installed fine" is not evidence of legitimacy — it is
the attack succeeding.

### V5a — Existence check against the live registry

```bash
set -euo pipefail
# npm
PKG="<PACKAGE_NAME>"
curl -sS -o /dev/null -w "npm %{http_code} $PKG\n" "https://registry.npmjs.org/$PKG" \
  | tee -a "$EV/v5-packages.txt"

# PyPI
PKG="<PACKAGE_NAME>"
curl -sS -o /dev/null -w "pypi %{http_code} $PKG\n" "https://pypi.org/pypi/$PKG/json" \
  | tee -a "$EV/v5-packages.txt"
```

`404` = the package does not exist. **STOP.** Do not try a near-miss name.

### V5b — `200` is not a pass — pull the provenance

A typosquat also returns `200`. Existence proves nothing on its own.

```bash
set -euo pipefail
# npm provenance
PKG="<PACKAGE_NAME>"
curl -sS "https://registry.npmjs.org/$PKG" | jq -r '
  "name:      " + .name,
  "created:   " + .time.created,
  "modified:  " + .time.modified,
  "latest:    " + (."dist-tags".latest // "NONE"),
  "repo:      " + (.repository.url // "NONE"),
  "license:   " + (.license // "NONE"),
  "versions:  " + ((.versions | keys | length) | tostring),
  "maintainers: " + ((.maintainers // [] | length) | tostring)
' | tee -a "$EV/v5-packages.txt"

# PyPI provenance
PKG="<PACKAGE_NAME>"
curl -sS "https://pypi.org/pypi/$PKG/json" | jq -r '
  "name:      " + .info.name,
  "version:   " + .info.version,
  "home:      " + (.info.home_page // "NONE"),
  "project:   " + ((.info.project_urls // {}) | tostring),
  "license:   " + (.info.license // "NONE"),
  "releases:  " + ((.releases | keys | length) | tostring)
' | tee -a "$EV/v5-packages.txt"
```

**STOP** if any of these is true:

- `created` / first release is within the last 90 days
- `repo` / `home` is `NONE`, or points somewhere unrelated to the package's claimed project
- there is exactly one version and no maintainers
- the name differs by one character, a hyphen, or a pluralisation from a package you know is
  the popular one (`requsts` vs `requests`, `python-dateutil` vs `dateutil`)
- the package name appeared in your own generated text before it appeared in the task spec

That last bullet is the important one. **A package name you produced from memory rather than
copied from the task spec or an existing manifest is suspect by default.**

### V5c — Prove it is already in the manifest, which is the best outcome

The cheapest safe dependency is one the repo already has:

```bash
git grep -n -- "<PACKAGE_NAME>" -- package.json package-lock.json requirements.txt \
  pyproject.toml poetry.lock go.mod go.sum Gemfile Gemfile.lock
```

A hit means the dependency is already approved and pinned. Use the version that is already
there. Do not bump it — a version bump is a separate task you were not assigned.

### V5d — Pinned GitHub Actions are dependencies too

Section 33.2 requires third-party Actions pinned to a full commit SHA, no tags. If your task adds
one, verify the SHA resolves:

```bash
gh api "repos/<OWNER>/<REPO>/commits/<FULL_40_CHAR_SHA>" --jq '.sha' \
  | tee -a "$EV/v5-packages.txt"
```

No output, an error, or a short SHA means **STOP**.

### V5e — You have no appeal authority

Section 30.2 (spec line 2731) provides an appeal path for a false positive: a decision record
with a second engineer confirming provenance. **You are not a second engineer and you cannot
write a decision record.** A failed slopsquat check is, for you, always a **STOP** (§8).

---

## 7. Scope: stay inside your lane

Two failure modes, one check.

- **Drift** — you saw an adjacent bug and fixed it. It was not your task. It is now an
  unreviewable PR that fails lane-guard.
- **Duplication** — you implemented something another lane already owns, because you could not
  see their tree.

PARTITION.md is FROZEN and is the only authority on ownership. Re-read the ownership table
before you write. Then prove your diff obeys it.

### V7a — Show exactly what you changed

```bash
git fetch origin integration
git diff --name-only origin/integration...HEAD | tee "$EV/v7-changed-files.txt"
```

### V7b — Every changed path must sit under a prefix your lane owns

Fill `OWNED` from the PARTITION.md row for **your** lane and nothing else. Verbatim, one prefix
per line:

```bash
set -euo pipefail
cat > "$EV/v7-owned-prefixes.txt" <<'EOF'
<OWNED_PREFIX_1>
<OWNED_PREFIX_2>
EOF

VIOLATIONS=0
while IFS= read -r f; do
  [ -z "$f" ] && continue
  ok=0
  while IFS= read -r pre; do
    [ -z "$pre" ] && continue
    case "$f" in "$pre"*) ok=1 ;; esac
  done < "$EV/v7-owned-prefixes.txt"
  if [ "$ok" -eq 1 ]; then
    echo "SCOPE-OK        $f"
  else
    echo "SCOPE-VIOLATION $f"; VIOLATIONS=$((VIOLATIONS+1))
  fi
done < <(git diff --name-only origin/integration...HEAD) > "$EV/v7-scope.txt"
cat "$EV/v7-scope.txt"

echo "SCOPE_VIOLATIONS=$VIOLATIONS" | tee -a "$EV/v7-scope.txt"
[ "$VIOLATIONS" -eq 0 ] || exit 1
```

`SCOPE_VIOLATIONS` must be `0`. Anything else: revert the offending files and **STOP** if the
task genuinely required them.

```bash
git checkout origin/integration -- "<FOREIGN_PATH>"
```

Reverting is correct. Arguing that the change is small, obvious, or beneficial is not. A one-line
fix on a foreign path is still a lane-guard failure and still blocks the merge train.

### V7c — Before you build anything, check nobody else owns it

```bash
set -euo pipefail
git grep -n -i -- "<THING_YOU_ARE_ABOUT_TO_BUILD>" -- contracts/ || \
  echo "NOT-IN-CONTRACTS: <THING_YOU_ARE_ABOUT_TO_BUILD>"
grep -n -i -- "<THING_YOU_ARE_ABOUT_TO_BUILD>" \
  "C:/D_Drive/PS/MultiProduct/Code/implementation/PARTITION.md"
```

If PARTITION.md assigns it to another lane, you do not build it — even a stub, even "temporarily",
even if you are blocked without it. **STOP** (§8).

---

## 8. V6 — Re-read the task spec after finishing

**Rule:** finishing the work is not finishing the task. After the last edit, you go back to the
task spec, extract every acceptance criterion, and prove each one individually.

This is the defence against silent partial completion — the failure Section 29.5 (spec line 2700)
names directly: *"Silent scope change is the failure this prevents. It produces work that was
never verified against its actual requirement."*

### V6a — Extract the criteria into a file, verbatim

Copy each acceptance criterion out of the task spec, one per line, changing nothing. Not your
summary of it. The literal text.

```bash
set -euo pipefail
cat > "$EV/v6-acceptance-criteria.txt" <<'EOF'
AC1: <LITERAL_TEXT_OF_CRITERION_1>
AC2: <LITERAL_TEXT_OF_CRITERION_2>
AC3: <LITERAL_TEXT_OF_CRITERION_3>
EOF
cat "$EV/v6-acceptance-criteria.txt"
```

### V6b — Bind one proving command to each criterion

```bash
set -euo pipefail
cat > "$EV/v6-proof-map.txt" <<'EOF'
AC1 | <COMMAND_THAT_PROVES_AC1> | <EXPECTED_OUTPUT>
AC2 | <COMMAND_THAT_PROVES_AC2> | <EXPECTED_OUTPUT>
AC3 | <COMMAND_THAT_PROVES_AC3> | <EXPECTED_OUTPUT>
EOF
cat "$EV/v6-proof-map.txt"
```

A criterion you cannot bind a command to is a criterion you cannot claim. **STOP** (§8).
"I inspected the code and it looks right" is not a command.

### V6c — Run every one and record the result

```bash
set -euo pipefail
set -o pipefail
: > "$EV/v6-results.txt"
while IFS='|' read -r ac cmd expected; do
  [ -z "$ac" ] && continue
  ac=$(echo "$ac" | xargs); cmd=$(echo "$cmd" | xargs)
  echo "=== $ac ===" >> "$EV/v6-results.txt"
  echo "\$ $cmd"     >> "$EV/v6-results.txt"
  eval "$cmd" >> "$EV/v6-results.txt" 2>&1
  echo "EXIT=$?"     >> "$EV/v6-results.txt"
done < "$EV/v6-proof-map.txt"
cat "$EV/v6-results.txt"
```

Then count what is unproven:

```bash
set -euo pipefail
grep -c '^=== ' "$EV/v6-results.txt"                      # criteria attempted
wc -l < "$EV/v6-acceptance-criteria.txt"                  # criteria that exist
grep -n 'EXIT=[^0]' "$EV/v6-results.txt" || echo "ALL-EXIT-ZERO"
```

The first two numbers must be equal, and the third must print `ALL-EXIT-ZERO`. If not, the task
is **not done**, no matter how much code you wrote.

### V6d — Re-read the STOP rule too

Your task spec contains a STOP rule (PARTITION.md, AI developer profile). Read it again now, at
the end, and confirm its condition did not become true while you worked. A STOP condition that
fired mid-task and was ignored is worse than one that fired at the start.

### The Blocker template — use verbatim

When any rule in this file says **STOP**, you stop editing immediately, you do not partially ship,
and you emit exactly this:

```
BLOCKER

Task:        <TASK_ID_FROM_TASK_SPEC>
Lane:        <LANE_ID>            (L1 | L2 | L3 | L4 | L5)
Branch:      <CURRENT_BRANCH>
Rule fired:  <V1 | V2 | V3 | V4 | V5 | V6 | V7>

What I tried to verify:
  <ONE_SENTENCE>

Command I ran:
  <EXACT_COMMAND>

Output I got:
  <EXACT_OUTPUT_PASTED_NOT_SUMMARISED>

Output the task spec led me to expect:
  <EXACT_EXPECTATION_QUOTED_FROM_TASK_SPEC>

Work state:
  Committed to branch: <YES_OR_NO>
  Files changed so far: <PASTE_OUTPUT_OF: git diff --name-only origin/integration...HEAD>

I did not guess, and I did not proceed. This needs an L0 decision.
```

Get the branch for that template with:

```bash
git rev-parse --abbrev-ref HEAD
```

---

## 9. Self-audit checklist — run before opening ANY PR

Run all of it. Top to bottom. Every line. A PR opened without a completed self-audit is
rejected on sight, and re-running it is cheaper than a rejected PR.

### 9.1 The commands

```bash
set -euo pipefail
set -u
echo "== SELF-AUDIT START $(date -u +%Y-%m-%dT%H:%M:%SZ) =="

echo "--- A1 branch is mine and correctly prefixed"
git rev-parse --abbrev-ref HEAD

echo "--- A2 rebased on integration"
git fetch origin integration
git rev-list --count HEAD..origin/integration      # must be 0

echo "--- A3 exactly what I changed"
git diff --name-only origin/integration...HEAD | tee "$EV/audit-files.txt"

echo "--- A4 scope: no foreign paths (see §7b)"
cat "$EV/v7-scope.txt" 2>/dev/null | tail -1

echo "--- A5 nothing uncommitted, nothing untracked left behind"
git status --porcelain

echo "--- A6 no debug residue"
git diff origin/integration...HEAD | \
  grep -n -E "^\+.*(TODO|FIXME|XXX|TBD|console\.log|print\(|binding\.pry|debugger)" \
  || echo "CLEAN"

echo "--- A7 no secrets"
git diff origin/integration...HEAD | \
  grep -n -E "^\+.*(BEGIN [A-Z ]*PRIVATE KEY|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|api[_-]?key\s*[:=]\s*[\"'][^\"']{12,})" \
  || echo "CLEAN"

echo "--- A8 every path I reference exists"
test -s "$EV/v1-paths.txt" || { echo "A8 FAIL: no V1 evidence file"; exit 1; }
grep -c '^PATH-MISSING' "$EV/v1-paths.txt"

echo "--- A9 the verify command's real result"
tail -20 "$EV/v3-verify.txt" 2>/dev/null || echo "NO-VERIFY-EVIDENCE"
grep -n '^EXIT_CODE=' "$EV/v3-verify.txt" 2>/dev/null || echo "NO-EXIT-CODE"

echo "--- A10 the verify command can actually fail"
grep -n '^SEEDED_EXIT_CODE=' "$EV/v3-seeded-defect.txt" 2>/dev/null || echo "NO-SEEDED-DEFECT"

echo "--- A11 every acceptance criterion proved"
test -s "$EV/v6-results.txt" || { echo "A11 FAIL: no V6 evidence file"; exit 1; }
grep -c '^=== ' "$EV/v6-results.txt"
wc -l < "$EV/v6-acceptance-criteria.txt" 2>/dev/null || echo 0
grep -n 'EXIT=[^0]' "$EV/v6-results.txt" 2>/dev/null || echo "ALL-EXIT-ZERO"

echo "--- A12 dependency check ran for every new package"
git diff origin/integration...HEAD -- package.json requirements.txt pyproject.toml go.mod \
  | grep -n '^+' || echo "NO-NEW-DEPS"
cat "$EV/v5-packages.txt" 2>/dev/null || echo "NO-PACKAGE-EVIDENCE"

echo "== SELF-AUDIT END =="
```

### 9.2 The pass conditions — all twelve must hold

| # | Check | Passes only when |
|---|---|---|
| A1 | Branch | Name starts with your lane's prefix from PARTITION.md (`lane/N/...`) |
| A2 | Rebase | `git rev-list --count HEAD..origin/integration` prints `0` |
| A3 | Diff | Every listed file is one your task spec named |
| A4 | Scope | `SCOPE_VIOLATIONS=0` |
| A5 | Clean tree | `git status --porcelain` prints nothing |
| A6 | No residue | Prints `CLEAN` |
| A7 | No secrets | Prints `CLEAN` |
| A8 | Paths | File `$EV/v1-paths.txt` exists **and** prints `0` |
| A9 | Verify ran | Real output present **and** `EXIT_CODE=0` |
| A10 | Verify can fail | `SEEDED_EXIT_CODE` present and **non-zero** |
| A11 | Criteria | File `$EV/v6-results.txt` exists **and** attempted == total, and `ALL-EXIT-ZERO` |
| A12 | Packages | `NO-NEW-DEPS`, or every new package has V5b provenance output |

**Any row failing means you do not open the PR.** Fix it inside your owned paths, or emit the
Blocker (§8). There is no third option and no partial-credit PR.

### 9.2a SELF-VERIFY negative — absent evidence file must fail loudly, not silently pass

```bash
set -euo pipefail
# Run the A8 check with no V1 evidence file present — must exit 1 with A8 FAIL message.
TMPEV=$(mktemp -d)
A8_RC=0
A8_OUT=$(EV="$TMPEV" bash -c '
  echo "--- A8 every path I reference exists"
  test -s "$EV/v1-paths.txt" || { echo "A8 FAIL: no V1 evidence file"; exit 1; }
  grep -c '"'"'^PATH-MISSING'"'"' "$EV/v1-paths.txt"
' 2>&1) || A8_RC=$?
# Run the A11 check with no V6 evidence file present — must exit 1 with A11 FAIL message.
A11_RC=0
A11_OUT=$(EV="$TMPEV" bash -c '
  echo "--- A11 every acceptance criterion proved"
  test -s "$EV/v6-results.txt" || { echo "A11 FAIL: no V6 evidence file"; exit 1; }
  grep -c '"'"'^=== '"'"' "$EV/v6-results.txt"
' 2>&1) || A11_RC=$?
rm -rf "$TMPEV"
printf 'a8-absent=[msg=%s rc=%s]\n' "$(printf '%s' "$A8_OUT" | grep 'A8 FAIL' || echo NO-FAIL)" "$A8_RC"
printf 'a11-absent=[msg=%s rc=%s]\n' "$(printf '%s' "$A11_OUT" | grep 'A11 FAIL' || echo NO-FAIL)" "$A11_RC"
```

Expected output:

```
a8-absent=[msg=A8 FAIL: no V1 evidence file rc=1]
a11-absent=[msg=A11 FAIL: no V6 evidence file rc=1]
```

**STOP rule** — if either check prints `rc=0`, the evidence-absence path returns a silent pass. The `cat … 2>/dev/null | grep -c … || true` form must be replaced with the `test -s` guard above. A missing evidence file is never the same as a clean evidence file.

### 9.3 Claim audit — read your own draft PR body

Before you post it, re-read every sentence you wrote and delete any that fails this test:

- [ ] Every **path** I wrote appears in `$EV/v1-paths.txt` as `PATH-OK`.
- [ ] Every **spec citation** I wrote carries a line number I saw with `grep -n`.
- [ ] Every **"passes"** I wrote sits directly above pasted command output.
- [ ] Every **symbol** I named appears in a `$EV/v4-*.txt` file with `HITS` greater than 0.
- [ ] Every **package** I added appears in `$EV/v5-packages.txt` with a `200` and provenance.
- [ ] Every **acceptance criterion** appears in `$EV/v6-results.txt` with `EXIT=0`.
- [ ] I made **no claim about another lane's code**, its status, or its plans.
- [ ] I described **only what I did**, never what I intended, expected, or assume happens next.
- [ ] There is **no "should"**, no "presumably", no "this likely", no "appears to" anywhere.
- [ ] There is **no TBD**, no placeholder, and no unreplaced `<...>` token.

Machine-check the last two:

```bash
grep -n -E "should (work|pass|be)|presumably|likely (works|passes)|appears to|I assume|TBD|<[A-Z_]+>" \
  "$EV/pr-body.md" || echo "LANGUAGE-CLEAN"
```

---

## 10. PR body — use `master/09`'s template, not a second one (B4)

`master/09-glossary-and-conventions.md` §6.2 is the one canonical PR body template — its
nine `##` sections, in that order, verbatim. Write your draft to `$EV/pr-body.md` in that
shape so §9.3 above can machine-check it, then paste it into the PR. Do not restructure it
into a different section set.

This file's own concerns fold into that template's existing sections rather than adding new
ones:

| This file requires… | Goes inside `master/09` §6.2's… |
|---|---|
| The exact list of changed files (`$EV/audit-files.txt`) | `## Lane and paths` — its "Paths touched" list already is this |
| The scope self-check (`SCOPE_VIOLATIONS=0`) | `## Lane and paths` — append the check's last line under the path list |
| The seeded-defect / verification-can-fail evidence (§31.2) | `## Self-verify transcript` — paste it directly below the positive run |
| The new-dependencies statement (`$EV/v5-packages.txt`, or "No new dependencies.") | `## What changed` — its last sentence |
| The twelve-point self-audit (A1–A12, all pass, with timestamp) | `## Agent-authored` — append below the `Agent-Authored: true` line |
| **The "Not done" statement — mandatory, never omit** | `## Acceptance criteria` — append as a final, unchecked-or-"Nothing." line after the criteria |

**The "Not done" statement stays mandatory even inside the shared template.** Writing "Nothing."
when something was in fact left undone is the single worst thing you can do on this project —
worse than the bug, worse than the missing test, worse than the failed build. Everything
downstream assumes your report is true.

---

## 11. The five sentences you may never write

Committed to memory, these are the ones that cause the damage:

1. "This should work." — You do not know. Run it. (§4)
2. "The file is probably at ..." — Check it. (§2)
3. "Tests pass." — With no pasted output, this is a lie. (§4)
4. "I also fixed ..." — You were not asked. Revert it. (§7)
5. "I assumed X, so ..." — Assumption is the STOP condition. Emit the Blocker. (§8)

Replace each with the same move: **run the command, paste the output, or stop.**
