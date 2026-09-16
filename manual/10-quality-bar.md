# 10 — The Quality Bar

**Audience:** you, the AI developer executing one task on one lane branch.
**Status:** binding. A task that violates this file is rejected at review even if the code you wrote is correct.
**Read with:** `manual/00-README-FOR-AI-DEVELOPERS.md` (the five rules) and `manual/09-cost-and-context-discipline.md` (what you may read, and when to stop).

---

## 10.0 The one-paragraph version

"Done" is not a feeling and it is not your assessment. **Done is a state you can prove with commands whose output you pasted.** Every file you write must be complete and runnable on the day you write it — never a sketch, never a skeleton, never a file whose real content is deferred to a comment. There are no `TODO`s, no `FIXME`s, no placeholder values, no empty function bodies, no "wire this up later." Your output must match the conventions file, not your own taste. And you must prove you did the **whole** task, not a smaller task that resembles it — because the most common way this build fails is an agent quietly shrinking a five-part criterion into a one-part deliverable and reporting `DONE`. If you cannot reach the bar, the correct output is `BLOCKED` with evidence. `BLOCKED` is cheap. A false `DONE` costs five lanes a merge train.

---

## 10.1 The definition of done — all eight gates, no exceptions

A task is `DONE` when **every one** of these is true and you have the pasted output to prove it. If one is false, the status is `BLOCKED`. There is no third status, no "done with caveats", no "done, minor item remaining."

| # | Gate | Proof you must paste |
|---|---|---|
| **G1** | Every acceptance criterion in the task card is MET — all of them, in full, at the scope the criterion states | The Criterion Coverage Table (§10.6) |
| **G2** | Every file you wrote is **complete** — no stub, no placeholder, no deferred content | Banned-token scan, `DONE-CHECK 1` (§10.3) |
| **G3** | Every file you wrote is **runnable / parseable** by its own toolchain | Per-type check, `DONE-CHECK 2` (§10.4) |
| **G4** | Your output conforms to the conventions file | Conventions conformance table (§10.5) |
| **G5** | You did not narrow the task | The narrowing test, `DONE-CHECK 3` (§10.6) |
| **G6** | The task card's self-verify command ran, exit code `0`, output pasted verbatim from this session | `DONE-CHECK 4` (§10.7) |
| **G7** | Every file you changed is inside your lane's owned paths, and nothing else was touched | `DONE-CHECK 5` (§10.7) |
| **G8** | The completion report is complete and honest, including out-of-scope items you saw and did not fix | The report shape in `manual/09-cost-and-context-discipline.md` §9.11 |

**The order matters.** Run G1 through G7 in order. The first one that fails stops the task; you do not "fix it later in review." Review is not your safety net — review is a human integrator with four other lanes queued behind you.

A note on why this is so blunt (§95.4, on bootstrap gates): *stubbed gates have a habit of staying stubbed.* A stub you ship with an honest intention to finish it is, empirically, a stub that ships. This file removes the intention and requires the finished thing.

---

## 10.2 What a complete file is — and what a plausible-looking stub is

A **complete file** is a file that, if the whole team disappeared today, still does its job tomorrow with nobody touching it.

A **plausible-looking stub** is a file that has the right name, the right imports, the right shape, the right docstring — and does nothing. It passes a glance. It fails a run. It is the single most common defective artifact on this build, because producing it feels exactly like producing the real thing.

Here is the difference, stated as tests you can apply to any file you just wrote.

| Property | Complete file | Plausible-looking stub |
|---|---|---|
| **Executes** | Runs to a defined exit code on real input | Raises, returns `None`, or exits before doing work |
| **Function bodies** | Every function does the thing its name says | One or more bodies are `pass`, `...`, `return None`, or `raise NotImplementedError` |
| **Values** | Every value is the real value the task specified | Contains `TODO`, `CHANGEME`, `example.com`, `your-org`, `foo`, `0.0.0`, `""` where a real value belongs |
| **Comments** | Explain non-obvious *why* | Contain `# TODO`, `# implement later`, `# wire up`, `# not yet` |
| **Schema fields** | Every field the task named is present, typed, and constrained | `properties: {}`, `required: []`, or half the named fields |
| **Error paths** | Failure returns a distinct, non-zero exit code with a message naming the file and the problem | Failure is unhandled, or every path returns `0` |
| **Entry point** | Callable exactly as the task's self-verify command calls it | Importable but not runnable, or runnable but not with those arguments |
| **Tests, when the card names a test file** | Assert real values and fail if the code is broken | `assert True`, or a test that passes against an empty implementation |
| **Coverage of the criterion** | Handles every case the criterion enumerates | Handles the first case, and the rest are "the same pattern" |

### The three questions

Before you report any file as done, answer these three out loud in your reasoning. If any answer is "no" or "not yet", the file is a stub and the task is `BLOCKED`.

1. **Can a person run this file, right now, with the exact command in my task card, and get the exact result the acceptance criteria describe?**
2. **Is there any line in this file whose real content is deferred to a future task, a comment, a human, or "later"?**
3. **If a reviewer deleted every comment in this file, would the file still do its whole job?**

### The prohibition, stated plainly

> **You do not ship sketches.** Every file you write is finished on the day you write it. If the task as written cannot produce a finished file — because an input is missing, a value is unspecified, or a decision has not been made — you do not write a half file and note the gap. You write nothing and you file a blocker (`manual/00-README-FOR-AI-DEVELOPERS.md` §8).
>
> A half file merged into `integration` is worse than no file, because the next lane builds on it, CI goes green against it, and nobody discovers it is hollow until a product depends on it.

---

## 10.3 Banned tokens and placeholder values — `DONE-CHECK 1`

The following tokens are **forbidden in any file you commit**. Not "discouraged". Forbidden. A PR containing one is rejected without further review.

### Hard-banned (any occurrence = FAIL)

```text
TODO            FIXME           XXX             HACK            TBD
PLACEHOLDER     CHANGEME        FILL_ME         FILLME          fill-me
NotImplementedError             NotImplemented
"implement later"               "wire this up"  "for now"       "temporary"
```

### Hard-banned placeholder *values* (any occurrence = FAIL unless the task card literally supplies that value)

```text
example.com     example.org     your-org        your-value      my-product
foo             bar             baz             lorem ipsum     asdf
0.0.0           v0.0.0          0000000         xxxxxxxx        <REPLACE>
```

### Hard-banned empty bodies

A function, method, class, handler, job step, validator or schema whose body is only one of:

```text
pass            ...             return          return None     {}          []
```

is an empty body. An empty body is a stub. A stub is a FAIL. (The single exception: a Python class body that is legitimately `pass` **only** when the task card explicitly specifies an empty marker/exception class and quotes it.)

### Run this before you commit — copy verbatim

```bash
set -euo pipefail
# DONE-CHECK 1 — banned tokens and placeholder values in the files THIS task changed.
# Run from the repository root of the repo you are working in.
set -o pipefail
git fetch origin integration --quiet
FILES="$(git diff --name-only origin/integration...HEAD)"
if [ -z "$FILES" ]; then
  echo "DONE-CHECK 1: FAIL — this task changed no files."
else
  printf '%s\n' "$FILES" | while IFS= read -r f; do
    [ -f "$f" ] || continue
    if grep -nEI 'TODO|FIXME|XXX|HACK|TBD|PLACEHOLDER|CHANGEME|FILL_?ME|fill-me|NotImplemented|implement later|wire this up|for now|temporary|CHANGE ?ME|<REPLACE>|your-(org|value)|my-product|example\.(com|org)|\bfoo\b|\bbar\b|\bbaz\b|lorem ipsum|\basdf\b|v?0\.0\.0|0000000|xxxxxxxx' "$f"; then
      echo "  ^^ DONE-CHECK 1: FAIL — banned token in $f"
    fi
  done
  echo "DONE-CHECK 1 SCAN COMPLETE — any line above marked FAIL blocks this task."
fi
```

```bash
set -euo pipefail
# DONE-CHECK 1b — empty bodies in Python, shell, JSON and YAML files this task changed.
git fetch origin integration --quiet
git diff --name-only origin/integration...HEAD | grep -E '\.(py|sh|json|yaml|yml)$' | while IFS= read -r f; do
  [ -f "$f" ] || continue
  grep -nE '^[[:space:]]*(pass|\.\.\.|return|return None)[[:space:]]*$|"(properties|required)"[[:space:]]*:[[:space:]]*(\{\}|\[\])' "$f" \
    && echo "  ^^ DONE-CHECK 1b: FAIL — empty body in $f" || true
done
echo "DONE-CHECK 1b SCAN COMPLETE"
```

```bash
set -euo pipefail
# DONE-CHECK 1c — a file too small to be complete. Prints every changed file under 5 non-blank lines.
git fetch origin integration --quiet
git diff --name-only origin/integration...HEAD | while IFS= read -r f; do
  [ -f "$f" ] || continue
  n=$(grep -cvE '^[[:space:]]*$' "$f")
  { [ "$n" -lt 5 ] && echo "DONE-CHECK 1c: SUSPECT — $f has only ${n} non-blank lines"; } || true
done
echo "DONE-CHECK 1c SCAN COMPLETE"
```

A `SUSPECT` from `1c` is not automatically a FAIL — a four-line YAML fixture can be complete. It is a FAIL if the file is smaller than what its acceptance criterion describes. You must state, in your report, why the file is complete at that size.

### One narrow exception, so this rule does not contradict the rest of the manual

The **report and blocker templates** in this manual and in `manual/09-cost-and-context-discipline.md` §9.10–§9.11 contain bracketed fields such as `[task id from the card]`. Those are the templates' own fill-in form and you replace them with real values before you emit the report. They are never committed as file content. Nothing you commit to a lane branch may contain a bracketed fill-in field.

---

## 10.4 Runnable, not merely present — `DONE-CHECK 2`

A file that exists is not a deliverable. A file that **runs** is a deliverable. Run the check for each type you produced. Every one of these commands is copy-pasteable as written; substitute only the path.

First, resolve your Python once — do not assume `python3` exists on this machine:

```bash
# Resolve the interpreter. If this prints STOP, file a blocker; do not proceed and do not guess.
PY="$(command -v python3 || command -v python)"
[ -n "$PY" ] && echo "PY=$PY" || echo "STOP: no python interpreter on PATH. File a blocker."
```

### Python

```bash
# Syntax must compile. Non-zero exit = FAIL.
"$PY" -m py_compile "<absolute/path/to/file.py>"
echo "EXIT_CODE=$?"
```

```bash
# The module must import without side effects and without error.
"$PY" -c "import importlib.util,sys; s=importlib.util.spec_from_file_location('m',sys.argv[1]); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print('IMPORT OK')" "<absolute/path/to/file.py>"
echo "EXIT_CODE=$?"
```

### JSON (including JSON Schema files)

```bash
"$PY" -c "import json,sys; json.load(open(sys.argv[1],encoding='utf-8')); print('JSON OK')" "<absolute/path/to/file.json>"
echo "EXIT_CODE=$?"
```

### YAML (registries, schemas, workflows, product contracts)

```bash
"$PY" -c "import yaml,sys; d=yaml.safe_load(open(sys.argv[1],encoding='utf-8')); print('YAML OK, top-level keys:', sorted(d) if isinstance(d,dict) else type(d).__name__)" "<absolute/path/to/file.yaml>"
echo "EXIT_CODE=$?"
```

If that command fails with `ModuleNotFoundError: No module named 'yaml'`, that is **a blocker, not a fail** — the environment is wrong and you do not install packages on your own initiative (`manual/09-cost-and-context-discipline.md` §9.7 item 6). File the blocker with the literal error.

### Shell

```bash
bash -n "<absolute/path/to/file.sh>" && echo "SHELL SYNTAX OK"
echo "EXIT_CODE=$?"
```

### GitHub Actions workflow (L2 only)

```bash
set -euo pipefail
# Parse as YAML, then assert the three keys a workflow cannot function without.
"$PY" -c "
import yaml,sys
d=yaml.safe_load(open(sys.argv[1],encoding='utf-8'))
missing=[k for k in ('name','jobs') if k not in d]
# 'on' is parsed by PyYAML as the boolean True; check both spellings.
if 'on' not in d and True not in d: missing.append('on')
print('WORKFLOW MISSING KEYS:', missing if missing else 'none')
sys.exit(1 if missing else 0)
" "<absolute/path/to/workflow.yml>"
echo "EXIT_CODE=$?"
```

### The rule

> **Any non-zero exit code here is a FAIL, and a FAIL means the task is `BLOCKED`.** You do not "fix it in the next task." You do not edit the check to make it pass. You either fix the file so the unmodified check passes, or you report `BLOCKED` with the literal error.

---

## 10.5 Conformance to the conventions file

**Your taste is not a standard.** Naming, layout, header blocks, field ordering, error message shape, exit codes, indentation and file structure are decided by the conventions file, not by you.

### Step 1 — locate the conventions file. Do not assume its name.

```bash
set -euo pipefail
# Locate the conventions file. Do NOT hard-code a guessed filename.
M="C:/D_Drive/PS/MultiProduct/Code/implementation/master"
[ -d "$M" ] || { echo "STOP: master directory ${M} does not exist. File a blocker."; }
CONV="$(ls -1 "$M" | grep -iE 'convention' | head -1)"
if [ -n "$CONV" ]; then
  echo "CONVENTIONS FILE: ${M}/${CONV}"
  wc -l "${M}/${CONV}"
else
  echo "STOP: no conventions file found in ${M}. File a blocker. Do not invent a house style."
fi
```

If that prints `STOP:`, **stop.** Do not invent a convention. Do not copy the style of a neighbouring file — reading another lane's source tree to imitate it is a cross-lane read and is forbidden (`PARTITION.md` rule 4; `manual/09-cost-and-context-discipline.md` §9.3).

### Step 2 — extract every binding line and check yourself against each one

```bash
set -euo pipefail
# Print the binding lines from the conventions file: this file expresses its rules as
# **Correct:** / **Incorrect:** example pairs and section headings, not modal-verb sentences.
M="C:/D_Drive/PS/MultiProduct/Code/implementation/master"
CONV="$(ls -1 "$M" | grep -iE 'convention' | head -1)"
[ -n "$CONV" ] && grep -nE '\*\*(Correct|Incorrect)\b|^#{2,3} [0-9]' "${M}/${CONV}" \
  || echo "STOP: cannot extract binding lines — no conventions file. File a blocker."
```

### Step 3 — paste this table into your report, one row per binding line that applies to your file type

```text
CONVENTIONS CONFORMANCE
  source: [absolute path to the conventions file]
  | # | binding line (quoted from the conventions file) | my file | conforms? |
  |---|---|---|---|
  | 1 | "[verbatim quote]" | [path] | YES |
  | 2 | "[verbatim quote]" | [path] | YES |
```

Every row must read `YES`. A row reading `NO`, `N/A (assumed)`, or `partially` makes the task `BLOCKED`.

### Step 4 — the case the conventions file does not cover

If your file needs a decision the conventions file does not make — a field order it does not specify, an error format it does not define, a filename pattern it does not give — **that is a decision, and you have no authority to make decisions** (`PARTITION.md`: *No task may require designing, choosing, or interpreting. If a task needs judgment, it belongs to L0*).

Stop and file the blocker. Do not pick the option that "looks consistent". Consistency you invented is drift you introduced, and the reconciler will find it later at ten times the cost.

---

## 10.6 The narrowing test — the check that you did not quietly shrink the task

This is the section that catches the failure mode this manual exists for. You are highly likely to do the following without noticing:

- implement **one** of the things a criterion listed, because the rest "follow the same pattern"
- validate **one** field, because the schema has many and the first proved the mechanism
- handle the **happy path**, because the error path was not spelled out
- cover **one product**, when the criterion said *every product in the registry*
- write the **code**, when the criterion said *code and a fixture and a failing-case test*
- satisfy the criterion's **verb** (`add`) but not its **quantifier** (`for each`)

None of these feel like failures while you are doing them. All of them are failures. Here is the mechanical test that finds them.

### Step 1 — Quote every acceptance criterion verbatim. Do not paraphrase.

Paraphrasing is how narrowing happens. The moment you rewrite "a validator that rejects each of the four malformed cases" as "a validator that rejects malformed input", you have already shrunk the task by three cases and you will never notice.

### Step 2 — Underline every noun, every verb, and every quantifier.

- **Every noun** must map to a file that exists on your branch.
- **Every verb** must map to a command whose output proves the verb happened.
- **Every quantifier** — *each, every, all, both, N of, per, for every* — must map to a **count you produced with a command**, not a count you believe.

### Step 3 — Build the Criterion Coverage Table. Paste it in your report.

```text
CRITERION COVERAGE
  | # | criterion, QUOTED VERBATIM from the task card | artifact (absolute path) | proof command | result |
  |---|---|---|---|---|
  | 1 | "[verbatim]" | [path] | [command] | [pasted output, one line] |
  | 2 | "[verbatim]" | [path] | [command] | [pasted output, one line] |
```

A criterion with no artifact is not done. A criterion with no proof command is not done. A criterion whose proof command you did not run is not done.

### Step 4 — Run the quantifier check for every "each / every / all" in the criteria.

If a criterion contains a quantifier over a set, you must **count the set with a command** and **count your coverage with a command**, and the two numbers must match.

```bash
set -euo pipefail
# DONE-CHECK 3 — quantifier check.
# Example shape: criterion says "one schema file per registry in registries/".
# Substitute the two real directories from YOUR task card. Both numbers must match.
SRC="<absolute/path/to/the/set/the/criterion/names>"
OUT="<absolute/path/to/where/your/artifacts/went>"
[ -d "$SRC" ] || { echo "STOP: ${SRC} does not exist. File a blocker."; }
[ -d "$OUT" ] || { echo "STOP: ${OUT} does not exist. File a blocker."; }
a=$(ls -1 "$SRC" | wc -l); b=$(ls -1 "$OUT" | wc -l)
echo "SET SIZE=${a}  MY COVERAGE=${b}"
[ "$a" = "$b" ] && echo "QUANTIFIER CHECK: PASS" || echo "QUANTIFIER CHECK: FAIL — I covered ${b} of ${a}. Task is BLOCKED or incomplete."
```

If the set is enumerated inside a file rather than as a directory of files, count it there:

```bash
set -euo pipefail
# Count the enumerated cases in the criterion's source file, then count your handling of them.
"$PY" -c "
import yaml,sys
d=yaml.safe_load(open(sys.argv[1],encoding='utf-8'))
k=sys.argv[2]
v=d.get(k)
print('COUNT of', k, '=', len(v) if v is not None else 'KEY MISSING')
" "<absolute/path/to/source.yaml>" "<the key the criterion names>"
```

### Step 5 — The five narrowing patterns. Check yourself against each by name.

| Pattern | What it looks like | The test |
|---|---|---|
| **N1 — Pattern-proving** | "I implemented the first one; the rest are identical" | Did you write all N? Count them. |
| **N2 — Happy-path-only** | Error branch missing because the card described the success case in more detail | Does a deliberately malformed input produce a non-zero exit and a message? Run it. |
| **N3 — Verb substitution** | Card said *validate*; you wrote something that *parses* | Does your artifact **reject** bad input, or only accept good input? |
| **N4 — Deliverable dropping** | Card named code + fixture + test; you delivered code | Count the deliverables named in the card. Count the files on your branch. |
| **N5 — Scope re-quantification** | Card said *for every X*; you did it for the X in the example | Run the Step 4 quantifier check. |

### Step 6 — The single sentence that decides it

Write this sentence in your report, filled in, and check that it is literally true:

```text
NARROWING TEST: I implemented [N] of [N] acceptance criteria, at the full scope each
criterion states, and the artifacts covering them are [list every path]. I did not defer,
sample, or represent any part of any criterion.
```

If you cannot write that sentence truthfully, the status is `BLOCKED` and you name the criterion you could not fully meet and why (`manual/00-README-FOR-AI-DEVELOPERS.md` Rule 5: *Never round up*).

---

## 10.7 The remaining gates — `DONE-CHECK 4` and `DONE-CHECK 5`

### `DONE-CHECK 4` — self-verify, run and pasted

```bash
# Run the task card's self-verify command EXACTLY as written. Change nothing about it.
# Replace the line below with that command, character for character.
# [self-verify command from the task card]
echo "EXIT_CODE=$?"
```

Rules, restated because this is the gate most often faked:

- `EXIT_CODE=0` **and** the expected output present → PASS.
- Any other exit code, or output you cannot interpret unambiguously → **FAIL**, and the task is `BLOCKED`.
- The command not existing, or erroring on its own, is a **blocker**, not a fail (`manual/09-cost-and-context-discipline.md` §9.10).
- You may not modify the command to make it green. You may not substitute a different command. You may not paste output from before your last edit.
- You may not write "tests pass" from reading the code. Reasoning is not running.

> **Reporting a green result you did not observe is the most serious failure available to you on this build.** It is worse than writing broken code, because broken code is found by CI and a fabricated result is found by a customer.

### `DONE-CHECK 5` — scope, proven not asserted

```bash
set -euo pipefail
# Every line of this output must be inside YOUR lane's owned paths (PARTITION.md, table in §"The five build lanes").
git fetch origin integration --quiet
git diff --name-only origin/integration...HEAD
echo "---- read every line above against your lane's owned path prefixes ----"
```

If any line falls outside your owned prefixes, you have broken the partition. Revert that file before you go further:

```bash
git checkout origin/integration -- "<the foreign path>"
git diff --name-only origin/integration...HEAD
```

Do not open the PR and let `lane-guard` decide. A foreign-path PR burns a full review cycle from the one human integrator that five lanes share.

---

## 10.8 Before and after — worked examples

Each example is a real deliverable shape from this build. The **unacceptable** version is what an agent produces when it is optimising for looking finished. The **acceptable** version is what passes.

---

### Example A — a registry schema (L1, `schemas/registry/**`)

**Task card criterion, quoted:** *"Create a JSON Schema at `schemas/registry/people.schema.json` that requires each person entry to carry `id`, `display_name`, `roles` and `active`, rejects unknown properties, and rejects an entry missing any required field."*

#### UNACCEPTABLE — `schemas/registry/people.schema.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "TODO: set the canonical id",
  "title": "People registry",
  "type": "object",
  "properties": {
    "people": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "string" }
        }
      }
    }
  }
}
```

**Why this fails — six ways, and every one of them would have passed a glance:**

| Gate | Failure |
|---|---|
| G2 | `"$id": "TODO: ..."` — hard-banned token **and** a placeholder value |
| G1 | Three of the four required properties (`display_name`, `roles`, `active`) are simply absent — **narrowing pattern N1**, pattern-proving |
| G1 | `required` is missing entirely, so the criterion "rejects an entry missing any required field" is not implemented at all |
| G1 | `additionalProperties` is missing, so "rejects unknown properties" is not implemented — **narrowing pattern N3**, verb substitution: this schema *describes*, it does not *reject* |
| G3 | Never validated against anything; no evidence it rejects anything |
| G5 | The report would have said "schema created" — true, and irrelevant |

#### ACCEPTABLE — `schemas/registry/people.schema.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  # NEEDS_URN (FD-050): replace with urn:multiproduct:schemas:<type>:<version>
  "$id": "https://control-plane.internal/schemas/registry/people.schema.json",
  "title": "People registry",
  "type": "object",
  "additionalProperties": false,
  "required": ["schema_version", "people"],
  "properties": {
    "schema_version": { "type": "integer", "minimum": 1 },
    "people": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["id", "display_name", "roles", "active"],
        "properties": {
          "id": { "type": "string", "pattern": "^[a-z0-9][a-z0-9-]{1,38}[a-z0-9]$" },
          "display_name": { "type": "string", "minLength": 1 },
          "roles": {
            "type": "array",
            "minItems": 1,
            "items": { "type": "string", "minLength": 1 },
            "uniqueItems": true
          },
          "active": { "type": "boolean" }
        }
      }
    }
  }
}
```

**Note the `$id` value.** It is acceptable **only because the task card supplied it**. If your card does not give you the canonical `$id`, you do not invent one and you do not write `TODO` — you file a blocker, because a schema identifier is a decision and decisions belong to L0.

**And the acceptable deliverable is not only the schema.** The criterion says *rejects*. So you also produce the evidence that it rejects, by running it against both a valid and a deliberately invalid document:

```bash
set -euo pipefail
PY="$(command -v python3 || command -v python)"
"$PY" - <<'PYEOF'
import json, sys
from jsonschema import Draft202012Validator
schema = json.load(open("schemas/registry/people.schema.json", encoding="utf-8"))
Draft202012Validator.check_schema(schema)
v = Draft202012Validator(schema)

good = {"schema_version": 1, "people": [
    {"id": "a-person", "display_name": "A Person", "roles": ["developer"], "active": True}]}
missing_field = {"schema_version": 1, "people": [
    {"id": "a-person", "display_name": "A Person", "roles": ["developer"]}]}
unknown_prop = {"schema_version": 1, "people": [
    {"id": "a-person", "display_name": "A Person", "roles": ["developer"],
     "active": True, "salary": 1}]}

print("VALID DOC ERRORS   :", len(list(v.iter_errors(good))))
print("MISSING-FIELD ERRORS:", len(list(v.iter_errors(missing_field))))
print("UNKNOWN-PROP ERRORS :", len(list(v.iter_errors(unknown_prop))))
sys.exit(0 if (not list(v.iter_errors(good))
               and list(v.iter_errors(missing_field))
               and list(v.iter_errors(unknown_prop))) else 1)
PYEOF
echo "EXIT_CODE=$?"
```

Expected, and what you paste:

```text
VALID DOC ERRORS   : 0
MISSING-FIELD ERRORS: 1
UNKNOWN-PROP ERRORS : 1
EXIT_CODE=0
```

**That output is the deliverable as much as the schema is.** A schema with no rejection evidence is an assertion; a schema with rejection evidence is a fact.

---

### Example B — a validator (L1, `validators/registry/**`)

**Task card criterion, quoted:** *"Add `validators/registry/validate_people.py`. It takes one argument, the path to the people registry file. It exits `0` when the file conforms to `schemas/registry/people.schema.json` and exits `1` with a message naming the file and the first failing field when it does not. It must not hard-code any person, role or count."*

#### UNACCEPTABLE — `validators/registry/validate_people.py`

```python
"""Validate the people registry."""
import sys

KNOWN_ROLES = ["founder", "team_lead", "developer"]   # keep in sync with roles.yaml


def validate(path):
    # TODO: load the schema and validate properly
    return True


if __name__ == "__main__":
    validate(sys.argv[1])
```

**Why this fails:**

| Gate | Failure |
|---|---|
| G2 | `# TODO` — hard-banned token |
| G2 | `validate()` returns `True` unconditionally: an empty body wearing a costume. It validates nothing and can never fail |
| G1 | The exit-code contract (`0` / `1`) is not implemented — `sys.exit` is never called, so **every** input, valid or not, exits `0` |
| G1 | "a message naming the file and the first failing field" — absent entirely |
| G1 | `KNOWN_ROLES` hard-codes roles, which the criterion explicitly forbids and which the programme forbids everywhere (`manual/00-README-FOR-AI-DEVELOPERS.md` §2: *no hard-coding of people, counts, products, stacks or providers*) |
| G6 | The self-verify command would exit `0` against a **broken** registry, and an agent pasting that `0` would report a green result that means nothing |

That last row is the important one. This file does not merely fail to work — **it fails in the direction that looks like success.** That is what a plausible-looking stub is.

#### ACCEPTABLE — `validators/registry/validate_people.py`

```python
"""Validate a people registry file against schemas/registry/people.schema.json.

Usage:
    python validators/registry/validate_people.py <path-to-people.yaml>

Exit codes:
    0  the document conforms
    1  the document does not conform (first failure is printed)
    2  the validator could not run (missing file, unreadable schema, bad YAML)
"""
import json
import pathlib
import sys

import yaml
from jsonschema import Draft202012Validator

SCHEMA_PATH = pathlib.Path(__file__).resolve().parents[2] / "schemas" / "registry" / "people.schema.json"


def load_schema(schema_path):
    if not schema_path.is_file():
        print(f"validate_people: schema not found: {schema_path}", file=sys.stderr)
        raise SystemExit(2)
    with schema_path.open(encoding="utf-8") as fh:
        schema = json.load(fh)
    Draft202012Validator.check_schema(schema)
    return schema


def load_document(doc_path):
    if not doc_path.is_file():
        print(f"validate_people: registry file not found: {doc_path}", file=sys.stderr)
        raise SystemExit(2)
    try:
        with doc_path.open(encoding="utf-8") as fh:
            return yaml.safe_load(fh)
    except yaml.YAMLError as exc:
        print(f"validate_people: {doc_path}: not valid YAML: {exc}", file=sys.stderr)
        raise SystemExit(2)


def main(argv):
    if len(argv) != 2:
        print("validate_people: exactly one argument required: <path-to-people.yaml>", file=sys.stderr)
        return 2
    doc_path = pathlib.Path(argv[1]).resolve()
    schema = load_schema(SCHEMA_PATH)
    document = load_document(doc_path)

    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(document), key=lambda e: list(e.absolute_path))
    if not errors:
        print(f"validate_people: OK: {doc_path}")
        return 0

    first = errors[0]
    field = ".".join(str(p) for p in first.absolute_path) or "<document root>"
    print(f"validate_people: FAIL: {doc_path}: field '{field}': {first.message}", file=sys.stderr)
    print(f"validate_people: {len(errors)} error(s) total", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

**Why this passes:** no banned tokens; no empty bodies; both exit paths implemented and distinguishable; a third exit code for "could not run", so a broken environment can never be mistaken for a passing validation; the error message names the file and the first failing field exactly as the criterion required; and **not one person, role, product or count is hard-coded** — every fact comes from the schema and the document.

**And the evidence, run and pasted:**

```bash
set -euo pipefail
PY="$(command -v python3 || command -v python)"
# The valid case must exit 0.
"$PY" validators/registry/validate_people.py registries/people.yaml
echo "VALID_EXIT=$?"
# The invalid case must exit 1. Build it in a scratch file; never mutate the real registry.
printf 'schema_version: 1\npeople:\n  - id: a-person\n    display_name: A Person\n' > /tmp/people-bad.yaml
"$PY" validators/registry/validate_people.py /tmp/people-bad.yaml
echo "INVALID_EXIT=$?"
```

Both numbers go in the report. `VALID_EXIT=0` alone is **not** evidence the validator works — it is equally consistent with a validator that returns `0` for everything, which is exactly the unacceptable version above. **A validator is only proven by a failing case.**

---

### Example C — the completion report

The deliverable is not only the code. The report is a deliverable, and a false report is a defect with a wider blast radius than any code you will write on this build.

#### UNACCEPTABLE

```text
STATUS: DONE
TASK: L1-F3-04
Created the people schema and validator. Tests pass. The validator follows the
same pattern as the other validators. Also noticed the roles schema has a typo
so I fixed that too while I was in there.
```

**Why this fails:** "Tests pass" with no command and no output — an unrun claim (G6). "Follows the same pattern as the other validators" — a cross-lane read that was not permitted, and a conventions claim with no conventions citation (G4). "Fixed that too" — scope violation (G7); the correct response to an adjacent defect is to **note it and leave it** (`manual/09-cost-and-context-discipline.md` §9.7 item 2). No criterion table, so nobody can tell whether the task was narrowed (G1, G5). This report is shorter to write and it destroys the entire value of the review.

#### ACCEPTABLE

```text
STATUS: DONE
TASK: L1-F3-04
LANE: L1
BRANCH: lane/1/f3-04-people-registry-schema

FILES CHANGED (complete list, absolute paths):
  <repo>/schemas/registry/people.schema.json     created
  <repo>/validators/registry/validate_people.py  created

CRITERION COVERAGE
  | # | criterion, quoted verbatim | artifact | proof command | result |
  |---|---|---|---|---|
  | 1 | "requires id, display_name, roles and active" | schemas/registry/people.schema.json | the four-case validation script in the task card | MISSING-FIELD ERRORS: 1 |
  | 2 | "rejects unknown properties" | schemas/registry/people.schema.json | same script | UNKNOWN-PROP ERRORS: 1 |
  | 3 | "exits 0 on conforming input" | validators/registry/validate_people.py | python validators/registry/validate_people.py registries/people.yaml | VALID_EXIT=0 |
  | 4 | "exits 1 with a message naming the file and the first failing field" | validators/registry/validate_people.py | python validators/registry/validate_people.py /tmp/people-bad.yaml | validate_people: FAIL: /tmp/people-bad.yaml: field 'people.0': 'active' is a required property / INVALID_EXIT=1 |
  | 5 | "must not hard-code any person, role or count" | both files | grep -nE "founder|team_lead|developer|\[[0-9]+\]" on both changed files | no matches |

NARROWING TEST: I implemented 5 of 5 acceptance criteria, at the full scope each
criterion states, and the artifacts covering them are schemas/registry/people.schema.json
and validators/registry/validate_people.py. I did not defer, sample, or represent any
part of any criterion.

CONVENTIONS CONFORMANCE
  source: C:/D_Drive/PS/MultiProduct/Code/implementation/master/09-glossary-and-conventions.md
  | # | binding line | my file | conforms? |
  |---|---|---|---|
  | 1 | "[verbatim quote]" | validators/registry/validate_people.py | YES |
  | 2 | "[verbatim quote]" | schemas/registry/people.schema.json | YES |

DONE-CHECK 1 (banned tokens): SCAN COMPLETE, no FAIL lines.
DONE-CHECK 2 (runnable): py_compile EXIT_CODE=0; JSON OK.

SELF-VERIFY:
  command: [exact command from the card]
  exit code: [observed exit code, must be 0]
  output: [pasted, unedited]

SCOPE: git diff --name-only origin/integration...HEAD printed exactly the two files
above. Both are under schemas/registry/** and validators/registry/**, owned by L1.

OBSERVED BUT NOT FIXED (out of scope, for L0 triage):
  schemas/registry/roles.schema.json line 14 appears to have a misspelled property
  name ("desciption"). It is in my lane but not in my task card. I did not change it.
```

Note the last block. Seeing the typo was good. **Not fixing it was also good.** Reporting it is the complete and correct response.

---

## 10.9 What is NOT evidence that you are done

Every line below has been used by an agent on some build to justify a `DONE` it had not earned. None of them counts.

1. "The code looks correct." — Looking is not running.
2. "The tests should pass." — Should is not did.
3. "It follows the same pattern as the existing implementation." — You were not permitted to read the existing implementation, and the pattern is not the criterion.
4. "CI will catch it if it's wrong." — CI is a backstop for the unforeseen, not a substitute for your verification. Also, CI is queued behind four other lanes.
5. "The remaining part is trivial." — Then it is done, and you did it. If it is not done, it is not trivial; it is missing.
6. "I left a TODO so it won't be forgotten." — It will be forgotten. §95.4: *stubbed gates have a habit of staying stubbed.*
7. "The task card probably meant the simpler version." — Probably is a guess, and guessing is a STOP (`manual/09-cost-and-context-discipline.md` §9.9, tripwire T10).
8. "I ran a similar command and it worked." — Similar is not the same. Run the exact one.
9. "It passed before my last edit." — Then it is unverified now.
10. "The file exists." — Existence is not function.
11. "I verified it by reading the output format in the docs." — Reading is not running.
12. "It's 95% done." — There is no 95%. There is `DONE` and there is `BLOCKED`.

---

## 10.10 The done gate — run this whole block before you report anything

Copy this block whole. Substitute only your lane's owned path prefixes and your card's self-verify command. Every line of output goes in your report.

```bash
set -euo pipefail
# ============ THE DONE GATE ============
# Run from the repository root. Stop at the first FAIL.
PY="$(command -v python3 || command -v python)"
[ -n "$PY" ] || { echo "STOP: no python interpreter. File a blocker."; }

echo "=== G7 SCOPE ==="
git fetch origin integration --quiet
git diff --name-only origin/integration...HEAD

echo "=== G2 BANNED TOKENS ==="
git diff --name-only origin/integration...HEAD | while IFS= read -r f; do
  [ -f "$f" ] || continue
  grep -nEI 'TODO|FIXME|XXX|HACK|TBD|PLACEHOLDER|CHANGEME|FILL_?ME|fill-me|NotImplemented|implement later|wire this up|for now|temporary|<REPLACE>|your-(org|value)|my-product|example\.(com|org)|\bfoo\b|\bbar\b|\bbaz\b|lorem ipsum|\basdf\b|v?0\.0\.0|0000000|xxxxxxxx' "$f" \
    && echo "  ^^ FAIL: banned token in $f" || true
done
echo "banned-token scan complete"

echo "=== G2 EMPTY BODIES ==="
git diff --name-only origin/integration...HEAD | grep -E '\.(py|sh|json|yaml|yml)$' | while IFS= read -r f; do
  [ -f "$f" ] || continue
  grep -nE '^[[:space:]]*(pass|\.\.\.|return|return None)[[:space:]]*$|"(properties|required)"[[:space:]]*:[[:space:]]*(\{\}|\[\])' "$f" && echo "  ^^ FAIL: empty body in $f" || true
done
echo "empty-body scan complete"

echo "=== G3 RUNNABLE ==="
git diff --name-only origin/integration...HEAD | while IFS= read -r f; do
  [ -f "$f" ] || continue
  case "$f" in
    *.py)         "$PY" -m py_compile "$f" && echo "PY OK   $f" || echo "FAIL    $f" ;;
    *.json)       "$PY" -c "import json,sys;json.load(open(sys.argv[1],encoding='utf-8'))" "$f" && echo "JSON OK $f" || echo "FAIL    $f" ;;
    *.yaml|*.yml) "$PY" -c "import yaml,sys;yaml.safe_load(open(sys.argv[1],encoding='utf-8'))" "$f" && echo "YAML OK $f" || echo "FAIL    $f" ;;
    *.sh)         bash -n "$f" && echo "SH OK   $f" || echo "FAIL    $f" ;;
    *)            echo "NO CHECK DEFINED FOR $f — state in your report why this file needs none" ;;
  esac
done

echo "=== G6 SELF-VERIFY ==="
# Replace the line below with the task card's self-verify command, character for character.
# [self-verify command from the task card]
echo "EXIT_CODE=$?"
echo "=== DONE GATE COMPLETE ==="
```

**Reading the result:** any line containing `FAIL`, any non-zero `EXIT_CODE`, or any path in the scope section outside your owned prefixes means the status is `BLOCKED`. You do not interpret, soften, or average these. They are binary.

---

## 10.11 Quick card — keep this in front of you

```text
DONE MEANS                                    DONE DOES NOT MEAN
--------------------------------------------------------------------------------
All N criteria met, at full scope.            Most of them, the pattern proven.
Every file runs today.                        Every file exists and looks right.
Zero TODO / placeholder / empty body.         A note explaining what is left.
Conventions file cited, row by row.           Style that looks consistent to me.
Quantifiers counted with a command.           "Each" handled for the example.
Self-verify run this session, output pasted.  "Tests pass."
Failing case proven to fail.                  Happy case proven to pass.
Scope diff read line by line.                 lane-guard will tell me.
Strays noted, not fixed.                      Fixed it while I was in there.
Otherwise: BLOCKED, with evidence.            Otherwise: DONE with caveats.
```

**Three sentences to remember when everything else has fallen out of context:**

1. A file you write is finished today or it is not written today — there are no sketches, no `TODO`s, and no placeholder values on this build.
2. Prove you did the **whole** task by quoting every criterion verbatim and counting every quantifier with a command; a criterion you paraphrased is a criterion you shrank.
3. `DONE` requires pasted output from commands you actually ran this session; anything less is `BLOCKED`, and `BLOCKED` is a successful, cheap, respected outcome.
