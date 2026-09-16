# L0-03 — THE MERGE TRAIN (operational procedure)

**Lane:** L0 Integrator · **Branches:** `main`, `integration` (PARTITION.md §"Branch & merge model")
**Executor:** the human lead. Every command below is run by a person, not by an AI developer.
**Owns exclusively:** `contracts/**`, `CODEOWNERS`, `docs/**`, root files, `Makefile` (PARTITION.md §"The five build lanes")
**Spec:** `C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md` (v4.0)
**Frozen partition:** `C:/D_Drive/PS/MultiProduct/Code/implementation/PARTITION.md` — nothing here contradicts it.
**Upstream in this lane:** `L0-00-charter.md` §9 states the merge train in five lines. This file is those five lines
turned into an operational procedure with literal commands, failure branches and records.

> **Reading rule for lanes L1–L5.** Sections 4, 6, 7 and 10 are the only parts binding on a lane executor:
> what "rebased" means, what the integration gate is, what a rebase directive obliges you to do, and the fact that
> being skipped is never recorded as your fault. Everything else is work the human lead performs. A lane
> **never** runs the merge, the promotion or the rollback commands in this file (PARTITION.md §"Branch & merge
> model": *"A lane NEVER merges another lane's branch. A lane NEVER rebases another lane's branch."*).

---

## 1. Shell and repository conventions

POSIX `sh` / Git Bash, run from the control-plane repository root. Identical to `L0-00-charter.md` §1.

**Commands**

```bash
set -euo pipefail
export CP_ROOT="$HOME/src/control-plane"
export CPR_ROOT="$HOME/src/control-plane-records"
cd "$CP_ROOT"
git rev-parse --show-toplevel
gh auth status
```

| Symbol | Meaning | Set by |
|---|---|---|
| `$CP_ROOT` | local clone of `control-plane` | you, once per shell |
| `$CYCLE` | zero-padded three-digit cycle number, e.g. `007` | task L0-03-03 |
| `$LANE` | `1`..`5`, never `0` — L0 does not ride its own train | per lane, in the cycle loop |
| `$PR` | GitHub pull-request number of the lane PR under consideration | task L0-03-04 |

Two repositories exist and are not interchangeable (PARTITION.md §"Repositories"). **The merge train runs on
`control-plane` only.** `control-plane-records` has no review protection and no merge train; it is written by the
records-writer credential one file per event (D89, spec L10182; D107, spec L10205) and L4's work there lands
outside this procedure. When a cycle's L4 slot says `MERGED`, it refers to L4's `control-plane` paths —
`schemas/records/**`, `metrics/**`, `tools/records/**` — and nothing else.

---

## 2. The ordered cycle, and why the order is what it is

**Frozen order, once per cycle: `L1 → L4 → L2 → L3 → L5`.** Any deviation is L0D-07 and requires a decision
record; there is no informal reordering.

| Position | Lane | Subsystems | Why here | PARTITION.md anchor |
|---|---|---|---|---|
| 1 | **L1** Registries & Contracts | A, B | Produces the registry and product schemas everything else validates against. If L1's schemas land after a consumer, the consumer's own SELF-VERIFY has been proved against a schema that no longer exists on `integration` | §"Dependency order": *"L1 (schemas) and L4 (record schemas) produce what everything validates against"* |
| 2 | **L4** Records, Events & Metrics | I, N | The other producer of things-validated-against: record and event schemas. Placed second, not first, because L4's `control-plane` surface is smaller and its `control-plane-records` surface does not ride the train at all | same |
| 3 | **L2** Pipeline & Evidence | E, F | Consumes L1 schemas: the workflows that emit the required status checks call L1's validators. A workflow merged before its validator exists is a required check that nothing can satisfy — exactly the failure §98.2 Phase 1 names (*"A required check no workflow emits blocks every pull request indefinitely"*, spec L9017) | §"Dependency order": *"L2 (workflows) consumes L1 schemas"* |
| 4 | **L3** Reconciler & Provisioning | C, D | Consumes L1 plus the L5 access model. Third-position-from-last because it reads both producers and the access declarations | §"Dependency order": *"L3 (reconciler) consumes L1 + L5 access model"* |
| 5 | **L5** Access, Infra & Ops | K, L, M, Q, R | Independent at build time; integrates last so that a protection or ruleset change never lands under a half-merged cycle | §"Dependency order": *"L5 (access/infra) is independent at build time, integrates last"* |

**The order is a sequence, not a chain.** Position 4 does not depend on position 3 having merged *this cycle* — it
depends on the *contract*, and `contracts/**` was frozen in Phase 0 (PARTITION.md rule 2). This is the technical
reason the starvation rule of §10 is safe: no lane consumes another lane's source tree (PARTITION.md rule 4), so a
lane skipped at position 1 cannot invalidate a merge at position 5.

**Cadence.** One cycle per week, Wednesday (`L0-00-charter.md` §8.2). A second mid-week cycle is permitted and is
not a deviation; running the lanes out of order inside a cycle is.

---

## 3. Tasks in this file

| Task id | Title | Size | Depends on |
|---|---|---|---|
| L0-03-01 | Install the train toolchain and the cycle-log store | M | L0-00-04, L0-00-08, L0-00-09 |
| L0-03-02 | Publish the TRAIN HALT record template | S | L0-00-05, L0-03-01 |
| L0-03-03 | Open the cycle — preflight, base freeze, candidate enumeration | S | L0-03-01, L0-03-02 |
| L0-03-04 | Admission check for one lane | M | L0-03-03 |
| L0-03-05 | A lane behind on rebase — the rebase directive | M | L0-03-04 |
| L0-03-06 | Merge the admitted lane PR and re-verify `integration` | M | L0-03-04 |
| L0-03-07 | A lane PR that fails the integration gate | M | L0-03-04 |
| L0-03-08 | Close the cycle and regenerate the log | S | L0-03-06 |
| L0-03-09 | Promote `integration → main` under the full gate | L | L0-03-08 |
| L0-03-10 | Roll back a bad `integration` merge | M | L0-03-06 |
| L0-03-11 | Roll back a bad promotion on `main` | M | L0-03-09 |
| L0-03-12 | Starvation accounting and the constraint diagnosis | M | L0-03-08 |

Dependency graph:

```
L0-00-04 ─┐
L0-00-08 ─┼── L0-03-01 ── L0-03-02 ── L0-03-03 ── L0-03-04 ─┬── L0-03-05
L0-00-09 ─┘                                                     ├── L0-03-06 ─┬── L0-03-08 ─┬── L0-03-09 ── L0-03-11
                                                                 │              │              └── L0-03-12
                                                                 └── L0-03-07  └── L0-03-10
```

---

### L0-03-01 — Install the train toolchain and the cycle-log store

**Size:** M · **Dependencies:** L0-00-04 (`lane-guard.sh`, `Makefile`), L0-00-08 (`docs/merge-train.md`), L0-00-09 (rehearsal passed)

Four root scripts and four Makefile targets. Root files and `docs/**` are L0-owned (PARTITION.md §"The five build
lanes"), and root files resolve to lane `0` through the final catch-all rule of `lane-paths.tsv` (L0-00-03).

The cycle log is **one file per cycle**, never a shared appended file, for the same reason PARTITION.md rule 3
gives: *"No shared mutable file, ever … Directory-per-item only."* The table inside `docs/merge-train.md` is
**generated** from those files by `make train-log` and is never hand-edited, per invariant 46 (spec L9514:
*"Derived data is computed, never hand-maintained."*).

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
git checkout integration && git pull --ff-only
mkdir -p docs/merge-train/cycles

cat > train-owners.sh <<'OWN'
#!/usr/bin/env sh
# train-owners.sh — L0-owned. Every path in a range must resolve to an ASSIGNED lane.
# Used by the promotion gate, where the diff spans all five lanes and lane-guard.sh
# (which checks one lane at a time) cannot be applied.
# Usage: ./train-owners.sh <base-ref> <head-ref>
set -eu
BASE="${1:?base ref required}"; HEAD="${2:?head ref required}"
MAP="$(dirname "$0")/lane-paths.tsv"
if [ ! -f "$MAP" ]; then echo "TRAIN-OWNERS FAIL: lane-paths.tsv missing"; exit 2; fi

owner_of() {
  _f="$1"; _own=""
  while IFS='	' read -r _lane _pat; do
    case "$_lane" in ''|\#*) continue ;; esac
    # shellcheck disable=SC2254
    case "$_f" in $_pat) _own="$_lane"; break ;; esac
  done < "$MAP"
  echo "${_own:-X}"
}

VIOL=0
for f in $(git diff --name-only "$BASE"..."$HEAD"); do
  o=$(owner_of "$f")
  if [ "$o" = "X" ]; then
    echo "TRAIN-OWNERS VIOLATION: $f is an UNASSIGNED path (L0D-04)"
    VIOL=$((VIOL+1))
  fi
done

if [ "$VIOL" -eq 0 ]; then echo "TRAIN-OWNERS OK"; exit 0; fi
echo "TRAIN-OWNERS FAIL: $VIOL unassigned path(s)"
exit 1
OWN
chmod +x train-owners.sh

cat > train-admit.sh <<'ADM'
#!/usr/bin/env sh
# train-admit.sh — L0-owned. Admission check for ONE lane PR in the current cycle.
# Prints exactly one line ending in verdict=ADMIT|REBASE|GATE-FAIL|HALT.
# Usage: ./train-admit.sh <lane 1..5> <pr-number>
set -eu
LANE="${1:?lane 1..5 required}"; PR="${2:?pr number required}"
MAXAGE_H=24   # initial value; the "< 1 day old" rule of PARTITION.md. Changing it is L0D-07.

git fetch --prune origin >/dev/null 2>&1

BR=$(gh pr view "$PR" --json headRefName -q .headRefName)
BASEREF=$(gh pr view "$PR" --json baseRefName -q .baseRefName)
DRAFT=$(gh pr view "$PR" --json isDraft -q .isDraft)
MSTATE=$(gh pr view "$PR" --json mergeStateStatus -q .mergeStateStatus)

case "$BR" in lane/"$LANE"/*) PFX=YES ;; *) PFX=NO ;; esac

if git merge-base --is-ancestor origin/integration "origin/$BR" 2>/dev/null
then REB=YES; else REB=NO; fi

NOW=$(date +%s)
TIP=$(git log -1 --format=%ct "origin/$BR")
AGE=$(( (NOW - TIP) / 3600 ))

GUARD=$(./lane-guard.sh "$LANE" origin/integration "origin/$BR" 2>&1 | tail -1)
case "$GUARD" in "LANE-GUARD OK") G=OK ;; *) G=FAIL ;; esac

CHKOUT=$(gh pr checks "$PR" --required 2>&1) && CHK=PASS || CHK=FAIL
case "$CHKOUT" in
  *"no checks reported"*|*"no required checks"*|*"No checks reported"*) CHK=ABSENT ;;
esac

V=GATE-FAIL
if [ "$BASEREF" != "integration" ] || [ "$PFX" = "NO" ]; then
  V=HALT
elif [ "$REB" = "NO" ] || [ "$MSTATE" = "BEHIND" ] || [ "$AGE" -gt "$MAXAGE_H" ]; then
  V=REBASE
elif [ "$G" = "OK" ] && [ "$DRAFT" = "false" ] && [ "$MSTATE" = "CLEAN" ] \
     && [ "$CHK" = "PASS" ]; then
  V=ADMIT
fi

printf 'lane=%s pr=%s branch=%s base=%s draft=%s rebased=%s age_h=%s guard=%s checks=%s mergestate=%s verdict=%s\n' \
  "$LANE" "$PR" "$BR" "$BASEREF" "$DRAFT" "$REB" "$AGE" "$G" "$CHK" "$MSTATE" "$V"
ADM
chmod +x train-admit.sh

cat > train-row.sh <<'ROW'
#!/usr/bin/env sh
# train-row.sh — L0-owned. Renders one cycle record as one markdown table row.
set -eu
F="${1:?cycle file required}"
val() { awk -F'\t' -v k="$1" '$1==k{print $2; exit}' "$F"; }
lane() { v=$(awk -F'\t' -v k="$1" '$1==k{print $2; exit}' "$F"); echo "${v:-NONE}"; }
printf '| %s | %s | %s | %s | %s | %s | %s | %s | %s |\n' \
  "$(val cycle)" "$(val date)" \
  "$(lane L1)" "$(lane L4)" "$(lane L2)" "$(lane L3)" "$(lane L5)" \
  "$(val promoted)" "$(val notes)"
ROW
chmod +x train-row.sh

cat > train-freeze-window.sh <<'FRZ'
#!/usr/bin/env sh
# train-freeze-window.sh — L0-owned. Friday 15:00 deployment freeze (Section 94.8, spec L8586).
# Prints FREEZE-WINDOW OPEN or FREEZE-WINDOW CLOSED. Exit 0 open, 1 closed.
set -eu
DOW=$(date +%u); HOUR=$(date +%H)
if [ "$DOW" -gt 5 ] || { [ "$DOW" -eq 5 ] && [ "$HOUR" -ge 15 ]; }; then
  echo "FREEZE-WINDOW CLOSED"; exit 1
fi
echo "FREEZE-WINDOW OPEN"; exit 0
FRZ
chmod +x train-freeze-window.sh
```

Append the train targets to the L0-owned `Makefile` written by L0-00-04. **Append — do not rewrite the file**;
the existing `lane-guard`, `train`, `freeze` and `promote-check` targets stay exactly as authored.

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
cat >> Makefile <<'MK'

# --- merge train (L0-03) ---
.PHONY: train-preflight train-log train-owners promote-gate

train-preflight:
	@git fetch --prune origin >/dev/null 2>&1
	@test -z "$$(git status --porcelain)" || { echo "PREFLIGHT FAIL: working tree dirty"; exit 1; }
	@test "$$(git rev-parse HEAD)" = "$$(git rev-parse origin/integration)" \
	  || { echo "PREFLIGHT FAIL: not on integration tip"; exit 1; }
	@$(MAKE) --no-print-directory promote-check
	@echo "PREFLIGHT OK"

train-owners:
	@./train-owners.sh $(BASE) $(HEAD)

train-log:
	@test -f docs/merge-train.md || { echo "TRAIN-LOG FAIL: runbook missing"; exit 1; }
	@grep -q '<!-- CYCLE-LOG:BEGIN -->' docs/merge-train.md \
	  || { echo "TRAIN-LOG FAIL: BEGIN marker missing"; exit 1; }
	@{ awk '{print} /<!-- CYCLE-LOG:BEGIN -->/{exit}' docs/merge-train.md; \
	   printf '| cycle | date | L1 | L4 | L2 | L3 | L5 | promoted | notes |\n'; \
	   printf '|---|---|---|---|---|---|---|---|---|\n'; \
	   for f in $$(ls docs/merge-train/cycles/cycle-*.tsv 2>/dev/null | LC_ALL=C sort); do \
	     ./train-row.sh "$$f"; \
	   done; \
	   awk '/<!-- CYCLE-LOG:END -->/{f=1} f{print}' docs/merge-train.md; \
	 } > docs/merge-train.md.new
	@mv docs/merge-train.md.new docs/merge-train.md
	@echo "TRAIN-LOG OK"

promote-gate:
	@./train-promote-gate.sh $(CYCLE)
MK
```

> **Note:** The `promote-gate` Makefile target added here invokes `./train-promote-gate.sh`, which is not created until **L0-03-09**. Running `make promote-gate` before T09 completes will fail with a missing-script error. This is expected — the target becomes operational only after T09.

Insert the two generator markers into `docs/merge-train.md`, immediately **replacing** the hand-written cycle-log
table that L0-00-08 placed there (criterion 5 of L0-00-08 required the header line; `make train-log` now emits
that same header between the markers, so the criterion still holds).

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
python - <<'PY'
import io, re, sys
p = "docs/merge-train.md"
s = io.open(p, encoding="utf-8").read()
hdr = "| cycle | date | L1 | L4 | L2 | L3 | L5 | promoted | notes |"
if "<!-- CYCLE-LOG:BEGIN -->" not in s:
    i = s.find(hdr)
    if i < 0:
        sys.exit("cycle-log header not found in docs/merge-train.md — re-run L0-00-08")
    # j skips the two header lines (column names + separator)
    j = s.index('\n', i) + 1   # end of first header line
    j = s.index('\n', j) + 1   # end of separator line
    s = s[:i] + "<!-- CYCLE-LOG:BEGIN -->\n<!-- CYCLE-LOG:END -->\n" + s[j:]
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("MARKERS OK")
PY

make train-log
git add Makefile train-owners.sh train-admit.sh train-row.sh train-freeze-window.sh docs/merge-train.md
git commit -m "L0-03-01: merge-train toolchain and generated cycle log"
git push origin integration
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | All four scripts are executable | `for s in train-owners train-admit train-row train-freeze-window; do test -x ./$s.sh \|\| echo "NOTEXEC $s"; done; echo DONE` | `DONE` with no `NOTEXEC` line |
| 2 | The cycle store exists and is empty | `ls docs/merge-train/cycles \| wc -l` | `0` |
| 3 | `train-owners.sh` passes a fully-assigned diff | `./train-owners.sh integration integration` | `TRAIN-OWNERS OK` |
| 4 | `train-owners.sh` fails an unassigned path | see SELF-VERIFY case U | `TRAIN-OWNERS FAIL: 1 unassigned path(s)` |
| 5 | Both log markers present and in order | `grep -n 'CYCLE-LOG:BEGIN\|CYCLE-LOG:END' docs/merge-train.md \| cut -d: -f1 \| tr '\n' ' '` | two ascending integers |
| 6 | `make train-log` is idempotent | `make train-log >/dev/null; a=$(sha256sum docs/merge-train.md); make train-log >/dev/null; b=$(sha256sum docs/merge-train.md); [ "$a" = "$b" ] && echo STABLE` | `STABLE` |
| 7 | The freeze-window script answers with one of two strings | `./train-freeze-window.sh; echo "rc=$?"` | `FREEZE-WINDOW OPEN` + `rc=0`, or `FREEZE-WINDOW CLOSED` + `rc=1` |
| 8 | The L0-00-04 targets survived the append | `make train \| head -1` | `MERGE TRAIN ORDER (FROZEN): L1 -> L4 -> L2 -> L3 -> L5` |
| 9 | The L0-00-08 cycle-log header still present | `grep -c 'cycle | date | L1 | L4 | L2 | L3 | L5' docs/merge-train.md` | `1` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP_ROOT"
git checkout -b tmp/train-selftest integration
mkdir -p unassigned/tree && echo u > unassigned/tree/probe.txt
git add -A && git commit -q -m "unassigned probe"
U=$(./train-owners.sh integration HEAD | tail -1)
git checkout -q integration && git branch -D tmp/train-selftest >/dev/null

make train-log >/dev/null
A=$(sha256sum docs/merge-train.md | cut -d' ' -f1)
make train-log >/dev/null
B=$(sha256sum docs/merge-train.md | cut -d' ' -f1)

printf 'exec=%s cycles=%s unassigned=[%s] stable=%s train=%s header=%s\n' \
  "$(for s in train-owners train-admit train-row train-freeze-window; do test -x ./$s.sh && echo x; done | wc -l | tr -d ' ')" \
  "$(ls docs/merge-train/cycles | wc -l | tr -d ' ')" \
  "$U" \
  "$([ "$A" = "$B" ] && echo YES || echo NO)" \
  "$(make train | head -1 | grep -c 'L1 -> L4 -> L2 -> L3 -> L5')" \
  "$(grep -c 'cycle | date | L1 | L4 | L2 | L3 | L5' docs/merge-train.md)"
```

Expected output, exactly:

```
exec=4 cycles=0 unassigned=[TRAIN-OWNERS FAIL: 1 unassigned path(s)] stable=YES train=1 header=1
```

**STOP rule** — if `unassigned` prints `TRAIN-OWNERS OK`, the promotion gate cannot see an unassigned path and the
partition erodes silently at promotion time. Do not edit the expected output and do not proceed to any cycle.
Fix `train-owners.sh` or `lane-paths.tsv` (L0D-04) first. If `stable=NO`, `make train-log` is not idempotent and
the runbook will churn on every cycle; fix the awk markers before use. Record either as a TRAIN HALT (L0-03-02).

---

### L0-03-02 — Publish the TRAIN HALT record template

**Size:** S · **Dependencies:** L0-00-05 (`docs/escalation/`), L0-03-01

`docs/escalation/BLOCKER.md` and `docs/escalation/CCR.md` (L0-00-05) are the lane→L0 channels. A train halt is
the opposite direction — L0's own record of a cycle that could not run as specified — so it gets its own template
and never reuses the lane templates. It is a **record of fact**, not an escalation: there is nobody above L0 to
escalate to, and §94.9 (spec L8603) is explicit that automation writes state and humans write meaning.

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
cat > docs/escalation/TRAIN-HALT.md <<'HALT'
# TRAIN HALT — record template (L0 only)

A halt is recorded when the cycle cannot run as `docs/merge-train.md` specifies. Copy verbatim into
`docs/merge-train/cycles/cycle-<NNN>.halt.md`, commit on `integration`, and reference it from the
cycle record's `notes` field. A halt is never resolved by relaxing the rule that produced it.

```text
CYCLE:            <NNN>
DATE:             <YYYY-MM-DD>
HALTED AT:        <task id, e.g. L0-03-04, and the lane position L1|L4|L2|L3|L5>
BASE SHA:         <the frozen integration base for this cycle>

WHAT THE PROCEDURE REQUIRED
<verbatim quote of the step from L0-03-merge-train.md>

EXACT OUTPUT OBSERVED
<paste the literal command and its literal output — no paraphrase>

CLASSIFICATION       <one of>
  PARTITION-VIOLATION  a PR touches a foreign or unassigned path (PARTITION.md rule 1)
  CONTRACT-DRIFT       contracts.sha256 no longer matches contracts/** (PARTITION.md rule 2)
  TOOLCHAIN-BROKEN     lane-guard.sh / train-*.sh does not behave as its SELF-VERIFY states
  GATE-UNSATISFIABLE   a required status check exists that no workflow emits (Section 98.2, Phase 1)
  BAD-INTEGRATION      integration is red after a merge (L0D-08 applies)
  OTHER                <state it in one sentence; do not invent a classification>

DECISION TAKEN       <one of: SKIP-LANE | REVERT | ROLL-FORWARD | ABORT-CYCLE | DEFER-PROMOTION>
DECISION ID:         <L0D-07 | L0D-08 | L0D-09 | L0D-06 | L0D-04>
DECISION RECORD:     records/decisions/<file written via the record-decision CLI, Section 97.2>

WHAT WAS NOT DONE
No rule was relaxed, no lane branch was rebased or rewritten by L0, no required check was removed,
no contract was edited outside the 17:00 contract window under an approved CCR.

CYCLE DISPOSITION    <CONTINUED | ABORTED>
LANES STILL MERGED THIS CYCLE: <list, in train order>
```
HALT

git add docs/escalation/TRAIN-HALT.md
git commit -m "L0-03-02: TRAIN HALT record template"
git push origin integration
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Template exists | `test -f docs/escalation/TRAIN-HALT.md && echo PRESENT` | `PRESENT` |
| 2 | All six classifications present | `for c in PARTITION-VIOLATION CONTRACT-DRIFT TOOLCHAIN-BROKEN GATE-UNSATISFIABLE BAD-INTEGRATION OTHER; do grep -q "$c" docs/escalation/TRAIN-HALT.md \|\| echo "MISSING $c"; done; echo DONE` | `DONE` alone |
| 3 | All five dispositions present | `for d in SKIP-LANE REVERT ROLL-FORWARD ABORT-CYCLE DEFER-PROMOTION; do grep -q "$d" docs/escalation/TRAIN-HALT.md \|\| echo "MISSING $d"; done; echo DONE` | `DONE` alone |
| 4 | Every decision id is one the charter defines | `grep -o 'L0D-[0-9][0-9]' docs/escalation/TRAIN-HALT.md \| sort -u \| tr '\n' ' '` | `L0D-04 L0D-06 L0D-07 L0D-08 L0D-09 ` |
| 5 | The lane templates are untouched | `test -f docs/escalation/BLOCKER.md && test -f docs/escalation/CCR.md && echo BOTH` | `BOTH` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP_ROOT"
printf 'file=%s class=%s disp=%s ids=[%s] lanetmpl=%s\n' \
  "$(test -f docs/escalation/TRAIN-HALT.md && echo PRESENT || echo MISSING)" \
  "$(for c in PARTITION-VIOLATION CONTRACT-DRIFT TOOLCHAIN-BROKEN GATE-UNSATISFIABLE BAD-INTEGRATION OTHER; do grep -qc "$c" docs/escalation/TRAIN-HALT.md && echo x; done | wc -l | tr -d ' ')" \
  "$(for d in SKIP-LANE REVERT ROLL-FORWARD ABORT-CYCLE DEFER-PROMOTION; do grep -q "$d" docs/escalation/TRAIN-HALT.md && echo x; done | wc -l | tr -d ' ')" \
  "$(grep -o 'L0D-[0-9][0-9]' docs/escalation/TRAIN-HALT.md | sort -u | tr '\n' ' ' | sed 's/ $//')" \
  "$(test -f docs/escalation/BLOCKER.md -a -f docs/escalation/CCR.md && echo BOTH || echo MISSING)"
```

Expected output, exactly:

```
file=PRESENT class=6 disp=5 ids=[L0D-04 L0D-06 L0D-07 L0D-08 L0D-09] lanetmpl=BOTH
```

**STOP rule** — if `ids` contains any `L0D-nn` that `L0-00-charter.md` §5 does not define, you have invented a
decision id. Delete it and use the defined one. Inventing an id is the governance equivalent of F-18
(*"Inventing a spec section number, AT id, invariant number, SIG id or D id"*) and makes the decision register
un-auditable. If `lanetmpl=MISSING`, run L0-00-05 first; a halt template without the escalation templates means
lanes have nowhere to report from.

---

### L0-03-03 — Open the cycle: preflight, base freeze, candidate enumeration

**Size:** S · **Dependencies:** L0-03-01, L0-03-02

The cycle is opened once, on Wednesday, before any lane is touched. The base SHA is frozen here so that every
post-merge comparison in the cycle has a fixed reference.

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
git checkout integration
git pull --ff-only
make train-preflight

# Cycle number: one greater than the highest existing cycle file, zero-padded to three digits.
LAST=$(ls docs/merge-train/cycles/cycle-*.tsv 2>/dev/null | sed 's/.*cycle-\([0-9]*\)\.tsv/\1/' | LC_ALL=C sort | tail -1)
export CYCLE=$(printf '%03d' $(( 10#${LAST:-0} + 1 )))
export CYCLE_BASE=$(git rev-parse origin/integration)
echo "CYCLE=$CYCLE BASE=$CYCLE_BASE"

# Open the cycle record. Fields are appended as the cycle runs; the file is created here.
CF="docs/merge-train/cycles/cycle-$CYCLE.tsv"
{
  printf 'cycle\t%s\n' "$CYCLE"
  printf 'date\t%s\n' "$(date +%F)"
  printf 'base\t%s\n' "$CYCLE_BASE"
  printf 'promoted\tNO\n'
  printf 'notes\t-\n'
} > "$CF"

# Enumerate candidate PRs, one line per lane, in TRAIN ORDER.
for n in 1 4 2 3 5; do
  echo "--- lane $n ---"
  gh pr list --base integration --state open --label "lane-$n" \
    --json number,headRefName,isDraft,updatedAt \
    --template '{{range .}}{{.number}}	{{.headRefName}}	draft={{.isDraft}}	{{.updatedAt}}{{"\n"}}{{end}}'
done
```

**Selection rule when a lane has more than one open PR.** Take the **oldest** open non-draft PR whose head branch
matches `lane/<n>/*`. One lane PR merges per lane per cycle; the rest wait for the next cycle. This is not a
judgment call and is not negotiable by the lane — it keeps a cycle's blast radius to one branch per lane, which is
what makes the revert of L0-03-10 a single-commit operation.

**Commands**

```bash
set -euo pipefail
# The one command that applies the selection rule. Repeat per lane, substituting $n.
n=1
gh pr list --base integration --state open --label "lane-$n" \
  --json number,headRefName,isDraft,createdAt \
  --jq '[.[] | select(.isDraft==false) | select(.headRefName|startswith("lane/'"$n"'/"))]
        | sort_by(.createdAt) | .[0].number // "NONE"'
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Preflight green before anything else runs | `make train-preflight` | `CONTRACTS-FROZEN OK` then `PREFLIGHT OK` |
| 2 | The cycle number is exactly one greater than the last | `ls docs/merge-train/cycles/cycle-*.tsv \| wc -l` before and after | second value = first + 1 |
| 3 | The cycle file has all five opening fields | `awk -F'\t' '{print $1}' docs/merge-train/cycles/cycle-$CYCLE.tsv \| tr '\n' ' '` | `cycle date base promoted notes ` |
| 4 | The frozen base equals the remote tip at open | `[ "$CYCLE_BASE" = "$(git rev-parse origin/integration)" ] && echo SAME` | `SAME` |
| 5 | Candidate enumeration is in train order | the loop above | five `--- lane n ---` headers in the order `1 4 2 3 5` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP_ROOT"
printf 'cycle=%s fields=[%s] base_frozen=%s preflight=%s order=[%s]\n' \
  "$CYCLE" \
  "$(awk -F'\t' '{print $1}' docs/merge-train/cycles/cycle-$CYCLE.tsv | tr '\n' ' ' | sed 's/ $//')" \
  "$([ "$CYCLE_BASE" = "$(git rev-parse origin/integration)" ] && echo SAME || echo MOVED)" \
  "$(make train-preflight | tail -1)" \
  "$(for n in 1 4 2 3 5; do printf '%s ' "$n"; done | sed 's/ $//')"
```

Expected output (with `NNN` your cycle number):

```
cycle=NNN fields=[cycle date base promoted notes] base_frozen=SAME preflight=PREFLIGHT OK order=[1 4 2 3 5]
```

**STOP rule** — if `preflight` is anything other than `PREFLIGHT OK`, **do not open the cycle**. A dirty tree or a
`CONTRACTS-DRIFT` line means `contracts/**` has moved without a re-freeze, which is a PARTITION.md rule 2
violation regardless of who moved it. Record a TRAIN HALT with `CLASSIFICATION: CONTRACT-DRIFT`, re-freeze only
inside the 17:00 contract window under an approved CCR (`L0-00-charter.md` §8.1), and re-open the cycle after.
If `base_frozen=MOVED`, someone pushed to `integration` between your fetch and your freeze — re-run the whole
task; a cycle whose base moved cannot attribute a later failure to a lane.

---

### L0-03-04 — Admission check for one lane

**Size:** M · **Dependencies:** L0-03-03

Run once per lane, in the order `1 4 2 3 5`. This is the integration gate's *entry* half: what a lane PR must
prove before it is allowed to merge.

**The integration gate — the complete list.** A lane PR is admitted only if all eight hold:

| # | Condition | Checked by | Anchor |
|---|---|---|---|
| G1 | Base branch is `integration` | `train-admit.sh` (`base=integration`) | PARTITION.md §"Branch & merge model": only `integration` merges to `main` |
| G2 | Head branch matches `lane/<N>/*` | `train-admit.sh` (`branch=`) | PARTITION.md §"The five build lanes", branch prefix column |
| G3 | Not a draft | `train-admit.sh` (`draft=false`) | — |
| G4 | `integration` is an ancestor of the head — the branch is rebased | `git merge-base --is-ancestor` (`rebased=YES`) | PARTITION.md: *"rebased on `integration` before PR"* |
| G5 | Head tip is less than 24 hours old | `train-admit.sh` (`age_h`) | PARTITION.md: *"short-lived (< 1 day)"* |
| G6 | `lane-guard` clean — no foreign, no unassigned path | `lane-guard.sh` (`guard=OK`) | PARTITION.md rule 1 |
| G7 | Every **required** status check passes, or none is armed yet | `gh pr checks --required` (`checks=PASS\|NONE`) | §98.2 Phase 1 (spec L9017): the list starts empty and grows per phase |
| G8 | `mergeStateStatus` is `CLEAN` | `train-admit.sh` (`mergestate=CLEAN`) | GitHub's own merge-readiness state |

`checks=NONE` is an **admitting** state, not a failing one, and this is deliberate. §98.2 Phase 1 states the
required-status-check list *starts empty per repository* and that *"a list that silently stays empty is a gate
that reads armed and is not"* (spec L9017). Treating `NONE` as a pass at the machine gate while the human gate
(this procedure, plus the lane's own SELF-VERIFY at L0-03-06) still runs is the honest reading: L0 knows the list
is empty because it has not armed the contexts yet, and adding a context is F-07 for a lane and an L0 act here.

```bash
set -euo pipefail
cd "$CP_ROOT"
# Per lane, in train order. Substitute $n and the PR number chosen by T03's selection rule.
n=1
PR=$(gh pr list --base integration --state open --label "lane-$n" \
     --json number,headRefName,isDraft,createdAt \
     --jq '[.[] | select(.isDraft==false) | select(.headRefName|startswith("lane/'"$n"'/"))]
           | sort_by(.createdAt) | .[0].number // empty')

if [ -z "$PR" ]; then
  printf 'L%s\tNONE\n' "$n" >> "docs/merge-train/cycles/cycle-$CYCLE.tsv"
  echo "lane=$n verdict=NO-CANDIDATE"
else
  ./train-admit.sh "$n" "$PR" | tee "/tmp/admit-$CYCLE-L$n.txt"
fi
```

**Routing table — the verdict decides the next task, mechanically.**

| `verdict=` | Meaning | Go to | Cycle-record line |
|---|---|---|---|
| `ADMIT` | All eight gate conditions hold | **L0-03-06** | written by T06 |
| `REBASE` | G4 or G5 or `mergestate=BEHIND` failed; everything else may be fine | **L0-03-05** | `L<n>	SKIPPED	reason=REBASE	pr=<PR>` if not rebased in time |
| `GATE-FAIL` | G6, G7 or G8 failed | **L0-03-07** | `L<n>	SKIPPED	reason=GATE	pr=<PR>` |
| `HALT` | G1 or G2 failed — the PR is aimed at the wrong base or carries a foreign branch prefix | TRAIN HALT (L0-03-02), `CLASSIFICATION: PARTITION-VIOLATION` | `L<n>	HALTED	pr=<PR>` |
| `NO-CANDIDATE` | The lane has no open non-draft PR | next lane immediately | `L<n>	NONE` |

`NO-CANDIDATE` is **not** a skip and does not count toward the starvation counters of L0-03-12. A lane with
nothing ready is a lane working; a lane with something ready that cannot merge is the signal.

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | The check emits exactly one line | `./train-admit.sh "$n" "$PR" \| wc -l` | `1` |
| 2 | The line ends in a verdict from the closed set | `./train-admit.sh "$n" "$PR" \| grep -cE 'verdict=(ADMIT|REBASE|GATE-FAIL|HALT)$'` | `1` |
| 3 | A cross-lane PR never admits | `./train-admit.sh 1 <a lane/3 PR number> \| grep -o 'verdict=.*'` | `verdict=HALT` |
| 4 | An un-rebased PR never admits | `./train-admit.sh "$n" <a PR behind integration> \| grep -o 'verdict=.*'` | `verdict=REBASE` |
| 5 | Every lane got a line or a `NONE` record this cycle | `grep -c '^L[12345]	' docs/merge-train/cycles/cycle-$CYCLE.tsv` plus the admit files | five lanes accounted for |

**SELF-VERIFY** (run after the five lanes have been checked, before any merge)

```bash
set -euo pipefail
cd "$CP_ROOT"
acct=0
for n in 1 4 2 3 5; do
  if [ -f "/tmp/admit-$CYCLE-L$n.txt" ] || grep -q "^L$n	NONE" "docs/merge-train/cycles/cycle-$CYCLE.tsv"; then
    acct=$((acct+1))
  fi
done
bad=$(cat /tmp/admit-$CYCLE-L*.txt 2>/dev/null | grep -vcE 'verdict=(ADMIT|REBASE|GATE-FAIL|HALT)$' || true)
printf 'lanes_accounted=%s malformed_verdicts=%s order=[%s]\n' \
  "$acct" "${bad:-0}" \
  "$(cat /tmp/admit-$CYCLE-L*.txt 2>/dev/null | sed -n 's/^lane=\([0-9]\).*/\1/p' | tr '\n' ' ' | sed 's/ $//')"
```

Expected output — `lanes_accounted=5`, `malformed_verdicts=0`, and `order` a subsequence of `1 4 2 3 5`:

```
lanes_accounted=5 malformed_verdicts=0 order=[1 4 2 3 5]
```

**STOP rule** — if `lanes_accounted` is below 5, a lane was silently skipped, which is the one failure mode this
whole procedure exists to prevent: an unrecorded skip produces no starvation counter, so the blocked lane is never
diagnosed (L0-03-12). Do not merge anything. Re-run the admission loop for the missing lane. If a verdict is
`HALT`, do **not** re-point the PR's base yourself and do not rename the lane's branch — both are lane-owned
objects and PARTITION.md forbids L0 rewriting them exactly as it forbids a lane rewriting another lane's. Record
the halt, comment the fact on the PR, and move to the next lane.

---

### L0-03-05 — A lane behind on rebase — the rebase directive

**Size:** M · **Dependencies:** L0-03-04

`verdict=REBASE` means the branch is not a descendant of `integration`, or its tip is older than 24 hours, or
GitHub reports `BEHIND`. PARTITION.md is unambiguous about who fixes it: *"`lane/N/<phase>-<task>` — one branch
per task, short-lived (< 1 day), **rebased on `integration` before PR**"* and *"A lane NEVER rebases another
lane's branch."* The lane rebases. **L0 does not rebase, does not push to a lane branch, does not use
`gh pr update-branch`, and does not use the merge queue's auto-update.** Rewriting a branch the lane executor is
still working on hands them a diverged local and a force-push race — and the AI executor profile in PARTITION.md
("no repo context, no judgment authority") means they will not recover from it unaided.

L0's only action is a directive comment with the exact commands, and a deadline inside this cycle.

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
n=1; PR=<pr-number>
BR=$(gh pr view "$PR" --json headRefName -q .headRefName)

cat > /tmp/rebase-directive.md <<DIR
**MERGE TRAIN — REBASE DIRECTIVE (cycle $CYCLE, lane $n)**

This PR is behind \`integration\` and cannot be admitted to cycle $CYCLE as it stands.
PARTITION.md: *"one branch per task, short-lived (< 1 day), rebased on \`integration\` before PR."*

Run **exactly** these commands on your own branch. Do not merge \`integration\` into your branch;
rebase, so the branch stays a linear descendant and the lane-guard diff stays scoped to your lane.

\`\`\`bash
cd "\$CP_ROOT"
git fetch --prune origin
git checkout $BR
git rebase origin/integration
# If, and only if, git reports a conflict:
#   STOP. Do not resolve it. A conflict between your branch and integration means two lanes
#   wrote the same path, which PARTITION.md rule 1 makes impossible unless the map is wrong.
#   Run:  git rebase --abort
#   Then open a BLOCKER issue from docs/escalation/BLOCKER.md with
#   FORBIDDEN/UNDECIDED ID: F-03, and paste the conflicting path list from:
#   git diff --name-only --diff-filter=U
./lane-guard.sh $n origin/integration HEAD
# Expect exactly: LANE-GUARD OK
git push --force-with-lease origin $BR
\`\`\`

Then reply on this PR with the output of \`./lane-guard.sh $n origin/integration HEAD\`.

**Deadline:** before this cycle reaches lane position 5. After that the PR is recorded \`SKIPPED\`
for cycle $CYCLE and is a first-class candidate in cycle $((10#$CYCLE + 1)). A skip is a record of a
train state, never a judgement about the lane (see the starvation rule, L0-03-12).
DIR

gh pr comment "$PR" --body-file /tmp/rebase-directive.md
gh pr edit "$PR" --add-label "needs-rebase"
```

Re-check once, when the lane replies, before the cycle reaches position 5:

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
./train-admit.sh "$n" "$PR"
# verdict=ADMIT  -> continue to L0-03-06 at this lane's position if the cycle has not passed it,
#                   otherwise the lane rides the next cycle at its normal position.
# verdict=REBASE -> record the skip:
printf 'L%s\tSKIPPED\treason=REBASE\tpr=%s\n' "$n" "$PR" >> "docs/merge-train/cycles/cycle-$CYCLE.tsv"
```

**A rebased branch is re-checked in full.** After a force-push the branch is a different branch: `lane-guard`,
the required checks and `mergeStateStatus` are all re-evaluated by re-running `train-admit.sh`. Never carry a
green result across a force-push.

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | The directive was posted to the PR | `gh pr view "$PR" --json comments -q '[.comments[].body] \| map(select(startswith("**MERGE TRAIN — REBASE DIRECTIVE"))) \| length'` | `1` or more |
| 2 | The label is set | `gh pr view "$PR" --json labels -q '[.labels[].name] \| index("needs-rebase") != null'` | `true` |
| 3 | L0 pushed nothing to the lane branch | `git log --format='%an' "origin/$BR" -1` | the lane executor's name, not L0's |
| 4 | After the lane rebases, `integration` is an ancestor | `git fetch -q origin && git merge-base --is-ancestor origin/integration "origin/$BR" && echo REBASED` | `REBASED` |
| 5 | The re-check produces a fresh verdict | `./train-admit.sh "$n" "$PR" \| grep -o 'verdict=.*'` | `verdict=ADMIT` or `verdict=REBASE` |
| 6 | A skip, if taken, is recorded | `grep -c "^L$n	SKIPPED	reason=REBASE" docs/merge-train/cycles/cycle-$CYCLE.tsv` | `1` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP_ROOT"
git fetch -q --prune origin
printf 'directive=%s label=%s l0_pushed=%s rebased=%s verdict=%s\n' \
  "$(gh pr view "$PR" --json comments -q '[.comments[].body]|map(select(startswith("**MERGE TRAIN — REBASE DIRECTIVE")))|length')" \
  "$(gh pr view "$PR" --json labels -q '[.labels[].name]|index("needs-rebase")!=null')" \
  "$(git log --format='%ae' "origin/$BR" -1 | grep -c "$(git config user.email)")" \
  "$(git merge-base --is-ancestor origin/integration "origin/$BR" 2>/dev/null && echo YES || echo NO)" \
  "$(./train-admit.sh "$n" "$PR" | sed -n 's/.*verdict=\(.*\)/\1/p')"
```

Expected output after a successful lane rebase:

```
directive=1 label=true l0_pushed=0 rebased=YES verdict=ADMIT
```

**STOP rule** — if `l0_pushed` is anything other than `0`, L0 has written to a lane branch. Stop and record a
TRAIN HALT with `CLASSIFICATION: OTHER` stating it plainly, because from that moment the lane's SELF-VERIFY
evidence no longer describes code the lane wrote, and invariant 40 (spec L9508: *"Humans write decisions and
meaning; machines write measurable state"*) has its authorship line crossed in the other direction. If the lane
reports a rebase **conflict**, do not resolve it and do not tell the lane to resolve it: a conflict is proof two
lanes own the same path, which is a `lane-paths.tsv` defect under L0D-04. Fix the map, then re-issue the
directive.

---

### L0-03-06 — Merge the admitted lane PR and re-verify `integration`

**Size:** M · **Dependencies:** L0-03-04 (verdict `ADMIT`)

Five steps per lane, from `L0-00-charter.md` §9, made literal. Steps 1–2 were L0-03-04. Steps 3–5 are here.

**Step 3 — the lane's own SELF-VERIFY, run by L0 against the branch head.** Every lane plan file ends its phase
with a SELF-VERIFY block and a stated expected output; L0 runs that block, not a paraphrase of it.

```bash
set -euo pipefail
cd "$CP_ROOT"
n=1; PR=<pr-number>
BR=$(gh pr view "$PR" --json headRefName -q .headRefName)
git fetch --prune origin
git checkout -B "verify/$CYCLE/L$n" "origin/$BR"

# Run the SELF-VERIFY block verbatim from the lane's plan file for the phase this PR closes.
# Lane plan files, by lane:
#   L1 -> Code/implementation/lanes/L1-0*.md      L2 -> .../L2-00-charter.md
#   L3 -> .../L3-0*.md                            L4 -> .../L4-0*.md
#   L5 -> .../L5-00-charter.md
# Record the result — the promotion gate (L0-03-09) requires this file.
VLOG="docs/merge-train/cycles/cycle-$CYCLE.verify"
PLAN_FILE=$(ls "$CP_ROOT"/Code/implementation/lanes/L${n}-0*.md 2>/dev/null | head -1)
SV_SCRIPT=$(mktemp)
# Extract the first SELF-VERIFY bash block from the lane plan file.
awk '/^#+[ \t]*SELF-VERIFY/{f=1} f && /^```bash/{f=2;next} f==2 && /^```/{exit} f==2{print}' \
  "${PLAN_FILE:-/dev/null}" > "$SV_SCRIPT"
if [ -s "$SV_SCRIPT" ] && sh "$SV_SCRIPT" 2>&1; then
  echo "L$n SELF-VERIFY OK" >> "$VLOG"
else
  echo "L$n SELF-VERIFY FAIL" >> "$VLOG"
  # --- Paired negative test ---
  # When "L$n SELF-VERIFY FAIL" is written here, the promotion gate in
  # train-promote-gate.sh (check P5) counts:
  #   VOK    = lines ending in "SELF-VERIFY OK"  in cycle-$CYCLE.verify
  #   MERGED = lines containing "MERGED"          in cycle-$CYCLE.tsv
  # and requires VOK >= MERGED to pass.  A FAIL entry makes VOK < MERGED,
  # causing: "GATE-FAIL P5 self-verify <n> < merged <m>"
  # which exits train-promote-gate.sh non-zero → PROMOTE-GATE FAIL.
  # The promotion to main is blocked until the lane fixes its SELF-VERIFY
  # and L0 re-runs step 3 on the corrected branch with a passing result.
  # Do NOT manually insert an OK line to bypass this gate (L0D-07).
fi
rm -f "$SV_SCRIPT"

git checkout integration
git branch -D "verify/$CYCLE/L$n"
```

**Step 4 — merge, always with a merge commit.** `gh pr merge --merge` always creates a merge commit; it is the
`--no-ff` of PARTITION.md expressed in `gh`. Never `--squash` and never `--rebase`: the revert of L0-03-10 needs
a merge commit with a first parent to name.

```bash
set -euo pipefail
cd "$CP_ROOT"
gh pr merge "$PR" --merge --delete-branch \
  --subject "merge-train cycle $CYCLE: lane $n (#$PR)" \
  --body "Cycle $CYCLE, position $(case $n in 1) echo 1;; 4) echo 2;; 2) echo 3;; 3) echo 4;; 5) echo 5;; esac) of 5. Order L1 -> L4 -> L2 -> L3 -> L5 (PARTITION.md, FROZEN)."

git checkout integration && git pull --ff-only
MERGE_SHA=$(git rev-parse HEAD)
printf 'L%s\tMERGED\tpr=%s\tmerge=%s\n' "$n" "$PR" "$MERGE_SHA" >> "docs/merge-train/cycles/cycle-$CYCLE.tsv"
echo "merged lane=$n pr=$PR sha=$MERGE_SHA"
```

**Step 5 — re-verify the merged result before the next lane starts.** This is the step that keeps attribution
possible: a red `integration` discovered two lanes later cannot be pinned to a merge.

```bash
set -euo pipefail
cd "$CP_ROOT"
./train-owners.sh "$CYCLE_BASE" HEAD          # every path in the cycle so far is owned
make promote-check                            # contracts still frozen
git log --oneline -1 --merges                 # the merge commit is the tip
gh run list --branch integration --limit 5 \
  --json workflowName,conclusion,headSha \
  --template '{{range .}}{{.workflowName}}	{{.conclusion}}	{{.headSha}}{{"\n"}}{{end}}'
```

If the post-merge run is red, `integration` is broken by a merge whose SHA you hold: go to **L0-03-10**.

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | The merge produced a merge commit, not a squash | `git rev-list --parents -n1 "$MERGE_SHA" \| wc -w` | `3` |
| 2 | The PR is merged and the branch deleted | `gh pr view "$PR" --json state,headRefName -q '.state'` | `MERGED` |
| 3 | Contracts still frozen after the merge | `make promote-check` | `CONTRACTS-FROZEN OK` |
| 4 | Every path merged this cycle is owned | `./train-owners.sh "$CYCLE_BASE" HEAD` | `TRAIN-OWNERS OK` |
| 5 | The lane's SELF-VERIFY result is recorded | `grep -c "^L$n SELF-VERIFY OK" docs/merge-train/cycles/cycle-$CYCLE.verify` | `1` |
| 6 | The cycle record names the merge | `grep -c "^L$n	MERGED	pr=$PR" docs/merge-train/cycles/cycle-$CYCLE.tsv` | `1` |
| 7 | `integration` CI is green on the merge SHA | `gh run list --branch integration --limit 1 --json conclusion -q '.[0].conclusion'` | `success` |
| 8 | No merge conflict artifact survives | `git ls-files -u \| wc -l` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP_ROOT"
printf 'parents=%s state=%s frozen=%s owners=%s selfverify=%s record=%s ci=%s conflicts=%s\n' \
  "$(git rev-list --parents -n1 "$MERGE_SHA" | wc -w | tr -d ' ')" \
  "$(gh pr view "$PR" --json state -q .state)" \
  "$(make promote-check | tail -1)" \
  "$(./train-owners.sh "$CYCLE_BASE" HEAD | tail -1)" \
  "$(grep -c "^L$n SELF-VERIFY OK" docs/merge-train/cycles/cycle-$CYCLE.verify)" \
  "$(grep -c "^L$n	MERGED	pr=$PR" docs/merge-train/cycles/cycle-$CYCLE.tsv)" \
  "$(gh run list --branch integration --limit 1 --json conclusion -q '.[0].conclusion')" \
  "$(git ls-files -u | wc -l | tr -d ' ')"
```

Expected output, exactly:

```
parents=3 state=MERGED frozen=CONTRACTS-FROZEN OK owners=TRAIN-OWNERS OK selfverify=1 record=1 ci=success conflicts=0
```

**STOP rule** — if `parents` is `2`, the PR was squashed or rebased and there is no merge commit to revert with
`-m 1`; record a TRAIN HALT with `CLASSIFICATION: OTHER`, and do **not** continue the cycle until the merge method
is corrected in the repository settings, because every subsequent lane in this cycle would inherit an
unrevertable history. If `conflicts` is non-zero, two lanes wrote the same path: **do not resolve the conflict** —
resolving it normalises exactly the shared-mutable-file pattern PARTITION.md rule 3 forbids. Record the halt with
`CLASSIFICATION: PARTITION-VIOLATION` and fix `lane-paths.tsv` under L0D-04 first. If `ci` is `failure`, go
straight to L0-03-10 and do not start the next lane; a second merge on a red base destroys attribution.

---

### L0-03-07 — A lane PR that fails the integration gate

**Size:** M · **Dependencies:** L0-03-04 (verdict `GATE-FAIL`)

`GATE-FAIL` means G6 (`lane-guard`), G7 (required checks) or G8 (`mergeStateStatus`) failed. The disposition is
fixed by which one, and none of the three is negotiable.

| Failure | What it means | L0's action | Never |
|---|---|---|---|
| `guard=FAIL` | The PR touches a foreign or unassigned path | Comment the guard output verbatim; label `partition-violation`; record `SKIPPED reason=GATE`; if any violation line says `UNASSIGNED`, also record a TRAIN HALT with `CLASSIFICATION: PARTITION-VIOLATION` because the map itself is deficient (L0D-04) | Merge "just this once". PARTITION.md rule 1: *"A lane PR touching a foreign path FAILS the lane-guard check. No exceptions."* |
| `checks=FAIL` | A **required** status check is red | Comment the failing contexts and the run URL; record `SKIPPED reason=GATE`; the lane fixes its own code on its own branch | Remove or bypass the required check. F-07 forbids a lane adding one; L0 removing one to land a PR is the same gate erosion from the other side (§98.2 Phase 1) |
| `checks=FAIL` **and** the context is emitted by no workflow | A required check exists that nothing satisfies — the exact failure §98.2 Phase 1 names | TRAIN HALT, `CLASSIFICATION: GATE-UNSATISFIABLE`. L0 removes the context from branch protection **as an L0 act with a decision record**, because a check no workflow emits blocks every PR in the repository indefinitely (spec L9017) | Ask a lane to fix it — arming and disarming contexts is L0's, and F-07 puts it out of lane reach |
| `mergestate=DIRTY` | Merge conflict with `integration` | Same as a rebase conflict: two lanes wrote one path. TRAIN HALT, `CLASSIFICATION: PARTITION-VIOLATION`, fix `lane-paths.tsv` (L0D-04) | Resolve the conflict in a merge commit (PARTITION.md rule 3) |
| `mergestate=BLOCKED` | Branch protection is unsatisfied — usually a missing Code Owner approval | Route to the review step of `L0-00-charter.md` §8.1 (14:00 lane PR review); record `SKIPPED reason=GATE` if it stays unsatisfied at position 5 | Self-approve. §11.3 (spec L865) requires *approval of the most recent reviewable push*, which mechanically prevents an author's own approval satisfying the requirement |
| `mergestate=UNSTABLE` | A non-required check is red | Admit only if G1–G7 hold and the red check is genuinely not in the required list — verify with `gh pr checks --required` — otherwise record `SKIPPED reason=GATE` | Reclassify a required check as non-required to get past it |

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
n=1; PR=<pr-number>

# 1. Capture the evidence, literally.
./train-admit.sh "$n" "$PR" | tee "/tmp/gatefail-$CYCLE-L$n.txt"
./lane-guard.sh "$n" origin/integration "origin/$(gh pr view "$PR" --json headRefName -q .headRefName)" \
  > "/tmp/guard-$CYCLE-L$n.txt" 2>&1 || true
gh pr checks "$PR" --required > "/tmp/checks-$CYCLE-L$n.txt" 2>&1 || true

# 2. Post it to the PR, unedited. The lane executor has no repo context; a paraphrase is useless to it.
{
  echo "**MERGE TRAIN — GATE FAILURE (cycle $CYCLE, lane $n)**"
  echo
  echo "This PR was not admitted to cycle $CYCLE. Verbatim gate output:"
  echo
  echo '```'
  cat "/tmp/gatefail-$CYCLE-L$n.txt"
  echo
  cat "/tmp/guard-$CYCLE-L$n.txt"
  echo
  cat "/tmp/checks-$CYCLE-L$n.txt"
  echo '```'
  echo
  echo "Fix on your own branch. Do not change the gate. Do not touch any path outside your lane."
  echo "When green, reply with the output of \`./lane-guard.sh $n origin/integration HEAD\`."
  echo "This PR rides cycle $((10#$CYCLE + 1)) at lane position $n unless it is admitted before this"
  echo "cycle reaches position 5."
} > /tmp/gatefail-comment.md
gh pr comment "$PR" --body-file /tmp/gatefail-comment.md

# 3. Record the skip and move to the next lane IMMEDIATELY. The train does not wait.
printf 'L%s\tSKIPPED\treason=GATE\tpr=%s\n' "$n" "$PR" >> "docs/merge-train/cycles/cycle-$CYCLE.tsv"

# 4. Label by failure kind, so the starvation accounting of T12 can classify without re-reading logs.
case "$(sed -n 's/.*guard=\([A-Z]*\).*/\1/p' "/tmp/gatefail-$CYCLE-L$n.txt")" in
  FAIL) gh pr edit "$PR" --add-label "partition-violation" ;;
  *)    gh pr edit "$PR" --add-label "gate-red" ;;
esac
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | The PR was not merged | `gh pr view "$PR" --json state -q .state` | `OPEN` |
| 2 | The verbatim gate output is on the PR | `gh pr view "$PR" --json comments -q '[.comments[].body]\|map(select(startswith("**MERGE TRAIN — GATE FAILURE")))\|length'` | `1` or more |
| 3 | The skip is recorded with a reason | `grep -c "^L$n	SKIPPED	reason=GATE	pr=$PR" docs/merge-train/cycles/cycle-$CYCLE.tsv` | `1` |
| 4 | A failure kind label is set | `gh pr view "$PR" --json labels -q '[.labels[].name]\|map(select(.=="partition-violation" or .=="gate-red"))\|length'` | `1` |
| 5 | No required check was removed to accommodate the PR | `gh api repos/{owner}/{repo}/branches/integration/protection/required_status_checks/contexts -q 'length'` before and after | identical numbers |
| 6 | The next lane started without delay | the cycle record shows a line for the next lane in train order | present |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP_ROOT"
printf 'state=%s comment=%s skip=%s label=%s contexts=%s\n' \
  "$(gh pr view "$PR" --json state -q .state)" \
  "$(gh pr view "$PR" --json comments -q '[.comments[].body]|map(select(startswith("**MERGE TRAIN — GATE FAILURE")))|length')" \
  "$(grep -c "^L$n	SKIPPED	reason=GATE	pr=$PR" docs/merge-train/cycles/cycle-$CYCLE.tsv)" \
  "$(gh pr view "$PR" --json labels -q '[.labels[].name]|map(select(.=="partition-violation" or .=="gate-red"))|length')" \
  "$(gh api repos/{owner}/{repo}/branches/integration/protection/required_status_checks/contexts -q 'length' 2>/dev/null || echo 0)"
```

Expected output (`contexts` is whatever the phase has armed so far and must be **unchanged** from before the
failure — record its value at cycle open and compare):

```
state=OPEN comment=1 skip=1 label=1 contexts=<same value as at cycle open>
```

**STOP rule** — if `state=MERGED`, a failing PR was merged. Go to L0-03-10 and revert it, then record a TRAIN
HALT with `CLASSIFICATION: OTHER`. If `contexts` decreased, a required status check was removed to land a PR:
stop the cycle entirely, restore the context, and record the halt with `CLASSIFICATION: GATE-UNSATISFIABLE` only
if the context genuinely had no emitting workflow — otherwise it is gate erosion and the correct record is a
decision record explaining why, under L0D-09. §98.2 Phase 1 (spec L9017) states the required-check list grows per
phase; nothing in the spec removes a context to unblock a pull request.

---

### L0-03-08 — Close the cycle and regenerate the log

**Size:** S · **Dependencies:** L0-03-06

The cycle closes when all five positions have a line in the cycle record — `MERGED`, `SKIPPED`, `HALTED` or
`NONE`. Every one of the five, every cycle, without exception; a missing line is the unrecorded skip that breaks
L0-03-12.

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
CF="docs/merge-train/cycles/cycle-$CYCLE.tsv"

# 1. Assert five lane lines exist, in train order.
for n in 1 4 2 3 5; do grep -q "^L$n	" "$CF" || echo "MISSING LANE LINE: L$n"; done

# 2. Notes: one line, no newlines, referencing any halt file recorded this cycle.
HALTS=$(ls docs/merge-train/cycles/cycle-$CYCLE.halt.md 2>/dev/null | wc -l | tr -d ' ')
sed -i "s|^notes\t.*|notes\thalts=$HALTS|" "$CF"

# 3. Regenerate the table in the runbook. Never hand-edit it (invariant 46).
make train-log

# 4. Commit the cycle on integration. This is an L0-owned docs/** change; lane-guard sees lane 0.
git add "$CF" docs/merge-train.md docs/merge-train/cycles/
git commit -m "L0-03-08: close merge-train cycle $CYCLE"
git push origin integration
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | All five lanes accounted for | `for n in 1 4 2 3 5; do grep -qc "^L$n	" docs/merge-train/cycles/cycle-$CYCLE.tsv \|\| echo MISS; done; echo DONE` | `DONE` alone |
| 2 | Every lane line carries a legal disposition | `awk -F'\t' '/^L[12345]\t/ && $2!~/^(MERGED\|SKIPPED\|HALTED\|NONE)$/' docs/merge-train/cycles/cycle-$CYCLE.tsv \| wc -l` | `0` |
| 3 | Every `MERGED` line names a merge SHA that exists | `awk -F'\t' '/MERGED/{for(i=1;i<=NF;i++) if($i~/^merge=/){sub("merge=","",$i); print $i}}' docs/merge-train/cycles/cycle-$CYCLE.tsv \| while read s; do git cat-file -e "$s^{commit}" \|\| echo BAD; done; echo OK` | `OK` alone |
| 4 | The generated table contains this cycle's row | `grep -c "^| $CYCLE |" docs/merge-train.md` | `1` |
| 5 | The table row count equals the cycle-file count | see SELF-VERIFY | equal |
| 6 | The runbook is committed and pushed | `git status --porcelain docs/ \| wc -l` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP_ROOT"
printf 'lanes=%s illegal=%s row=%s rows=%s files=%s clean=%s\n' \
  "$(for n in 1 4 2 3 5; do grep -q "^L$n	" docs/merge-train/cycles/cycle-$CYCLE.tsv && echo x; done | wc -l | tr -d ' ')" \
  "$(awk -F'\t' '/^L[12345]\t/ && $2!~/^(MERGED|SKIPPED|HALTED|NONE)$/' docs/merge-train/cycles/cycle-$CYCLE.tsv | wc -l | tr -d ' ')" \
  "$(grep -c "^| $CYCLE |" docs/merge-train.md)" \
  "$(awk '/CYCLE-LOG:BEGIN/{f=1;next} /CYCLE-LOG:END/{f=0} f && /^\| [0-9]/' docs/merge-train.md | wc -l | tr -d ' ')" \
  "$(ls docs/merge-train/cycles/cycle-*.tsv | wc -l | tr -d ' ')" \
  "$(git status --porcelain docs/ | wc -l | tr -d ' ')"
```

Expected output, with `rows` and `files` equal:

```
lanes=5 illegal=0 row=1 rows=<N> files=<N> clean=0
```

**STOP rule** — if `lanes` is below `5`, do not close the cycle and do not promote: the missing lane has no
record, so its starvation counter cannot increment and a genuinely blocked lane becomes invisible, which is the
one thing §10 exists to prevent. Re-run L0-03-04 for the missing lane and record its disposition, even
retroactively, marking the line `SKIPPED reason=UNRECORDED` and recording a TRAIN HALT with
`CLASSIFICATION: OTHER`. If `rows` and `files` differ, `make train-log` did not consume every cycle file — check
the `LC_ALL=C sort` glob before trusting any starvation count.

---

### L0-03-09 — Promote `integration → main` under the full gate

**Size:** L · **Dependencies:** L0-03-08

Promotion is L0D-09 and nothing else authorises it. `main` is *"protected, releasable. Only `integration` merges
here"* (PARTITION.md §"Branch & merge model"), so promotion is a pull request, never a push, and never a
fast-forward performed locally.

Write the gate script first — it is the one gate whose failure must be impossible to overlook.

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
cat > train-promote-gate.sh <<'GATE'
#!/usr/bin/env sh
# train-promote-gate.sh — L0-owned. The full gate for integration -> main (L0D-09).
# Usage: ./train-promote-gate.sh <CYCLE>
set -eu
CYCLE="${1:?cycle required}"
CF="docs/merge-train/cycles/cycle-$CYCLE.tsv"
VF="docs/merge-train/cycles/cycle-$CYCLE.verify"
FAIL=0
note() { echo "  $1"; }
bad()  { echo "GATE-FAIL $1"; FAIL=$((FAIL+1)); }

git fetch --prune origin >/dev/null 2>&1

# P1 — contracts frozen (PARTITION.md rule 2)
if make --no-print-directory promote-check | grep -q '^CONTRACTS-FROZEN OK$'; then
  note "P1 contracts frozen OK"; else bad "P1 contracts not frozen"; fi

# P2 — every path in the promotion range resolves to an assigned lane (PARTITION.md rule 1, L0D-04)
if ./train-owners.sh origin/main origin/integration | grep -q '^TRAIN-OWNERS OK$'; then
  note "P2 all paths owned OK"; else bad "P2 unassigned path in range"; fi

# P3 — no machine identity touched .github/workflows in the range
#      (Section 33.2, spec L2866; Section 53.2 Level 4, spec L4697)
BOTWF=0
for sha in $(git log --format='%H' origin/main..origin/integration); do
  an=$(git log -1 --format='%an <%ae>' "$sha")
  case "$an" in
    *"[bot]"*|*"bot@"*)
      if git show --name-only --format= "$sha" | grep -q '^\.github/workflows/'; then
        echo "  BOT WORKFLOW COMMIT: $sha $an"; BOTWF=$((BOTWF+1))
      fi ;;
  esac
done
if [ "$BOTWF" -eq 0 ]; then note "P3 no machine workflow commit OK"; else bad "P3 $BOTWF machine workflow commit(s)"; fi

# P4 — no API key anywhere in the environment (Section 98.2 Phase 1; invariants 83, 84)
if [ -z "$(env | grep -i api_key || true)" ]; then note "P4 no API key OK"; else bad "P4 API key present in env"; fi

# P5 — all five lane SELF-VERIFY results recorded for merged lanes this cycle
MERGED=$(grep -c '	MERGED	' "$CF" || true)
VOK=0; [ -f "$VF" ] && VOK=$(grep -c 'SELF-VERIFY OK$' "$VF" || true)
if [ "$VOK" -ge "$MERGED" ]; then note "P5 self-verify $VOK >= merged $MERGED OK"; else bad "P5 self-verify $VOK < merged $MERGED"; fi

# P6 — the cycle is closed: five lane lines present
LANES=0
for n in 1 4 2 3 5; do if grep -q "^L$n	" "$CF"; then LANES=$((LANES+1)); fi; done
if [ "$LANES" -eq 5 ]; then note "P6 cycle closed OK"; else bad "P6 cycle open: $LANES/5 lanes recorded"; fi

# P7 — the cycle has not already been promoted
if grep -q '^promoted	NO$' "$CF"; then note "P7 not yet promoted OK"; else bad "P7 cycle already promoted or field malformed"; fi

# P8 — the Friday 15:00 freeze window (Section 94.8, spec L8586)
if ./train-freeze-window.sh >/dev/null; then note "P8 freeze window open OK"; else bad "P8 freeze window CLOSED"; fi

# P9 — integration CI green on the exact head being promoted
HEAD_SHA=$(git rev-parse origin/integration)
CONC=$(gh run list --branch integration --limit 20 \
        --json headSha,conclusion --jq "[.[]|select(.headSha==\"$HEAD_SHA\")|.conclusion]|unique|join(\",\")")
case "$CONC" in
  "success") note "P9 integration CI green OK" ;;
  "")        bad "P9 no CI run for $HEAD_SHA" ;;
  *)         bad "P9 integration CI conclusions: $CONC" ;;
esac

if [ "$FAIL" -eq 0 ]; then echo "PROMOTE-GATE OK ($CYCLE $HEAD_SHA)"; exit 0; fi
echo "PROMOTE-GATE FAIL: $FAIL condition(s)"
exit 1
GATE
chmod +x train-promote-gate.sh
git add train-promote-gate.sh
git commit -m "L0-03-09: promotion gate"
git push origin integration
```

Run the gate, then open the promotion PR.

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
make promote-gate CYCLE="$CYCLE"      # must print PROMOTE-GATE OK

gh pr create --base main --head integration \
  --title "PROMOTE cycle $CYCLE: integration -> main" \
  --label "promotion" \
  --body "$(printf 'Promotion of merge-train cycle %s.\n\nGate: `make promote-gate CYCLE=%s` -> PROMOTE-GATE OK\nCycle record: docs/merge-train/cycles/cycle-%s.tsv\nOrder this cycle: L1 -> L4 -> L2 -> L3 -> L5 (PARTITION.md, FROZEN)\nDecision: L0D-09.\n' "$CYCLE" "$CYCLE" "$CYCLE")"

PROMO=$(gh pr list --base main --head integration --state open --json number -q '.[0].number')

# P10 — the human gate. Branch protection requires a Code Owner approval from a HUMAN identity
# (Section 11.3, spec L864-865; Section 98.2 Phase 1 completion check, executed negatively).
gh pr view "$PROMO" --json reviews \
  --jq '[.reviews[]|select(.state=="APPROVED")|.author.login]|unique|join(",")'
# Every login printed MUST appear in CODEOWNERS and MUST NOT end in "[bot]".
grep -o '@[A-Za-z0-9-]*' CODEOWNERS | sort -u

gh pr merge "$PROMO" --merge \
  --subject "PROMOTE cycle $CYCLE: integration -> main" \
  --body "Gate: PROMOTE-GATE OK. Cycle record: docs/merge-train/cycles/cycle-$CYCLE.tsv. L0D-09."

# Record the promotion and regenerate the log.
git checkout integration && git pull --ff-only
sed -i "s|^promoted\tNO$|promoted\tYES|" "docs/merge-train/cycles/cycle-$CYCLE.tsv"
make train-log
git add docs/merge-train.md "docs/merge-train/cycles/cycle-$CYCLE.tsv"
git commit -m "L0-03-09: cycle $CYCLE promoted to main"
git push origin integration
```

**The ten promotion conditions, and where each comes from**

| # | Condition | Source |
|---|---|---|
| P1 | `contracts.sha256` matches `contracts/**` | PARTITION.md rule 2; `make promote-check` (L0-00-04) |
| P2 | Every path in `main..integration` resolves to an assigned lane | PARTITION.md rule 1; L0D-04 |
| P3 | No machine identity committed under `.github/workflows/**` in the range | §33.2 (spec L2866); §53.2 Level 4 (spec L4697) |
| P4 | `env \| grep -i api_key` empty | §98.2 Phase 1 (spec L9012); invariants 83, 84 (spec L9563–L9564) |
| P5 | A recorded SELF-VERIFY result for every lane merged this cycle | `L0-00-charter.md` §9 step 3 |
| P6 | All five lane positions recorded — the cycle is closed | L0-03-08 |
| P7 | The cycle has not already been promoted | idempotence |
| P8 | Before Friday 15:00 | §94.8 (spec L8586): *"Friday 15:00 · All · Deployment freeze begins"* |
| P9 | `integration` CI green on the exact head SHA | — |
| P10 | A Code Owner approving review from a **human** identity | §11.3 (spec L864–865); §98.2 Phase 1 completion check |

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | The gate passed before the PR existed | `make promote-gate CYCLE="$CYCLE"` | `PROMOTE-GATE OK (<cycle> <sha>)` |
| 2 | The promotion is a PR, not a push | `gh pr view "$PROMO" --json baseRefName,headRefName -q '.baseRefName+"<-"+.headRefName'` | `main<-integration` |
| 3 | At least one approving review exists | `gh pr view "$PROMO" --json reviews -q '[.reviews[]\|select(.state=="APPROVED")]\|length'` | `1` or more |
| 4 | No approver is a machine account | `gh pr view "$PROMO" --json reviews -q '[.reviews[]\|select(.state=="APPROVED")\|.author.login]\|map(select(endswith("[bot]")))\|length'` | `0` |
| 5 | Every approver appears in CODEOWNERS | see SELF-VERIFY `codeowner` field | `YES` |
| 6 | The promotion merge has two parents | `git fetch -q origin && git rev-list --parents -n1 origin/main \| wc -w` | `3` |
| 7 | `main` now contains the promoted head | `git merge-base --is-ancestor <promoted-sha> origin/main && echo CONTAINED` | `CONTAINED` |
| 8 | The cycle record shows the promotion | `grep -c '^promoted	YES$' docs/merge-train/cycles/cycle-$CYCLE.tsv` | `1` |
| 9 | The generated table agrees | `grep "^| $CYCLE |" docs/merge-train.md \| grep -c 'YES'` | `1` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP_ROOT"
git fetch -q --prune origin
APPROVERS=$(gh pr view "$PROMO" --json reviews -q '[.reviews[]|select(.state=="APPROVED")|.author.login]|unique|join(" ")')
CO=YES
for a in $APPROVERS; do grep -q "@$a" CODEOWNERS || CO=NO; done
printf 'gate=%s pr=%s approvals=%s bots=%s codeowner=%s parents=%s promoted=%s row=%s\n' \
  "$(make promote-gate CYCLE="$CYCLE" | tail -1 | cut -d' ' -f1-2)" \
  "$(gh pr view "$PROMO" --json baseRefName,headRefName -q '.baseRefName+"<-"+.headRefName')" \
  "$(gh pr view "$PROMO" --json reviews -q '[.reviews[]|select(.state=="APPROVED")]|length')" \
  "$(gh pr view "$PROMO" --json reviews -q '[.reviews[]|select(.state=="APPROVED")|.author.login]|map(select(endswith("[bot]")))|length')" \
  "$CO" \
  "$(git rev-list --parents -n1 origin/main | wc -w | tr -d ' ')" \
  "$(grep -c '^promoted	YES$' docs/merge-train/cycles/cycle-$CYCLE.tsv)" \
  "$(grep "^| $CYCLE |" docs/merge-train.md | grep -c 'YES')"
```

Expected output, exactly:

```
gate=PROMOTE-GATE OK pr=main<-integration approvals=1 bots=0 codeowner=YES parents=3 promoted=1 row=1
```

(`approvals` may exceed `1`; it must never be `0`.)

**STOP rule** — if `bots` is anything other than `0`, a machine account approved a promotion. Stop, revert the
promotion (L0-03-11), and record a TRAIN HALT: §98.2 Phase 1 verifies negatively that *"an approval from a
machine account does not satisfy branch protection — CODEOWNERS is generated to contain human identities only"*
(spec L9019), and a promotion that passed with one means CODEOWNERS or branch protection is wrong, not that the
rule is soft. If `approvals=0`, protection is not armed on `main` at all; stop every cycle until it is.

If `gate` is `PROMOTE-GATE FAIL`, **do not open the PR** and do not re-run the gate hoping for a different
answer. Read the failing `GATE-FAIL P<n>` lines and act on them; `P8` (freeze window closed) is not overridable
by anything short of a SEV-1, and even then the operation is a rollback, not a promotion — invariant 27 (spec
L9489): *"Rollback is preferred to hotfix, and requires no prior approval during a SEV-1."*

If **no second human exists** to give the Code Owner approval — the bootstrap condition — do not self-approve and
do not disable the requirement. Record a bootstrap exception in `exceptions.yaml` with an expiry, a named owner
and a deactivation trigger (§54.2; L0D-19), which makes it inherit invariant 77 and SIG-39 and gives it AT-039's
behaviour: *"When the headcount trigger is met or the expiry passes, the gate arms or the exception surfaces as
Blocking drift — it cannot lapse silently"* (spec L9361).

---

### L0-03-10 — Roll back a bad `integration` merge

**Size:** M · **Dependencies:** L0-03-06

Trigger: post-merge CI red at L0-03-06 step 5, `make promote-check` printing `CONTRACTS-DRIFT`, or
`train-owners.sh` failing after a merge that individually passed `lane-guard`.

**The default is revert, and the default is not a judgment call.** Invariant 27 (spec L9489): *"Rollback is
preferred to hotfix."* Roll-forward is chosen only when the revert would itself be non-reversible in the §28.1
sense — *"Data deletion, an irreversible external side effect, or a destructive migration"* (spec L2588) — and
that choice is L0D-08 with a decision record, never an inclination.

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
git checkout integration && git pull --ff-only

# 1. Name the merge. It is in the cycle record; do not guess it from the log.
BAD=$(awk -F'\t' -v l="L$n" '$1==l && $2=="MERGED"{for(i=1;i<=NF;i++) if($i~/^merge=/){sub("merge=","",$i);print $i}}' \
      "docs/merge-train/cycles/cycle-$CYCLE.tsv")
git show --stat --oneline -s "$BAD"

# 2. Revert the merge commit, keeping the first parent (integration's own history).
git revert -m 1 --no-edit "$BAD"
REVERT=$(git rev-parse HEAD)
git push origin integration

# 3. Prove integration is back where it was for that lane's paths.
git diff --stat "$CYCLE_BASE" HEAD -- $(awk -F'\t' -v l="$n" '$1==l{print $2}' lane-paths.tsv | tr '\n' ' ')
make promote-check
./train-owners.sh "$CYCLE_BASE" HEAD

# 4. Record it. Amend the lane's line in place, then append the revert fact.
sed -i "s|^L$n	MERGED	pr=\([0-9]*\)	merge=$BAD|L$n	SKIPPED	reason=REVERTED	pr=\1	merge=$BAD	revert=$REVERT|" \
  "docs/merge-train/cycles/cycle-$CYCLE.tsv"
make train-log
git add docs/merge-train.md "docs/merge-train/cycles/cycle-$CYCLE.tsv"
git commit -m "L0-03-10: revert lane $n merge $BAD on integration (L0D-08)"
git push origin integration

# 5. Tell the lane, with the evidence.
gh pr comment "$PR" --body "$(printf '**MERGE TRAIN — MERGE REVERTED (cycle %s, lane %s)**\n\nMerge `%s` was reverted on `integration` by `%s` under L0D-08.\nReason: <paste the literal failing output>.\n\nRe-landing: your next PR must FIRST revert the revert, or the change will appear\nempty to git. On a fresh branch off `integration`:\n\n```bash\ngit revert --no-edit %s\n```\n\nThen re-apply your fix on top and open a new PR. Do not force-push over the revert.\n' "$CYCLE" "$n" "$BAD" "$REVERT" "$REVERT")"
```

**The revert-the-revert rule is the part people forget.** Once a merge is reverted, re-merging the same branch
brings nothing: git sees the content already present-then-removed and produces an empty diff. The lane's
re-landing PR must revert the revert first. State it in the comment every time; the AI lane executor has no repo
context and will not deduce it.

**Cycle disposition after a revert.** The train **continues** to the next lane position. A revert restores
`integration` to a state that already passed the gate, so the remaining lanes merge against a known-good base.
Only a revert that itself fails aborts the cycle, and that is a TRAIN HALT with `CLASSIFICATION: BAD-INTEGRATION`.

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | The revert commit exists and names the merge | `git log -1 --format=%s HEAD~0 \| grep -c "$(git log -1 --format=%h "$BAD")"` — or `git show -s --format=%B "$REVERT" \| grep -c "$BAD"` | `1` |
| 2 | The lane's paths are back to the cycle base | `git diff --quiet "$CYCLE_BASE" HEAD -- <lane paths> && echo RESTORED` | `RESTORED` |
| 3 | Contracts still frozen | `make promote-check` | `CONTRACTS-FROZEN OK` |
| 4 | `integration` CI green after the revert | `gh run list --branch integration --limit 1 --json conclusion -q '.[0].conclusion'` | `success` |
| 5 | The cycle record shows the revert | `grep -c "^L$n	SKIPPED	reason=REVERTED" docs/merge-train/cycles/cycle-$CYCLE.tsv` | `1` |
| 6 | No `MERGED` line survives for that lane | `grep -c "^L$n	MERGED" docs/merge-train/cycles/cycle-$CYCLE.tsv` | `0` |
| 7 | The lane was told, including the revert-the-revert instruction | `gh pr view "$PR" --json comments -q '[.comments[].body]\|map(select(contains("git revert --no-edit")))\|length'` | `1` or more |
| 8 | No history was rewritten | `git log --format=%H origin/integration \| grep -c "$BAD"` | `1` — the bad merge is still in history, reverted, not erased |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP_ROOT"
LANEPATHS=$(awk -F'\t' -v l="$n" '$1==l{sub(/\/\*$/,"",$2); print $2}' lane-paths.tsv | tr '\n' ' ')
printf 'revert=%s restored=%s frozen=%s ci=%s record=%s merged_gone=%s told=%s history=%s\n' \
  "$(git show -s --format=%B "$REVERT" | grep -c "$BAD")" \
  "$(git diff --quiet "$CYCLE_BASE" HEAD -- $LANEPATHS && echo RESTORED || echo DIVERGED)" \
  "$(make promote-check | tail -1)" \
  "$(gh run list --branch integration --limit 1 --json conclusion -q '.[0].conclusion')" \
  "$(grep -c "^L$n	SKIPPED	reason=REVERTED" docs/merge-train/cycles/cycle-$CYCLE.tsv)" \
  "$(grep -c "^L$n	MERGED" docs/merge-train/cycles/cycle-$CYCLE.tsv)" \
  "$(gh pr view "$PR" --json comments -q '[.comments[].body]|map(select(contains("git revert --no-edit")))|length')" \
  "$(git log --format=%H origin/integration | grep -c "$BAD")"
```

Expected output, exactly:

```
revert=1 restored=RESTORED frozen=CONTRACTS-FROZEN OK ci=success record=1 merged_gone=0 told=1 history=1
```

**STOP rule** — if `history` is `0`, the bad merge has been removed from `integration`'s history, meaning someone
force-pushed or reset the branch instead of reverting. Stop everything. That destroys the audit trail the whole
records model rests on — invariant 47 (spec L9515): *"History is append-only for state, decisions, approvals and
records; records are not deleted and state changes are recorded, not overwritten."* Restore `integration` from a
lane clone's reflog, record a TRAIN HALT with `CLASSIFICATION: BAD-INTEGRATION`, and treat the missing history as
a Level 5 finding. If `restored=DIVERGED`, the revert did not undo everything the merge introduced — do **not**
hand-edit files to close the gap; revert the remaining merges of this cycle in reverse train order and re-open the
cycle. If `ci` is still `failure` after a clean revert, the failure predates this merge: the cycle base itself was
red, and the correct record is a TRAIN HALT with `CLASSIFICATION: BAD-INTEGRATION` naming `$CYCLE_BASE`.

---

### L0-03-11 — Roll back a bad promotion on `main`

**Size:** M · **Dependencies:** L0-03-09

`main` is protected: no force push, no direct push, no deletion (§11.3, spec L869). Rolling back a promotion is
therefore a **revert pull request**, and it goes through the same human gate the promotion did. There is no
break-glass shortcut here that is not the documented break-glass procedure of §54 with an audit record (§11.3,
spec L870).

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
git fetch --prune origin
PROMO_SHA=$(git rev-parse origin/main)          # the promotion merge commit
git show --stat -s "$PROMO_SHA"

# 1. Revert on a branch. L0's own branch, not a lane branch — root/docs are L0-owned,
#    but this branch touches whatever the promotion carried, so it is L0's by residual ownership.
git checkout -b "l0/revert-promo-$CYCLE" "origin/main"
git revert -m 1 --no-edit "$PROMO_SHA"
REVERT=$(git rev-parse HEAD)
git push -u origin "l0/revert-promo-$CYCLE"

# 2. Open the revert PR against main.
gh pr create --base main --head "l0/revert-promo-$CYCLE" \
  --title "REVERT promotion of cycle $CYCLE" \
  --label "promotion,revert" \
  --body "$(printf 'Reverts promotion merge %s (cycle %s) under L0D-08.\n\nObserved failure:\n```\n<paste literal output>\n```\n\nInvariant 27: rollback is preferred to hotfix. Reversibility class of the reverted\nchange per Section 28.1: <fully-reversible | partially-reversible | non-reversible>.\nIf partially- or non-reversible, the compensating action or recovery strategy is named here:\n<name it, or state NONE REQUIRED>.\n' "$PROMO_SHA" "$CYCLE")"

RPR=$(gh pr list --base main --head "l0/revert-promo-$CYCLE" --state open --json number -q '.[0].number')
# 3. Human Code Owner approval, exactly as for a promotion. No self-approval (Section 11.3, spec L865).
gh pr view "$RPR" --json reviews -q '[.reviews[]|select(.state=="APPROVED")|.author.login]|join(",")'
gh pr merge "$RPR" --merge --delete-branch

# 4. Bring integration back in line with main, so the next cycle's base descends from the revert.
git checkout integration && git pull --ff-only
git merge --no-ff -m "sync integration with reverted main (cycle $CYCLE)" origin/main
git push origin integration

# 5. Record it.
sed -i "s|^promoted\tYES$|promoted\tREVERTED|" "docs/merge-train/cycles/cycle-$CYCLE.tsv"
sed -i "s|^notes\t.*|notes\tpromotion reverted: $REVERT|" "docs/merge-train/cycles/cycle-$CYCLE.tsv"
make train-log
git add docs/merge-train.md "docs/merge-train/cycles/cycle-$CYCLE.tsv"
git commit -m "L0-03-11: promotion of cycle $CYCLE reverted (L0D-08)"
git push origin integration
```

**Reversibility classification is declared, not assumed.** §28.1 (spec L2583–L2588) requires every change to
declare its class at plan time and forbids describing a `non-reversible` change as rollback-able. The revert PR
body carries the classification of what is being undone; if it is `partially-reversible`, the compensating action
must exist, be tested and be named (spec L2587). A promotion whose contents were `non-reversible` is not rolled
back by this task at all — it is recovered by the named recovery strategy, normally restore-from-backup, and that
is an L0D-08 decision with a decision record.

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | The revert reached `main` by PR | `gh pr view "$RPR" --json state,baseRefName -q '.state+" "+.baseRefName'` | `MERGED main` |
| 2 | A human approved it | `gh pr view "$RPR" --json reviews -q '[.reviews[]\|select(.state=="APPROVED")\|.author.login]\|map(select(endswith("[bot]")))\|length'` | `0`, with at least one approver |
| 3 | `main` still contains the bad promotion, reverted not erased | `git fetch -q origin; git log --format=%H origin/main \| grep -c "$PROMO_SHA"` | `1` |
| 4 | `main` no longer carries the reverted content | `git diff --quiet origin/main <the pre-promotion main sha> && echo RESTORED` | `RESTORED` |
| 5 | `integration` descends from the reverted `main` | `git merge-base --is-ancestor origin/main origin/integration && echo SYNCED` | `SYNCED` |
| 6 | The cycle record says `REVERTED` | `grep -c '^promoted	REVERTED$' docs/merge-train/cycles/cycle-$CYCLE.tsv` | `1` |
| 7 | The reversibility class is declared in the PR body | `gh pr view "$RPR" --json body -q .body \| grep -cE 'fully-reversible|partially-reversible|non-reversible'` | `1` or more |
| 8 | No force push happened on `main` | `gh api repos/{owner}/{repo}/branches/main/protection -q '.allow_force_pushes.enabled'` | `false` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP_ROOT"
git fetch -q --prune origin
PRE=<the main sha immediately before the promotion>
printf 'pr=%s bots=%s history=%s restored=%s synced=%s record=%s class=%s force=%s\n' \
  "$(gh pr view "$RPR" --json state,baseRefName -q '.state+" "+.baseRefName')" \
  "$(gh pr view "$RPR" --json reviews -q '[.reviews[]|select(.state=="APPROVED")|.author.login]|map(select(endswith("[bot]")))|length')" \
  "$(git log --format=%H origin/main | grep -c "$PROMO_SHA")" \
  "$(git diff --quiet origin/main "$PRE" && echo RESTORED || echo DIVERGED)" \
  "$(git merge-base --is-ancestor origin/main origin/integration && echo SYNCED || echo DIVERGED)" \
  "$(grep -c '^promoted	REVERTED$' docs/merge-train/cycles/cycle-$CYCLE.tsv)" \
  "$(gh pr view "$RPR" --json body -q .body | grep -cE 'fully-reversible|partially-reversible|non-reversible')" \
  "$(gh api repos/{owner}/{repo}/branches/main/protection -q '.allow_force_pushes.enabled')"
```

Expected output, exactly:

```
pr=MERGED main bots=0 history=1 restored=RESTORED synced=SYNCED record=1 class=1 force=false
```

**STOP rule** — if `force` is `true`, force pushing is enabled on `main` and §11.3 (spec L869: *"Block force
pushes and deletions on the default branch"*) is not in effect. Stop every cycle and every promotion until branch
protection is corrected; this is L5's `access/**` work and L0 files it as a Blocking-class item, not as a
convenience to work around. If `restored=DIVERGED`, the revert did not undo the promotion cleanly — the change
was not `fully-reversible` and §28.1 forbids calling this a rollback (spec L2588: *"Never described as
rollback-able"*). Record a TRAIN HALT with `DECISION TAKEN: ROLL-FORWARD`, `DECISION ID: L0D-08`, and execute the
named recovery strategy instead. If `history` is `0`, `main`'s history was rewritten: same Level 5 treatment as
L0-03-10's STOP rule, invariant 47.

---

### L0-03-12 — Starvation accounting and the constraint diagnosis

**Size:** M · **Dependencies:** L0-03-08

**The starvation rule, stated once.**

> A lane that cannot merge is skipped. The train does not stop, the remaining lanes merge in order behind it, and
> the skip is recorded as a **train state**, never as a lane failure. Consecutive skips are counted, and the count
> — not anyone's impression — triggers a constraint diagnosis that L0 answers.

Three parts, each with its own mechanism.

**Part 1 — the no-hold rule.** One blocked lane never halts the other four. `L0-00-charter.md` §9: *"the train
does not stop for it, and the remaining lanes merge in order behind it."* This is safe because of PARTITION.md
rule 4 (*"No cross-lane imports. A lane consumes another lane's output only through `contracts/**` or a published
artifact"*) and rule 2 (contracts frozen in Phase 0): position 5 validates against the frozen contract, not
against whatever position 1 did or did not merge this week. The order of §2 is a sequence, not a dependency chain
of merges.

**Part 2 — attribution.** A skip is never written as a lane's fault, and never appears in any evidence bundle as
one. The spec's own rule for the analogous case is §83.4 (spec L7360): *"Where the cause is Ready-queue
starvation, the signal routes to the Team Lead as a planning-capacity signal and the individual receives no
negative signal at all."* Here the analogue is exact — the lane executor has no judgment authority
(PARTITION.md §"AI developer profile"), so a lane that cannot merge is by construction a defect in the task, the
contract, or the gate, all three of which are L0's.

**Part 3 — the counters and what they trigger.** Counted from the cycle records, mechanically:

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
for n in 1 4 2 3 5; do
  streak=0
  for f in $(ls docs/merge-train/cycles/cycle-*.tsv | LC_ALL=C sort -r); do
    d=$(awk -F'\t' -v l="L$n" '$1==l{print $2; exit}' "$f")
    case "$d" in
      SKIPPED) streak=$((streak+1)) ;;
      MERGED|HALTED) break ;;
      NONE|"") break ;;          # NONE is not a skip; it stops the streak without incrementing
    esac
  done
  printf 'L%s\tskip_streak=%s\n' "$n" "$streak"
done
```

| Consecutive `SKIPPED` | L0's obligation | Anchor |
|---|---|---|
| 1 | Note it in the cycle record. No further action | — |
| **2** | Open a **constraint diagnosis**: name which of the seven §73.2 categories binds (spec L6007–L6021) — Review, Verification, Planning, Architecture, Engineering capacity, Product priority, Founder-decision latency. Record it as a decision record via the §97.2 record-decision CLI, and put its id in the next cycle's `notes` | §73.2; `L0-00-charter.md` §8.2 Monday 10:00 (*"which constraint binds this week"*) |
| **3** | L0 removes the cause itself: either land the contract change under a CCR (L0D-06) so the lane can proceed, or re-scope the lane's current phase and record it, or declare the phase carried with a review date (L0D-20's shape). The lane is **not** asked to try again unchanged | PARTITION.md §"AI developer profile"; L0D-06, L0D-07 |
| **4 or more** | Not permitted to occur. If it does, the lane has been starved for a month of cycles and the failure is L0's cadence, recorded as a TRAIN HALT with `CLASSIFICATION: OTHER` and carried into the Friday bootstrap-log entry under `records/bootstrap-log/` (§95.4) | §95.4 staleness detector; `L0-00-charter.md` §8.2 |

The thresholds `2`, `3` and `4` are **initial values** and their calibration is a merge-train matter under
**L0D-07**; each change is a decision record, exactly like any deviation from the merge order. They are not a
lane-visible setting and no lane may propose or apply one (C-02).

**The reverse rule — the train never waits for the lanes.** A cycle in which every lane is `NONE` still opens,
still closes, and still writes a cycle record. An empty cycle is evidence; a skipped cycle is a hole in the
record where a starvation count should be.

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
# Emit the diagnosis when a streak reaches 2. Substitute the category from the Section 73.2 taxonomy.
n=1
cat > /tmp/constraint-diagnosis.md <<'DIAG'
CONSTRAINT DIAGNOSIS — merge train

LANE:                 L<n>
CONSECUTIVE SKIPS:    <count>
CYCLES:               <list of cycle numbers, oldest first>
SKIP REASONS:         <REBASE | GATE | REVERTED, per cycle>

BINDING CONSTRAINT (Section 73.2, exactly one of the seven):
  Review | Verification | Planning | Architecture | Engineering capacity |
  Product priority | Founder-decision latency

EVIDENCE
<paste the literal train-admit.sh lines from each cycle>

WHAT L0 CHANGES
<the contract change (CCR, L0D-06), the re-scope, or the carried phase — an action L0 takes,
 never an instruction to the lane to try again unchanged>

ATTRIBUTION
This is a train state and a constraint on the programme. It is not a lane performance signal
and appears in no evidence bundle as one (Section 83.4).

DECISION RECORD: records/decisions/<written via the record-decision CLI, Section 97.2>
DECISION ID:     L0D-07
DIAG
cp /tmp/constraint-diagnosis.md "docs/merge-train/cycles/cycle-$CYCLE.diagnosis-L$n.md"
git add "docs/merge-train/cycles/cycle-$CYCLE.diagnosis-L$n.md"
git commit -m "L0-03-12: constraint diagnosis for lane $n (L0D-07)"
git push origin integration
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | A streak is computable for every lane | the counter loop above | five lines, `L1 L4 L2 L3 L5`, each with `skip_streak=<integer>` |
| 2 | `NONE` never increments a streak | craft a cycle file with `L1	NONE` and re-run the loop | `L1	skip_streak=0` |
| 3 | Every streak of 2 or more has a diagnosis file | see SELF-VERIFY `undiagnosed` field | `0` |
| 4 | Every diagnosis names exactly one §73.2 category | `grep -c 'BINDING CONSTRAINT' docs/merge-train/cycles/*.diagnosis-*.md` per file | `1` each |
| 5 | No lane is ever recorded as at fault | `grep -ril 'lane failure\|lane is behind\|lane fault' docs/merge-train/ \| wc -l` | `0` |
| 6 | No streak reaches 4 | see SELF-VERIFY `max_streak` | `3` or less |
| 7 | Every cycle file has all five lanes, so no streak is computed over a hole | `for f in docs/merge-train/cycles/cycle-*.tsv; do c=$(grep -c '^L[12345]	' "$f"); [ "$c" -eq 5 ] \|\| echo "$f=$c"; done; echo DONE` | `DONE` alone |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP_ROOT"
MAX=0; UND=0
for n in 1 4 2 3 5; do
  streak=0
  for f in $(ls docs/merge-train/cycles/cycle-*.tsv | LC_ALL=C sort -r); do
    d=$(awk -F'\t' -v l="L$n" '$1==l{print $2; exit}' "$f")
    case "$d" in SKIPPED) streak=$((streak+1)) ;; *) break ;; esac
  done
  [ "$streak" -gt "$MAX" ] && MAX=$streak
  if [ "$streak" -ge 2 ] && [ -z "$(ls docs/merge-train/cycles/*.diagnosis-L$n.md 2>/dev/null)" ]; then
    UND=$((UND+1))
  fi
done
printf 'max_streak=%s undiagnosed=%s holes=%s blame=%s\n' \
  "$MAX" "$UND" \
  "$(for f in docs/merge-train/cycles/cycle-*.tsv; do c=$(grep -c '^L[12345]	' "$f"); [ "$c" -eq 5 ] || echo x; done | wc -l | tr -d ' ')" \
  "$(grep -ril 'lane failure\|lane is behind\|lane fault' docs/merge-train/ | wc -l | tr -d ' ')"
```

Expected output on a healthy programme:

```
max_streak=0 undiagnosed=0 holes=0 blame=0
```

`max_streak` may legitimately be `1`, `2` or `3`; `undiagnosed`, `holes` and `blame` must be `0` always.

**STOP rule** — if `undiagnosed` is non-zero, a lane has been skipped twice with no diagnosis: **do not open the
next cycle** until the diagnosis exists. Repeat skipping without diagnosis is precisely how one blocked lane
quietly becomes a dead lane, and §73.2 exists to force the cause to be named rather than felt (*"Time-to-merge is
a symptom, not a hiring trigger. Diagnose the cause first."*, spec L6009). If `max_streak` is `4` or more, stop
the train: the programme has a lane it is not building, and continuing to run cycles around it manufactures the
appearance of progress. Record the TRAIN HALT, carry it into the Friday bootstrap-log entry (§95.4), and treat
the lane's next task as an L0 authoring task until it merges again. If `holes` is non-zero, the counters are
computed over incomplete cycle records and every number above is unreliable — fix L0-03-08 first.

---

## 4. Quick reference — one cycle, start to finish

**Commands**

```bash
cd "$CP_ROOT" && git checkout integration && git pull --ff-only
make train-preflight                                   # PREFLIGHT OK              [T03]
LAST=$(ls docs/merge-train/cycles/cycle-*.tsv 2>/dev/null | sed 's/.*cycle-\([0-9]*\)\.tsv/\1/' | LC_ALL=C sort | tail -1)
export CYCLE=$(printf '%03d' $(( 10#${LAST:-0} + 1 )))
export CYCLE_BASE=$(git rev-parse origin/integration)  # freeze the base           [T03]

for n in 1 4 2 3 5; do                                 # TRAIN ORDER — never vary  [T04]
  PR=$(gh pr list --base integration --state open --label "lane-$n" \
       --json number,headRefName,isDraft,createdAt \
       --jq '[.[]|select(.isDraft==false)|select(.headRefName|startswith("lane/'"$n"'/"))]
             | sort_by(.createdAt) | .[0].number // empty')
  [ -z "$PR" ] && { printf 'L%s\tNONE\n' "$n" >> "docs/merge-train/cycles/cycle-$CYCLE.tsv"; continue; }
  ./train-admit.sh "$n" "$PR"                          # verdict routes the lane
done
#   ADMIT     -> T06  run the lane SELF-VERIFY, gh pr merge --merge, re-verify
#   REBASE    -> T05  post the rebase directive; L0 never rebases a lane branch
#   GATE-FAIL -> T07  post the verbatim gate output; record SKIPPED reason=GATE
#   HALT      -> T02  TRAIN HALT, CLASSIFICATION: PARTITION-VIOLATION

make train-log && git add -A && git commit -m "close cycle $CYCLE" && git push origin integration   [T08]
make promote-gate CYCLE="$CYCLE"                       # PROMOTE-GATE OK           [T09]
gh pr create --base main --head integration --title "PROMOTE cycle $CYCLE: integration -> main"
# red integration after a merge -> T10 revert (-m 1). bad promotion -> T11 revert PR on main.
# two consecutive skips on a lane -> T12 constraint diagnosis, Section 73.2 category, L0D-07.
```

---

## 5. What this file does not decide

| Matter | Owner |
|---|---|
| Any deviation from `L1 → L4 → L2 → L3 → L5` | L0D-07, decision record required |
| Revert versus roll-forward on a broken `integration` | L0D-08 |
| Whether to promote at all | L0D-09 |
| Approving the contract change that unblocks a starved lane | L0D-06 |
| Extending `lane-paths.tsv` when a path resolves `UNASSIGNED` | L0D-04 |
| Which required status check contexts are armed, and when | L0 (a lane adding one is F-07); §98.2 names the contexts each phase adds |
| Branch-protection configuration itself | L5 `access/**`; L0 files a Blocking-class item, never edits it |
| The bootstrap exception when no second human can approve | L0D-19, `exceptions.yaml` with expiry, owner and deactivation trigger (§54.2, AT-039) |

Nothing in a lane PR description, a lane blocker issue, a lane comment or a lane's own plan file moves any row of
this table. The merge train's order, cadence, conflict resolution, revert-versus-roll-forward and promotion are
L0's alone (`L0-00-charter.md` §3, pillar 3).
