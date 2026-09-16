# L0-02 — THE LANE GUARD

**Lane:** L0 Integrator · **Executor:** the human lead (this file is not executed by an AI developer)
**Owns exclusively:** repository-root files, `contracts/**`, `CODEOWNERS`, `Makefile`, `docs/**` (PARTITION.md §"The five build lanes")
**Frozen partition:** `C:/D_Drive/PS/MultiProduct/Code/implementation/PARTITION.md` — this file never contradicts it.
**Spec:** `C:/D_Drive/PS/MultiProduct/Research/MultiProduct_MasterSpec_v4.0.md` (v4.0)

> **What this file is.** `L0-00-charter.md` tasks **L0-00-03** and **L0-00-04** stand up the *first cut* of the
> partition map and the guard — enough to prove the idea works locally. This file is the **production version**:
> the machine-readable manifest, the guard engine, the GitHub Actions workflow that makes it binding on every lane
> pull request, the CODEOWNERS generator that mirrors the manifest, the exact error text an AI developer sees, and
> the override procedure. Everything here is real, copy-pasteable code.
>
> **Compatibility with L0-00.** `lane-guard.sh` v2 keeps v1's calling convention (`lane-guard.sh <lane> <base> <head>`)
> and v1's two terminal lines (`LANE-GUARD OK`, `LANE-GUARD FAIL: N violation(s)`) **byte-for-byte**, so
> L0-00-04's SELF-VERIFY block still produces its documented output after v2 is installed. `lane-paths.tsv` is
> **updated by B-05/FD-003 and FD-055**: L0-00-03's manifest now carries forty-one rules — the original twenty-two plus the `0\t.github/workflows/lane-guard.yml` carve-out (FD-003) plus additional L0-owned paths and the `gate-state/**` row (FD-055). One acceptance
> criterion of L0-00-01 is corrected here for cause; see **L0D-LG-5** in §11.

---

## 1. Why this check is load-bearing

Five AI developers with no repo context are about to write to one repository at the same time. The single
assumption that makes that safe is PARTITION.md rule 1 — **one owner per path** — and an assumption enforced by
nothing is a wish. The spec has a name for this failure and states it twice:

> §53.1 — *"no control that can be rewritten by the credential it is checking is a control"*
> §33.2 (D89) — *"a bypass actor is exempt from every rule in the ruleset it is listed on … so a compensator
> sitting inside the bypassed ruleset compensates for nothing"*

The lane guard has exactly the shape the spec's `renovate-path-guard` has (§33.2): a required status check that
**fails any pull request whose diff touches a file outside a declared manifest**. It is designed here against the
same three rules the spec makes binding on that guard:

| Spec rule | Anchor | How the lane guard satisfies it |
|---|---|---|
| The check must be emitted by a job carrying **no `if:` and no path filter**; a skipped required check counts as satisfied | §33.2 | The `lane-guard` job has no `if:` and no `paths:` filter. Every pull request produces a real conclusion |
| The compensator must not sit inside the thing it compensates for | §33.2, D89 | The ruleset carrying the required check has an **empty `bypass_actors` list** (task T08) |
| No control may be rewritable by what it inspects | §53.1 | The guard reads its manifest, its owners table, its exception register and its own script from the **base ref**, never from the pull-request head; and the workflow file at head is compared byte-for-byte against a frozen contract at base |

---

## 2. The five failure modes, and the mechanism that stops each

| # | Failure mode | What it looks like | Mechanism that stops it | Where |
|---|---|---|---|---|
| F1 | A lane writes into another lane's tree | `lane/1/*` commits `reconciler/diff.py` | Ownership check against `lane-paths.tsv` | §5, §6 |
| F2 | A lane invents a new top-level tree nobody owns | `lane/3/*` commits `telemetry/agent.yaml` | Residual rule `X` → unassigned is blocked for everyone (L0D-04) | §5 |
| F3 | A lane edits the guard that constrains it | `lane/2/*` (which owns `.github/workflows/**`) edits `.github/workflows/lane-guard.yml` | `GUARD-CRITICAL` class + byte-freeze against `contracts/ci/lane-guard.yml.frozen` | §6, §7 |
| F4 | A lane deletes the guard job so the check never reports | the job disappears from the merge ref | The check is a **required** status context; an unreported required context leaves the PR permanently pending, which blocks the merge | §8, T08 |
| F5 | A lane launders a foreign path — rename, delete, symlink, submodule | `git mv reconciler/x registries/x`; or a symlink `registries/link → ../reconciler` | `--no-renames` (old and new path both judged); delete is judged on the old path; mode `120000`/`160000` classes | §6 |

Everything below implements this table.

---

## 3. The enforcement stack — six layers, weakest first

| Layer | Artifact | Binding? | Defeated by | Backstopped by |
|---|---|---|---|---|
| 1 | `make lane-guard` run locally by the lane before pushing | Advisory | Not running it | Layer 3 |
| 2 | `CODEOWNERS`, generated from the manifest | Review-routing + Code-Owner-review requirement (§11.3) | Nothing — but it routes, it does not block a diff | Layer 3 |
| 3 | `.github/workflows/lane-guard.yml`, required status check `lane-guard` | **Binding** | Editing the workflow | Layer 4 |
| 4 | Byte-freeze: head's workflow ≡ `contracts/ci/lane-guard.yml.frozen` at base | **Binding** | Deleting the job entirely | Layer 5 |
| 5 | Required-context pending-forever rule + ruleset with **zero** bypass actors | **Binding** | Nothing a lane can do | Layer 6 |
| 6 | `make promote-check` contract freeze hash + L0's local `make lane-guard` re-run during the merge train | **Binding, human** | Nothing | — |

A lane agent can defeat layers 1–2. It cannot defeat 3–6 without a human with admin rights, which is exactly the
intent: **the override procedure of §9 is the only way through, and it requires L0.**

---

## 4. Ownership of the workflow file — the one genuine conflict, and its resolution

PARTITION.md gives `.github/workflows/**` to **L2, exclusively**. GitHub will only run a workflow that lives in
`.github/workflows/`. So the file that enforces the partition must sit inside a tree the partition gives to a
lane. That is F3 above, and it is resolved **without amending the frozen partition**:

| Decision | Statement |
|---|---|
| **L0D-LG-1** | The lane-guard workflow's *content* is an L0 artifact frozen at `contracts/ci/lane-guard.yml.frozen`. `contracts/**` is L0-owned and FROZEN in Phase 0 (PARTITION.md rule 2) |
| **L0D-LG-2** | The workflow's *location* `.github/workflows/lane-guard.yml` remains L2-owned per PARTITION.md. L2 may not change its bytes: the guard classifies it `GUARD-CRITICAL` and additionally compares it byte-for-byte against the frozen contract on every pull request |
| **L0D-LG-3** | L0 places the file once, on `integration`, in Phase 0 — **before any lane branch exists**, therefore before `.github/workflows/**` has an L2 branch to be taken from. This is the §95.2 bootstrap-arming pattern: configured before the party it constrains exists. It is a one-time placement, recorded, and never repeated |

Nothing in PARTITION.md is contradicted: L2 still owns the path; L2 simply may not edit one file in it, exactly as
L2 may not edit `contracts/**`. A Contract Change Request (charter §7.2) is how L2 asks for the workflow to change.

---

## 5. The path-ownership manifest — machine-readable, one file, no parser

The manifest is `lane-paths.tsv` at the repository root, authored by **L0-00-03** and reproduced here for
reference. **This file is not modified by L0-02.** TSV rather than YAML so the guard needs no parser and no
dependency (L0D-04).

```
# lane-paths.tsv — machine-readable form of PARTITION.md. L0-owned (L0D-04).
# Format: <lane><TAB><sh glob>. First match wins, so order is significant.
# Lane X = unassigned nested path: blocked for everyone, escalates to L0.
# Lane 0 = L0 (integrator). The final catch-all covers repository-root files.
1	schemas/registry/*
1	schemas/product/*
1	registries/*
1	validators/registry/*
2	.github/workflows/*
2	templates/workflows/*
2	tools/evidence/*
3	reconciler/*
3	tools/provision/*
3	validators/drift/*
4	schemas/records/*
4	metrics/*
4	tools/records/*
5	access/*
5	infra/*
5	ops-vm/*
5	notify/*
5	assets/*
0	contracts/*
0	docs/*
X	*/*
0	*
```

**Semantics, exact.** Each pattern is matched with POSIX `sh` `case`. In `case`, `*` matches `/`, so
`registries/*` covers `registries/a/b/c.yaml` at any depth. First match wins, so order is significant:
lane trees, then L0 trees, then the residual `X` rule (any *nested* path not claimed above), then the
root catch-all `0 *` (any *top-level* file belongs to L0).

**Every root file this document adds is covered by the existing `0 *` catch-all**, so the manifest keeps exactly
forty-one rules (including the `0\t.github/workflows/lane-guard.yml` carve-out and the `gate-state/**` row from FD-055) and L0-00-03's acceptance criteria remain true (updated to `41`):

| New root file | Owner by rule | Purpose |
|---|---|---|
| `lane-owners.tsv` | `0 *` | lane → human reviewer login (T01) |
| `lane-guard-exceptions.tsv` | `0 *` | the override register (T03) |
| `lane-guard-selftest.sh` | `0 *` | adversarial proof the guard fails what it must (T04) |
| `codeowners-gen.sh` | `0 *` | CODEOWNERS generator (T05) |
| `lane-guard-ruleset.json` | `0 *` | the ruleset that makes the check required (T08) |

### 5.1 The second manifest: `lane-owners.tsv`

```
# lane-owners.tsv — L0-owned. lane <TAB> @github-login <TAB> display name.
# HUMAN IDENTITIES ONLY. A machine account here would let a machine approval
# satisfy branch protection; the Phase 1 completion check tests this negatively
# (MasterSpec v4.0 §98.2; §11.3; D53).
```

### 5.2 The guard-critical set — hard-coded in the script, not in data

These paths are **the guard itself**. They are hard-coded inside `lane-guard.sh` rather than read from a data
file, because a data file is something a pull request could propose to change. Any lane 1–5 touching any of them
is a violation of class `GUARD-CRITICAL`, and **no exception may ever cover them** (§9).

```
CODEOWNERS
Makefile
contracts.sha256
lane-paths.tsv
lane-owners.tsv
lane-guard.sh
lane-guard-exceptions.tsv
lane-guard-selftest.sh
codeowners-gen.sh
lane-guard-ruleset.json
.github/workflows/lane-guard.yml
contracts/ci/lane-guard.yml.frozen
contracts/ci/lane-guard.contract.md
```

---

## 6. The guard engine — `lane-guard.sh` v2, complete

Authored by task **L0-02-02**. POSIX `sh`; no bashisms; runs identically under Git Bash on Windows and under
`ubuntu-latest` on a GitHub-hosted runner.

```sh
#!/usr/bin/env sh
# =============================================================================
# lane-guard.sh — v2 — L0-owned root file (PARTITION.md: "root files").
# Enforces PARTITION.md rule 1: ONE OWNER PER PATH.
#
# Usage:  ./lane-guard.sh <lane 0..5> <base-ref> <head-ref>
#
# Exit codes:
#   0  no violations                       (last line: "LANE-GUARD OK")
#   1  one or more violations              (last line: "LANE-GUARD FAIL: N violation(s)")
#   2  configuration error — FAIL CLOSED   (last line: "LANE-GUARD FAIL: configuration error")
#
# Environment overrides. The CI workflow sets these to copies taken from the
# BASE ref, so that a pull request can never supply the rules that judge it
# (MasterSpec v4.0 §53.1: no control rewritable by what it inspects).
#   LG_MAP     path to lane-paths.tsv             default: alongside this script
#   LG_OWNERS  path to lane-owners.tsv            default: alongside this script
#   LG_EXC     path to lane-guard-exceptions.tsv  default: alongside this script
#   LG_PR      pull-request number, for exception matching   default: none
#   LG_TODAY   ISO date used for expiry comparison           default: date -u +%F
# =============================================================================
set -eu

TAB=$(printf '\t')
SELF_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
MAP="${LG_MAP:-$SELF_DIR/lane-paths.tsv}"
OWN="${LG_OWNERS:-$SELF_DIR/lane-owners.tsv}"
EXC="${LG_EXC:-$SELF_DIR/lane-guard-exceptions.tsv}"
PR="${LG_PR:-none}"
TODAY="${LG_TODAY:-$(date -u +%Y-%m-%d)}"

CRITICAL="CODEOWNERS Makefile contracts.sha256 lane-paths.tsv lane-owners.tsv
lane-guard.sh lane-guard-exceptions.tsv lane-guard-selftest.sh codeowners-gen.sh
lane-guard-ruleset.json .github/workflows/lane-guard.yml
contracts/ci/lane-guard.yml.frozen contracts/ci/lane-guard.contract.md"

cfgfail() {
  printf 'LANE-GUARD CONFIGURATION ERROR: %s\n' "$*"
  printf 'The guard cannot prove the partition holds, so it refuses to pass.\n'
  printf 'This is an L0 matter. Open BLOCKER: lane-guard configuration.\n'
  printf 'LANE-GUARD FAIL: configuration error\n'
  exit 2
}

lane_name() {
  case "$1" in
    0) printf 'L0 Integrator' ;;
    1) printf 'L1 Registries & Contracts' ;;
    2) printf 'L2 Pipeline & Evidence' ;;
    3) printf 'L3 Reconciler & Provisioning' ;;
    4) printf 'L4 Records, Events & Metrics' ;;
    5) printf 'L5 Access, Infra & Ops' ;;
    X) printf 'UNASSIGNED - no lane owns this (L0D-04)' ;;
    *) printf 'UNKNOWN LANE' ;;
  esac
}

reviewer_of() {
  _l="$1"; _r=""
  if [ -f "$OWN" ]; then
    while IFS="$TAB" read -r _ln _login _disp; do
      case "$_ln" in ''|\#*) continue ;; esac
      if [ "$_ln" = "$_l" ]; then _r="$_login"; break; fi
    done < "$OWN"
  fi
  if [ -n "$_r" ]; then printf '%s' "$_r"; else printf '(no reviewer declared for lane %s)' "$_l"; fi
}

# owner_of <path> -> sets OWNER_LANE, OWNER_LINE, OWNER_PAT. No subshell.
owner_of() {
  _f="$1"; OWNER_LANE="X"; OWNER_LINE="0"; OWNER_PAT="(no rule matched)"; _n=0
  while IFS="$TAB" read -r _lane _pat; do
    _n=$((_n + 1))
    case "$_lane" in ''|\#*) continue ;; esac
    [ -n "${_pat:-}" ] || continue
    # shellcheck disable=SC2254
    case "$_f" in
      $_pat) OWNER_LANE="$_lane"; OWNER_LINE="$_n"; OWNER_PAT="$_pat"; return 0 ;;
    esac
  done < "$MAP"
  return 0
}

# --- validate configuration, fail closed -------------------------------------
[ -f "$MAP" ] || cfgfail "lane-paths.tsv not found at $MAP"
[ -f "$OWN" ] || cfgfail "lane-owners.tsv not found at $OWN"
awk -F"$TAB" '!/^#/ && NF>0 && NF!=2 {bad++} END{exit(bad?1:0)}' "$MAP" \
  || cfgfail "lane-paths.tsv has a row that is not exactly two tab-separated fields"

LANE="${1:-}"; BASE="${2:-}"; HEAD="${3:-}"
[ -n "$LANE" ] && [ -n "$BASE" ] && [ -n "$HEAD" ] \
  || cfgfail "usage: lane-guard.sh <lane 0..5> <base-ref> <head-ref>"
case "$LANE" in 0|1|2|3|4|5) : ;; *) cfgfail "lane must be 0,1,2,3,4 or 5 — got '$LANE'" ;; esac

# --- validate the exception register, fail closed -----------------------------
if [ -f "$EXC" ]; then
  _n=0
  while IFS="$TAB" read -r _id _lane _path _pr _exp _owner _trig _reason; do
    _n=$((_n + 1))
    case "${_id:-}" in ''|\#*) continue ;; esac
    [ -n "${_reason:-}" ] || cfgfail "$EXC line $_n: needs 8 tab-separated fields (id lane path pr expiry owner trigger reason)"
    case "$_id"    in EXC-LG-[0-9][0-9][0-9]) : ;; *) cfgfail "$EXC line $_n: id must match EXC-LG-NNN — got '$_id'" ;; esac
    case "$_lane"  in 0|1|2|3|4|5) : ;; *) cfgfail "$EXC line $_n: lane must be 0..5 — got '$_lane'" ;; esac
    case "$_path"  in *[*?[]*) cfgfail "$EXC line $_n: path must be literal, no glob characters — got '$_path'" ;; esac
    case "$_pr"    in ''|*[!0-9]*) cfgfail "$EXC line $_n: pr must be a pull-request number — got '$_pr'" ;; esac
    case "$_exp"   in [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]) : ;; *) cfgfail "$EXC line $_n: expiry must be YYYY-MM-DD — got '$_exp'" ;; esac
    case "$_owner" in @?*) : ;; *) cfgfail "$EXC line $_n: owner must be an @github-login — got '$_owner'" ;; esac
    [ -n "$_trig" ] || cfgfail "$EXC line $_n: deactivation_trigger is mandatory (MasterSpec v4.0 §54.2)"
    for _c in $CRITICAL; do
      [ "$_path" = "$_c" ] && cfgfail "$EXC line $_n: '$_path' is guard-critical and can never be excepted"
    done
  done < "$EXC"
fi

exception_for() {   # exception_for <path> <lane> -> prints "ID|EXPIRY|OWNER" or ""
  _p="$1"; _l="$2"
  [ -f "$EXC" ] || return 0
  _t=$(printf '%s' "$TODAY" | tr -d '-')
  while IFS="$TAB" read -r _id _lane _path _pr _exp _owner _trig _reason; do
    case "${_id:-}" in ''|\#*) continue ;; esac
    [ "$_path" = "$_p" ] || continue
    [ "$_lane" = "$_l" ] || continue
    [ "$_pr" = "$PR" ]   || continue
    _e=$(printf '%s' "$_exp" | tr -d '-')
    [ "$_e" -ge "$_t" ]  || continue
    printf '%s|%s|%s' "$_id" "$_exp" "$_owner"
    return 0
  done < "$EXC"
  return 0
}

TMP=$(mktemp -d 2>/dev/null || mktemp -d -t lg)
trap 'rm -rf "$TMP"' EXIT
: > "$TMP/viol"; : > "$TMP/over"

git diff --raw --no-renames "$BASE...$HEAD" > "$TMP/raw" 2>/dev/null \
  || git diff --raw --no-renames "$BASE"..."$HEAD" > "$TMP/raw" \
  || cfgfail "git diff failed between '$BASE' and '$HEAD'"

report() {   # report <class> <path> <ownerlane> <detail>
  _cls="$1"; _p="$2"; _o="$3"; _d="$4"
  printf '\n'
  printf 'LANE-GUARD VIOLATION [%s]\n' "$_cls"
  printf '  path         : %s\n' "$_p"
  printf '  your lane    : %s  (%s)\n' "$LANE" "$(lane_name "$LANE")"
  printf '  owner lane   : %s  (%s)\n' "$_o" "$(lane_name "$_o")"
  printf '  matched rule : lane-paths.tsv line %s  ->  %s%s%s\n' "$OWNER_LINE" "$OWNER_LANE" "$TAB" "$OWNER_PAT"
  printf '  reviewer     : %s\n' "$(reviewer_of "$_o")"
  printf '  why          : %s\n' "$_d"
  printf '  fix          : remove this path from your branch. Lane %s may not write it.\n' "$LANE"
  printf '                   git checkout %s -- "%s"     # restore the base version\n' "$BASE" "$_p"
  printf '                   git rm --cached -- "%s"     # if you added it\n' "$_p"
  printf '  need it?     : you may NOT edit it yourself. File a Contract Change Request\n'
  printf '                 (docs/escalation/CCR.md) or a blocker (docs/escalation/BLOCKER.md).\n'
  printf '                 Override requires L0 and is described in docs/lane-guard.md.\n'
  printf '  authority    : PARTITION.md rule 1 - one owner per path. No exceptions without L0.\n'
  if [ "${GITHUB_ACTIONS:-}" = "true" ]; then
    printf '::error file=%s,title=lane-guard %s::%s is owned by lane %s (%s), not lane %s. PARTITION.md rule 1.\n' \
      "$_p" "$_cls" "$_p" "$_o" "$(lane_name "$_o")" "$LANE"
  fi
  printf '%s %s\n' "$_cls" "$_p" >> "$TMP/viol"
}

report_plain() {   # report_plain <class> <path> <detail>
  _cls="$1"; _p="$2"; _d="$3"
  printf '\n'
  printf 'LANE-GUARD VIOLATION [%s]\n' "$_cls"
  printf '  path         : %s\n' "$_p"
  printf '  your lane    : %s  (%s)\n' "$LANE" "$(lane_name "$LANE")"
  printf '  why          : %s\n' "$_d"
  printf '  fix          : remove this entry from your branch and push again.\n'
  printf '  authority    : PARTITION.md rule 1 - one owner per path. No exceptions without L0.\n'
  if [ "${GITHUB_ACTIONS:-}" = "true" ]; then
    printf '::error file=%s,title=lane-guard %s::%s\n' "$_p" "$_cls" "$_d"
  fi
  printf '%s %s\n' "$_cls" "$_p" >> "$TMP/viol"
}

printf 'lane-guard v2 — lane %s (%s) — base %s — head %s — pr %s\n' \
  "$LANE" "$(lane_name "$LANE")" "$BASE" "$HEAD" "$PR"
printf 'manifest %s — %s rules\n' "$MAP" "$(grep -vc '^#' "$MAP")"

while IFS= read -r line; do
  [ -n "$line" ] || continue
  meta=${line%%"$TAB"*}
  path=${line#*"$TAB"}
  # meta is ":<srcmode> <dstmode> <srcsha> <dstsha> <status>"
  # shellcheck disable=SC2086
  set -- $meta
  dstmode="${2:-000000}"; status="${5:-M}"

  # --- illegal path shapes ---------------------------------------------------
  case "$path" in
    \"*)   report_plain "PATH-ILLEGAL" "$path" \
             "git quoted this path, so it contains non-ASCII or control bytes. The control plane is ASCII-only."
           continue ;;
    *" "*) report_plain "PATH-ILLEGAL" "$path" \
             "path contains a space. The control plane forbids spaces in tracked paths."
           continue ;;
    -*)    report_plain "PATH-ILLEGAL" "$path" \
             "path begins with '-' and is unsafe to pass to any tool."
           continue ;;
  esac

  # --- guard-critical --------------------------------------------------------
  if [ "$LANE" != "0" ]; then
    _hit=""
    for _c in $CRITICAL; do [ "$path" = "$_c" ] && _hit="$_c"; done
    if [ -n "$_hit" ]; then
      printf '\n'
      printf 'LANE-GUARD VIOLATION [GUARD-CRITICAL]\n'
      printf '  path         : %s\n' "$path"
      printf '  your lane    : %s  (%s)\n' "$LANE" "$(lane_name "$LANE")"
      printf '  owner lane   : 0  (L0 Integrator)\n'
      printf '  why          : this file IS the lane guard. A lane that can edit the guard\n'
      printf '                 is not guarded. MasterSpec v4.0 §53.1: no control that can be\n'
      printf '                 rewritten by what it inspects is a control.\n'
      printf '  fix          : git checkout %s -- "%s"\n' "$BASE" "$path"
      printf '  need it?     : NO OVERRIDE EXISTS for this class. File a Contract Change\n'
      printf '                 Request (docs/escalation/CCR.md). Only L0 may change it.\n'
      printf '  authority    : PARTITION.md rule 1 and rule 2; L0D-LG-2.\n'
      if [ "${GITHUB_ACTIONS:-}" = "true" ]; then
        printf '::error file=%s,title=lane-guard GUARD-CRITICAL::%s is the lane guard itself. Lane %s may not edit it. No override exists.\n' \
          "$path" "$path" "$LANE"
      fi
      printf 'GUARD-CRITICAL %s\n' "$path" >> "$TMP/viol"
      continue
    fi
  fi

  # --- ownership -------------------------------------------------------------
  owner_of "$path"
  if [ "$OWNER_LANE" != "$LANE" ]; then
    _exc=$(exception_for "$path" "$LANE")
    if [ -n "$_exc" ]; then
      _eid=${_exc%%|*}; _rest=${_exc#*|}; _eexp=${_rest%%|*}; _eown=${_rest#*|}
      printf '\n'
      printf 'LANE-GUARD OVERRIDE: %s permitted for lane %s by %s (expires %s, owner %s, pr %s)\n' \
        "$path" "$LANE" "$_eid" "$_eexp" "$_eown" "$PR"
      printf '%s\n' "$_eid" >> "$TMP/over"
    elif [ "$OWNER_LANE" = "X" ]; then
      report "UNASSIGNED-PATH" "$path" "X" \
        "no rule in lane-paths.tsv claims this path. Unassigned paths are blocked for everyone and escalate to L0 (L0D-04)."
    else
      report "FOREIGN-PATH" "$path" "$OWNER_LANE" \
        "PARTITION.md assigns this path to another lane, exclusively."
    fi
    continue
  fi

  # --- entry kind, inside your own tree --------------------------------------
  if [ "$status" != "D" ]; then
    case "$dstmode" in
      120000) report_plain "SYMLINK-ADDED" "$path" \
                "symlinks are forbidden: a symlink inside your tree can point at another lane's tree, which defeats the partition." ;;
      160000) report_plain "SUBMODULE-ADDED" "$path" \
                "gitlinks/submodules are forbidden in the control-plane repository." ;;
    esac
  fi
done < "$TMP/raw"

V=$(grep -c . "$TMP/viol" 2>/dev/null || printf '0')
O=$(grep -c . "$TMP/over" 2>/dev/null || printf '0')
V=$(printf '%s' "$V" | tr -d ' \n'); O=$(printf '%s' "$O" | tr -d ' \n')

printf '\n'
if [ "$V" -eq 0 ]; then
  if [ "$O" -gt 0 ]; then
    printf 'LANE-GUARD: %s override(s) applied under L0 authority. Each expires; see lane-guard-exceptions.tsv.\n' "$O"
  fi
  printf 'LANE-GUARD OK\n'
  exit 0
fi
printf 'LANE-GUARD SUMMARY\n'
sort "$TMP/viol" | awk '{c[$1]++} END{for(k in c) printf "  %-16s %d\n", k, c[k]}'
printf 'LANE-GUARD FAIL: %s violation(s)\n' "$V"
exit 1
```

### 6.1 Design notes that are not optional

| Detail | Why it is written that way |
|---|---|
| `git diff --raw --no-renames "$BASE...$HEAD"` | Three-dot is merge-base semantics, which is what a pull request actually proposes. `--no-renames` makes a rename appear as `D old` + `A new`, so moving a foreign file **out** of its tree is caught on the old path (F5) |
| `--raw`, not `--name-only` | `--raw` carries the destination file mode, which is the only way to see a symlink (`120000`) or a gitlink (`160000`) |
| Diff written to `$TMP/raw`, then read with `while … done < file` | A pipe into `while` runs in a subshell; violation counters and `owner_of`'s globals would be discarded. This bug passes every happy-path test and silently reports `OK` on a violating PR |
| Quoted paths detected by a leading `"` | Git C-quotes any path containing non-ASCII or control bytes. Rejecting them is cheaper and safer than decoding them |
| Guard-critical list hard-coded in the script | Data files can be proposed for change by a pull request; this list cannot |
| `cfgfail` exits **2**, never 0 | A guard that cannot read its manifest must fail closed. §64's fail-closed control classification |
| Exceptions never apply to `GUARD-CRITICAL`, `PATH-ILLEGAL`, `SYMLINK-ADDED`, `SUBMODULE-ADDED` | An override for the guard's own files is an override of the override procedure |

---

## 7. The workflow — `contracts/ci/lane-guard.yml.frozen`, complete

This is the byte-exact content of both `contracts/ci/lane-guard.yml.frozen` (L0-owned, frozen) and
`.github/workflows/lane-guard.yml` (installed). They must be identical; the guard proves it on every PR.

**It uses no third-party GitHub Action at all.** §33.2 requires third-party actions to be pinned to a full commit
SHA with no exceptions; a workflow with zero third-party actions satisfies that rule with nothing to drift. The
checkout is done with `git` and the job's own `GITHUB_TOKEN`.

```yaml
# .github/workflows/lane-guard.yml
# FROZEN. The authoritative copy is contracts/ci/lane-guard.yml.frozen (L0-owned).
# This file is byte-compared against that contract on every pull request. Do not
# edit it: PARTITION.md rule 2, L0D-LG-2. Changes go through a Contract Change
# Request (docs/escalation/CCR.md).
#
# No third-party actions are used, so the SHA-pinning rule of MasterSpec v4.0
# §33.2 has nothing to pin. No `if:` and no path filter appear on this job,
# because a skipped required check counts as satisfied (§33.2).
name: lane-guard

on:
  pull_request:
    types: [opened, synchronize, reopened, ready_for_review]

permissions:
  contents: read

concurrency:
  group: lane-guard-${{ github.event.pull_request.number }}
  cancel-in-progress: true

jobs:
  lane-guard:
    name: lane-guard
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - name: Enforce the partition
        shell: bash
        env:
          GH_TOKEN:  ${{ github.token }}
          SERVER:    ${{ github.server_url }}
          BASE_REPO: ${{ github.repository }}
          HEAD_REPO: ${{ github.event.pull_request.head.repo.full_name }}
          BASE_REF:  ${{ github.event.pull_request.base.ref }}
          BASE_SHA:  ${{ github.event.pull_request.base.sha }}
          HEAD_REF:  ${{ github.event.pull_request.head.ref }}
          HEAD_SHA:  ${{ github.event.pull_request.head.sha }}
          PR_NUMBER: ${{ github.event.pull_request.number }}
        run: |
          set -euo pipefail

          die() {
            printf '%s\n' "$*"
            { printf '## lane-guard\n\n```\n%s\n```\n' "$*"; } >> "$GITHUB_STEP_SUMMARY"
            printf 'LANE-GUARD FAIL: configuration error\n'
            exit 2
          }

          # ---- 1. the branch must live in this repository ----------------------
          if [ "$HEAD_REPO" != "$BASE_REPO" ]; then
            die "LANE-GUARD REFUSED: head is $HEAD_REPO, not $BASE_REPO.
          Lane branches live in the control-plane repository. A fork pull request
          cannot be judged against the partition and is never merged.
          Authority: PARTITION.md, 'Branch & merge model'."
          fi

          # ---- 2. branch name -> lane number ------------------------------------
          case "$HEAD_REF" in
            lane/1/*)         LANE=1 ;;
            lane/2/*)         LANE=2 ;;
            lane/3/*)         LANE=3 ;;
            lane/4/*)         LANE=4 ;;
            lane/5/*)         LANE=5 ;;
            l0/*|integration|main) LANE=0 ;;
            *)
              die "LANE-GUARD REFUSED: branch '$HEAD_REF' names no lane.
          Every lane branch is named lane/<N>/<phase>-<task> with N in 1..5.
          Rename the branch and reopen the pull request.
          Authority: PARTITION.md, 'Branch & merge model'."
              ;;
          esac
          echo "lane=$LANE branch=$HEAD_REF base=$BASE_REF pr=$PR_NUMBER"

          # ---- 3. fetch both commits with plain git ----------------------------
          B64="$(printf 'x-access-token:%s' "$GH_TOKEN" | base64 | tr -d '\n')"
          echo "::add-mask::$B64"
          WORK="$RUNNER_TEMP/lane-guard"
          rm -rf "$WORK"; mkdir -p "$WORK/repo" "$WORK/rules"
          cd "$WORK/repo"
          git init -q .
          git remote add origin "$SERVER/$BASE_REPO"
          git -c http.extraheader="AUTHORIZATION: basic $B64" \
              fetch -q --no-tags origin "$BASE_SHA" "$HEAD_SHA" \
            || die "LANE-GUARD REFUSED: could not fetch $BASE_SHA and $HEAD_SHA."

          # ---- 4. the rules come from BASE, never from the pull request --------
          for f in lane-paths.tsv lane-owners.tsv lane-guard.sh lane-guard-exceptions.tsv; do
            if git cat-file -e "$BASE_SHA:$f" 2>/dev/null; then
              git show "$BASE_SHA:$f" > "$WORK/rules/$f"
            elif [ "$f" = "lane-guard-exceptions.tsv" ]; then
              : > "$WORK/rules/$f"
            else
              die "LANE-GUARD REFUSED: $f is missing at the base commit $BASE_SHA.
          The guard cannot prove the partition holds without it, so it fails closed."
            fi
          done
          chmod +x "$WORK/rules/lane-guard.sh"

          # ---- 5. the workflow at HEAD must equal the frozen contract at BASE ---
          git show "$BASE_SHA:contracts/ci/lane-guard.yml.frozen" > "$WORK/frozen.yml" \
            || die "LANE-GUARD REFUSED: contracts/ci/lane-guard.yml.frozen missing at base."
          git show "$HEAD_SHA:.github/workflows/lane-guard.yml" > "$WORK/head.yml" \
            || die "LANE-GUARD REFUSED: .github/workflows/lane-guard.yml missing at head."
          if ! cmp -s "$WORK/head.yml" "$WORK/frozen.yml"; then
            printf '::error file=.github/workflows/lane-guard.yml,title=lane-guard GUARD-TAMPER::This branch changes the lane guard workflow. It must be byte-identical to contracts/ci/lane-guard.yml.frozen. No override exists.\n'
            {
              printf '## lane-guard\n\n'
              printf '**GUARD-TAMPER** — `.github/workflows/lane-guard.yml` on this branch differs from the frozen contract `contracts/ci/lane-guard.yml.frozen`.\n\n'
              printf 'A lane that can edit the guard is not guarded (MasterSpec v4.0 §53.1).\n'
              printf 'No override exists for this class. File a Contract Change Request: `docs/escalation/CCR.md`.\n\n'
              printf '```diff\n'; diff -u "$WORK/frozen.yml" "$WORK/head.yml" | head -80; printf '```\n'
            } >> "$GITHUB_STEP_SUMMARY"
            printf 'LANE-GUARD FAIL: 1 violation(s)\n'
            exit 1
          fi

          # ---- 6. run the guard ------------------------------------------------
          set +e
          LG_MAP="$WORK/rules/lane-paths.tsv" \
          LG_OWNERS="$WORK/rules/lane-owners.tsv" \
          LG_EXC="$WORK/rules/lane-guard-exceptions.tsv" \
          LG_PR="$PR_NUMBER" \
          sh "$WORK/rules/lane-guard.sh" "$LANE" "$BASE_SHA" "$HEAD_SHA" > "$WORK/report.txt" 2>&1
          RC=$?
          set -e
          cat "$WORK/report.txt"

          {
            if [ "$RC" -eq 0 ]; then printf '## lane-guard — PASS\n\n'; else printf '## lane-guard — FAIL\n\n'; fi
            printf 'Branch `%s` is lane **%s**. Base `%s`.\n\n' "$HEAD_REF" "$LANE" "$BASE_REF"
            printf '```\n'; cat "$WORK/report.txt"; printf '```\n'
            if [ "$RC" -ne 0 ]; then
              printf '\n**Authority:** `docs/charter/PARTITION.md` rule 1 — one owner per path.\n'
              printf '**You may not fix this by editing the manifest.** See `docs/lane-guard.md`.\n'
            fi
          } >> "$GITHUB_STEP_SUMMARY"

          exit "$RC"
```

### 7.1 Why the fetch is done this way

| Step | Alternative that is wrong | Reason |
|---|---|---|
| `git init` + `fetch` two SHAs | `actions/checkout@vN` | A tag is not a pin (§33.2, §36.3). Using no action at all removes the pin problem instead of managing it |
| Rules read via `git show "$BASE_SHA:…"` | Reading the working tree after checkout of the merge ref | The merge ref contains the PR's edits. A PR that widens `lane-paths.tsv` would then be judged by its own widened rules |
| `::add-mask::$B64` before any use | Passing the token in the remote URL | A URL-embedded token appears in `git`'s own error output |
| `exit "$RC"` as the final statement | `continue-on-error` | The check must assert a real conclusion (§33.2) |

---

## 8. The error message an AI developer sees

The requirement is that it names **exactly which path was foreign and exactly which lane owns it**. Worked
example: branch `lane/1/p1-registry-schemas` has committed `reconciler/diff/engine.py`.

```
lane-guard v2 — lane 1 (L1 Registries & Contracts) — base 4f1c…  — head 9ab2…  — pr 118
manifest /home/runner/work/_temp/lane-guard/rules/lane-paths.tsv — 41 rules

LANE-GUARD VIOLATION [FOREIGN-PATH]
  path         : reconciler/diff/engine.py
  your lane    : 1  (L1 Registries & Contracts)
  owner lane   : 3  (L3 Reconciler & Provisioning)
  matched rule : lane-paths.tsv line 12  ->  3	reconciler/*
  reviewer     : @lane3-reviewer-login
  why          : PARTITION.md assigns this path to another lane, exclusively.
  fix          : remove this path from your branch. Lane 1 may not write it.
                   git checkout 4f1c… -- "reconciler/diff/engine.py"     # restore the base version
                   git rm --cached -- "reconciler/diff/engine.py"     # if you added it
  need it?     : you may NOT edit it yourself. File a Contract Change Request
                 (docs/escalation/CCR.md) or a blocker (docs/escalation/BLOCKER.md).
                 Override requires L0 and is described in docs/lane-guard.md.
  authority    : PARTITION.md rule 1 - one owner per path. No exceptions without L0.

LANE-GUARD SUMMARY
  FOREIGN-PATH     1
LANE-GUARD FAIL: 1 violation(s)
```

The same facts reach the developer three ways, so that a low-context agent cannot miss them:

| Surface | Content |
|---|---|
| Job log | The block above |
| Job summary (rendered on the PR checks tab) | The same block, fenced, plus the authority line |
| File annotation, inline in "Files changed" | `reconciler/diff/engine.py is owned by lane 3 (L3 Reconciler & Provisioning), not lane 1. PARTITION.md rule 1.` |

**The message deliberately never offers a self-service way out.** It names the reviewer of the owning lane and it
names the two escalation templates. It does not mention editing `lane-paths.tsv`, because a lane that edits the
manifest hits `GUARD-CRITICAL` on the next run and has wasted a cycle.

### 8.1 The message for the class with no override

```
LANE-GUARD VIOLATION [GUARD-CRITICAL]
  path         : .github/workflows/lane-guard.yml
  your lane    : 2  (L2 Pipeline & Evidence)
  owner lane   : 0  (L0 Integrator)
  why          : this file IS the lane guard. A lane that can edit the guard
                 is not guarded. MasterSpec v4.0 §53.1: no control that can be
                 rewritten by what it inspects is a control.
  fix          : git checkout 4f1c… -- ".github/workflows/lane-guard.yml"
  need it?     : NO OVERRIDE EXISTS for this class. File a Contract Change
                 Request (docs/escalation/CCR.md). Only L0 may change it.
  authority    : PARTITION.md rule 1 and rule 2; L0D-LG-2.
```

This is the message L2 sees, and L2 is the lane that *owns* `.github/workflows/**`. It is correct that it is the
sharpest message in the file.

---

## 9. The override procedure — L0 only, and structurally impossible to self-grant

**There is no commit trailer, no label, no environment variable and no `skip-checks` path.** The only override is
a row in `lane-guard-exceptions.tsv`, which:

1. is a **root file**, therefore L0-owned (`lane-paths.tsv` rule `0 *`), and is itself `GUARD-CRITICAL`, so a lane
   that adds a row to it fails on that row before the row can be honoured;
2. is read by the guard **from the base ref**, so a row that exists only on the lane's branch does not exist as
   far as the guard is concerned;
3. must name the **exact pull-request number**, so an override cannot be reused on the next PR;
4. must carry an **expiry**, because expiry is mandatory for every exception in this estate (§54.2:
   *"An exception with no expiry is not an exception; it is undocumented policy"*);
5. may **never** name a guard-critical path — the guard refuses the whole register with exit 2 if one does.

### 9.1 Register format

Nine columns is a schema nobody keeps; eight tab-separated fields is one a `while read` parses. The field set is
the mandatory subset of the §54.1 exception schema, so each row transcribes one-for-one into
`registries/exceptions.yaml` when L1 stands that registry up.

```
# lane-guard-exceptions.tsv — L0-owned root file. THE ONLY OVERRIDE PATH.
# id <TAB> lane <TAB> path <TAB> pr <TAB> expiry <TAB> owner <TAB> deactivation_trigger <TAB> reason
#
# Rules, enforced by lane-guard.sh (exit 2 if any is broken):
#   id      EXC-LG-NNN
#   lane    1..5
#   path    ONE literal path. No globs. Never a guard-critical path.
#   pr      the exact pull-request number this row unblocks. One PR, one row.
#   expiry  YYYY-MM-DD, mandatory (MasterSpec v4.0 §54.2). Inclusive.
#   owner   @github-login of the L0 human accountable for the compensating control.
#   deactivation_trigger  mandatory; the event that closes this row.
#   reason  one line, no tabs.
#
# Adding a row is an L0 act performed on `integration` directly. It is never
# merged from a lane branch: PARTITION.md rule 1 makes that impossible.
```

### 9.2 The procedure

| Step | Who | Action |
|---|---|---|
| 1 | Lane | Hits the guard. **Stops.** Opens a blocker using `docs/escalation/BLOCKER.md`, titled `BLOCKER lane-guard: <lane> needs <path>`, naming the task id, the exact path and the exact violation class |
| 2 | L0 | Decides which of four things is true: (a) the path belongs to the lane and the *manifest* is wrong; (b) the work belongs to the owning lane and should be re-tasked; (c) it needs a contract change; (d) it genuinely needs a one-PR override |
| 3a | L0 | (a) → amend `lane-paths.tsv` on `integration`, re-run `lane-guard-selftest.sh`, regenerate `CODEOWNERS` (`make codeowners`). **This is a partition amendment and is recorded as a decision** |
| 3b | L0 | (b) → close the blocker, re-task to the owning lane. No override |
| 3c | L0 | (c) → Contract Change Request path, charter §7.2. No override |
| 3d | L0 | (d) → append one row to `lane-guard-exceptions.tsv` on `integration`, push, and comment the `EXC-LG-NNN` id on the blocker |
| 4 | Lane | Rebases on `integration`, pushes. The guard now prints `LANE-GUARD OVERRIDE: …` and passes |
| 5 | L0 | Writes the decision record under `records/decisions/` per §97.2, and removes the row once the deactivation trigger fires |

**Guard-critical paths have no step 3d.** There is no override; the answer is always 3a or 3c.

### 9.3 What an override looks like in the log

```
LANE-GUARD OVERRIDE: infra/runners/lane4-fixture.tf permitted for lane 4 by EXC-LG-001 (expires 2026-09-10, owner @lead-login, pr 233)

LANE-GUARD: 1 override(s) applied under L0 authority. Each expires; see lane-guard-exceptions.tsv.
LANE-GUARD OK
```

An expired row does not warn — it simply stops matching, and the path reverts to `FOREIGN-PATH`. That is the
§54.2 rule *"the exception becomes Blocking-class drift on its expiry date"* expressed in the cheapest possible way.

---

## 10. CODEOWNERS generation

CODEOWNERS is **generated from the same manifest the guard reads**, so review routing and merge blocking can
never disagree. §11.3 requires exactly this: *"CODEOWNERS … is generated from the registries rather than
hand-maintained; the generator emits human identities only."*

> **Scope note.** This is the *build-time partition* CODEOWNERS for the `control-plane` repository. It is a
> different artifact from the *per-product* CODEOWNERS that `create-product` generates from `product.yaml`
> assignments (§11.3, §53.1 row `product.yaml assignments → CODEOWNERS`), which L3 builds. Neither generator
> touches the other's file.

`codeowners-gen.sh`, L0-owned root file, authored by task **L0-02-05**:

```sh
#!/usr/bin/env sh
# =============================================================================
# codeowners-gen.sh — L0-owned root file.
# Generates CODEOWNERS from lane-paths.tsv + lane-owners.tsv so that review
# routing mirrors the partition exactly. Never hand-edit CODEOWNERS.
#
# CODEOWNERS semantics: LAST matching rule wins. Emission order is therefore
#   1. the default owner        (least specific)
#   2. lane trees 1..5
#   3. L0 trees
#   4. guard-critical files     (most specific — these must win)
#
# HUMAN IDENTITIES ONLY. A machine account here would let a machine approval
# satisfy branch protection (MasterSpec v4.0 §11.3, §98.2 Phase 1, D53).
# =============================================================================
set -eu
TAB=$(printf '\t')
SELF_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
MAP="$SELF_DIR/lane-paths.tsv"
OWN="$SELF_DIR/lane-owners.tsv"
OUT="${1:-$SELF_DIR/CODEOWNERS}"

[ -f "$MAP" ] || { echo "CODEOWNERS-GEN FAIL: lane-paths.tsv missing"; exit 2; }
[ -f "$OWN" ] || { echo "CODEOWNERS-GEN FAIL: lane-owners.tsv missing"; exit 2; }

CRITICAL="CODEOWNERS Makefile contracts.sha256 lane-paths.tsv lane-owners.tsv
lane-guard.sh lane-guard-exceptions.tsv lane-guard-selftest.sh codeowners-gen.sh
lane-guard-ruleset.json .github/workflows/lane-guard.yml
contracts/ci/lane-guard.yml.frozen contracts/ci/lane-guard.contract.md"

login_of() {
  _l="$1"; _r=""
  while IFS="$TAB" read -r _ln _login _disp; do
    case "$_ln" in ''|\#*) continue ;; esac
    if [ "$_ln" = "$_l" ]; then _r="$_login"; break; fi
  done < "$OWN"
  [ -n "$_r" ] || { echo "CODEOWNERS-GEN FAIL: no owner declared for lane $_l in lane-owners.tsv" >&2; exit 2; }
  printf '%s' "$_r"
}

# reject machine identities in the owners table before emitting anything
if grep -Eiq '(\[bot\]|-bot|_bot|\bbot\b|renovate|dependabot|github-actions|records-writer|reconciler-bot|-app$)' "$OWN"; then
  echo "CODEOWNERS-GEN FAIL: lane-owners.tsv names an identity that looks like a machine account."
  echo "CODEOWNERS carries human identities only (MasterSpec v4.0 §11.3, §98.2 Phase 1, D53)."
  exit 2
fi

L0OWNER=$(login_of 0)

{
  printf '# CODEOWNERS — GENERATED by codeowners-gen.sh. DO NOT HAND-EDIT.\n'
  printf '# Source of truth: lane-paths.tsv + lane-owners.tsv. Regenerate with `make codeowners`.\n'
  printf '# Human identities only: a machine-account approval must never satisfy branch\n'
  printf '# protection (MasterSpec v4.0 §11.3; §98.2 Phase 1 completion check; D53).\n'
  printf '# Last matching rule wins, so the guard-critical block at the bottom is final.\n'
  printf '\n'
  printf '# --- default owner ---\n'
  printf '*%s%s\n' "$TAB" "$L0OWNER"
  printf '\n'
  printf '# --- lane-owned trees (PARTITION.md, FROZEN) ---\n'
  while IFS="$TAB" read -r lane pat; do
    case "$lane" in ''|\#*) continue ;; esac
    case "$lane" in 1|2|3|4|5) : ;; *) continue ;; esac
    dir="/${pat%\*}"
    printf '%s%s%s\n' "$dir" "$TAB" "$(login_of "$lane")"
  done < "$MAP"
  printf '\n'
  printf '# --- L0-owned trees ---\n'
  while IFS="$TAB" read -r lane pat; do
    case "$lane" in ''|\#*) continue ;; esac
    [ "$lane" = "0" ] || continue
    [ "$pat" = "*" ] && continue
    dir="/${pat%\*}"
    printf '%s%s%s\n' "$dir" "$TAB" "$L0OWNER"
  done < "$MAP"
  printf '\n'
  printf '# --- guard-critical: the lane guard itself. L0 only, no override exists. ---\n'
  for c in $CRITICAL; do
    printf '/%s%s%s\n' "$c" "$TAB" "$L0OWNER"
  done
} > "$OUT"

printf 'CODEOWNERS-GEN OK %s rules\n' "$(grep -vc '^#\|^$' "$OUT")"
```

### 10.1 The mirror property, stated precisely

For every rule `N<TAB>tree/*` in `lane-paths.tsv` with `N` in `1..5`, `CODEOWNERS` contains exactly one line
`/tree/<TAB>@lane-N-reviewer`. Task **L0-02-05**'s acceptance criterion 3 proves this by comparing the two
derived sets and requiring an empty symmetric difference. If a lane tree is ever added to the manifest and
CODEOWNERS is not regenerated, that comparison fails.

---

## 11. Lane-guard decision register

Plan-local ids. They do not collide with the charter's `L0D-01 … L0D-26`, nor with Appendix A's `D1 … D112`.

| Plan id | Decision | Rationale | Anchor |
|---|---|---|---|
| **L0D-LG-1** | The lane-guard workflow's content is an L0 contract at `contracts/ci/lane-guard.yml.frozen` | `contracts/**` is L0-owned and frozen; this is the only L0-owned place a workflow body can live | PARTITION.md rule 2 |
| **L0D-LG-2** | `.github/workflows/lane-guard.yml` stays L2-owned by path but is byte-frozen; the guard classifies it `GUARD-CRITICAL` | Preserves the frozen partition unamended while closing the self-reference hole | §53.1; §33.2 (D89) |
| **L0D-LG-3** | L0 places the workflow once, on `integration`, in Phase 0, before any lane branch exists | The §95.2 bootstrap-arming pattern: configure before the constrained party exists | §95.2 |
| **L0D-LG-4** | The workflow uses **zero** third-party actions | §33.2 forbids unpinned actions; zero actions removes the class of problem rather than managing it | §33.2 |
| **L0D-LG-5** | L0-00-01 acceptance criterion 4 (`grep -ci 'bot\|\[bot\]\|records-writer\|reconciler' CODEOWNERS` must be `0`) is **replaced** by an owner-column-only check | The v1 criterion greps whole lines, and a correct CODEOWNERS contains the path `/reconciler/`, so the v1 check can never pass on a correct file. The rule it was protecting — no machine identity may be an owner — is preserved, and now tested where it lives: the owner column | §11.3; §98.2 Phase 1 |
| **L0D-LG-6** | `control-plane-records` gets no lane guard | One lane owns the whole repository, so there is no partition to enforce there. Its controls are the D107 no-bypass ruleset and D89's separate-repository scoping | §12 below; D89, D107 |

---

## 12. The `control-plane-records` repository

PARTITION.md gives L4 **all** of `control-plane-records`. A path-ownership guard there would have exactly one
rule — "lane 4 owns everything" — and would be theatre. The controls that repository actually needs are settings,
not files, and settings are not paths, so L0 configures them without writing into L4's tree:

| Control | Mechanism | Anchor |
|---|---|---|
| Rewriting blocked, appending allowed | A ruleset with **no bypass actor** blocking force-push and deletion | D107 |
| The records-writer credential is scoped to this repository alone | A GitHub App token scoped to `control-plane-records`; **no machine identity is a bypass actor on `control-plane`** | D89 |
| Head-SHA anchoring | The reconciler anchors the records head SHA into the protected `control-plane` repository each run; a head that does not descend from the last anchor is proof of rewriting, at Level 5 | D107, §53.2 |

Task **L0-02-08** verifies the `control-plane` ruleset's bypass list is empty. Verifying the records-repository
ruleset belongs to L5's access work and is not duplicated here.

---

## 13. L0-02 TASKS

Nine tasks. Executor: the human lead. All paths exact; all commands literal; `$CP_ROOT` is set as in
`L0-00-charter.md` §1.

---

### L0-02-01 — Author `lane-owners.tsv`

**Size:** S · **Dependencies:** `L0-00-03`

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
git checkout integration && git pull --ff-only

printf '%s\n' \
'# lane-owners.tsv — L0-owned. lane <TAB> @github-login <TAB> display name.' \
'# HUMAN IDENTITIES ONLY. A machine account here would let a machine approval' \
'# satisfy branch protection; the Phase 1 completion check tests this' \
'# negatively (MasterSpec v4.0 §98.2; §11.3; D53).' > lane-owners.tsv
printf '0\t@REPLACE_LEAD\tL0 Integrator\n'                  >> lane-owners.tsv
printf '1\t@REPLACE_L1\tL1 Registries & Contracts\n'        >> lane-owners.tsv
printf '2\t@REPLACE_L2\tL2 Pipeline & Evidence\n'           >> lane-owners.tsv
printf '3\t@REPLACE_L3\tL3 Reconciler & Provisioning\n'     >> lane-owners.tsv
printf '4\t@REPLACE_L4\tL4 Records, Events & Metrics\n'     >> lane-owners.tsv
printf '5\t@REPLACE_L5\tL5 Access, Infra & Ops\n'           >> lane-owners.tsv
```

Now replace every `@REPLACE_*` with a real GitHub login of a human who holds Write. During the solo build all six
may be the same login; that is the recorded state of `EXC-BOOT-001` (§95.2) and is not a defect.

**Commands**

```bash
git add lane-owners.tsv
git commit -m "L0-02-01: lane owners table (human identities only)"
git push origin integration
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | File exists | `test -f lane-owners.tsv && echo PRESENT` | `PRESENT` |
| 2 | Exactly 6 rows, comments excluded | `grep -vc '^#' lane-owners.tsv` | `6` |
| 3 | Every row has exactly 3 tab-separated fields | `awk -F'\t' '!/^#/ && NF!=3' lane-owners.tsv \| wc -l` | `0` |
| 4 | Lanes 0–5 each appear once | `awk -F'\t' '!/^#/{print $1}' lane-owners.tsv \| sort \| tr -d '\n'` | `012345` |
| 5 | No placeholder remains | `grep -c 'REPLACE_' lane-owners.tsv` | `0` |
| 6 | No machine identity | `grep -Eci '(\[bot\]|-bot|_bot|renovate|dependabot|github-actions|records-writer)' lane-owners.tsv` | `0` |
| 7 | Every login starts with `@` | `awk -F'\t' '!/^#/ && $2 !~ /^@/' lane-owners.tsv \| wc -l` | `0` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP_ROOT"
printf 'rows=%s fields=%s lanes=%s placeholders=%s machines=%s at=%s\n' \
  "$(grep -vc '^#' lane-owners.tsv)" \
  "$(awk -F'\t' '!/^#/ && NF!=3' lane-owners.tsv | wc -l | tr -d ' ')" \
  "$(awk -F'\t' '!/^#/{print $1}' lane-owners.tsv | sort | tr -d '\n')" \
  "$(grep -c 'REPLACE_' lane-owners.tsv)" \
  "$(grep -Eci '(\[bot\]|-bot|_bot|renovate|dependabot|github-actions|records-writer)' lane-owners.tsv)" \
  "$(awk -F'\t' '!/^#/ && $2 !~ /^@/' lane-owners.tsv | wc -l | tr -d ' ')"
```

Expected output, exactly:

```
rows=6 fields=0 lanes=012345 placeholders=0 machines=0 at=0
```

**STOP rule** — if `machines` is non-zero, do not proceed and do not "temporarily" leave the entry in. A machine
identity in CODEOWNERS defeats the Phase 1 completion check that an approval from a machine account does not
satisfy branch protection (§98.2). Open `BLOCKER L0-02-01: machine identity in lane-owners.tsv`.

---

### L0-02-02 — Install `lane-guard.sh` v2

**Size:** L · **Dependencies:** `L0-00-04`, `L0-02-01`

Replace the whole of `lane-guard.sh` with the script printed in **§6** of this document, byte for byte. Do not
retype it; copy it.

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
# 1. paste the §6 script into lane-guard.sh, then:
chmod +x lane-guard.sh
sh -n lane-guard.sh && echo SYNTAX-OK
# Commit v2 to integration BEFORE the compatibility probe so that the working
# tree is clean when we enter the temp branch. If the commit happens after
# git checkout integration the old v1 is restored and "nothing to commit".
git add lane-guard.sh
git commit -m "L0-02-02: lane-guard.sh v2 (modes, renames, exceptions, annotations)"

# 2. prove the v1 contract survives — L0-00-04's own self-test, unchanged
git checkout -b tmp/lg-v2-compat integration
mkdir -p registries && echo "a: 1" > registries/probe.yaml
git add registries/probe.yaml && git commit -q -m "probe A"
A=$(sh ./lane-guard.sh 1 integration HEAD | tail -1)
# probe B needs two foreign-path files to produce the expected 2 violations:
# reconciler/* is L3-owned and metrics/* is L4-owned, both foreign for L1.
# (lane-guard.sh is no longer in the diff since v2 was committed to integration
# before this branch was cut, so it cannot substitute for a second violation.)
mkdir -p reconciler metrics && echo "b" > reconciler/probe.txt && echo "c" > metrics/probe.txt
git add reconciler/probe.txt metrics/probe.txt && git commit -q -m "probe B"
B=$(sh ./lane-guard.sh 1 integration HEAD | tail -1)
printf 'A=[%s] B=[%s]\n' "$A" "$B"
git checkout integration && git branch -D tmp/lg-v2-compat

git push origin integration
```

Step 2 must print `A=[LANE-GUARD OK] B=[LANE-GUARD FAIL: 2 violation(s)]` — L0-00-04's documented output,
unchanged by v2.

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Parses as POSIX sh | `sh -n lane-guard.sh && echo SYNTAX-OK` | `SYNTAX-OK` |
| 2 | Executable | `test -x lane-guard.sh && echo EXEC` | `EXEC` |
| 3 | v1 terminal strings preserved | `grep -c 'LANE-GUARD OK' lane-guard.sh; grep -c 'LANE-GUARD FAIL: %s violation(s)' lane-guard.sh` | `2` and `1` |
| 4 | No bashisms | `grep -Ec '\[\[|PIPESTATUS|<<<|\$\(\(.*\+\+\)\)|declare |local ' lane-guard.sh` | `0` |
| 5 | Missing manifest fails closed with rc 2 | `LG_MAP=/nonexistent sh ./lane-guard.sh 1 integration HEAD; echo "rc=$?"` | `rc=2` |
| 6 | Bad lane argument fails closed | `sh ./lane-guard.sh 9 integration HEAD; echo "rc=$?"` | `rc=2` |
| 7 | Guard-critical list has 13 entries | `grep -A3 '^CRITICAL=' lane-guard.sh \| sed 's/^CRITICAL="//' \| tr ' ' '\n' \| grep -c .` | `13` |
| 8 | v1 compatibility probe passes | step 2 above | `A=[LANE-GUARD OK] B=[LANE-GUARD FAIL: 2 violation(s)]` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP_ROOT"
LG_MAP=/nonexistent sh ./lane-guard.sh 1 integration HEAD >/dev/null 2>&1; rc_map=$?
sh ./lane-guard.sh 9 integration HEAD >/dev/null 2>&1; rc_lane=$?
printf 'syntax=%s exec=%s bashisms=%s rc_map=%s rc_lane=%s ok_str=%s fail_str=%s\n' \
  "$(sh -n lane-guard.sh >/dev/null 2>&1 && echo OK || echo BAD)" \
  "$(test -x lane-guard.sh && echo EXEC || echo NOEXEC)" \
  "$(grep -Ec '\[\[|PIPESTATUS|<<<|declare |local ' lane-guard.sh)" \
  "$rc_map" "$rc_lane" \
  "$(grep -c 'LANE-GUARD OK' lane-guard.sh)" \
  "$(grep -c "LANE-GUARD FAIL: %s violation" lane-guard.sh)"
```

Expected output, exactly:

```
syntax=OK exec=EXEC bashisms=0 rc_map=2 rc_lane=2 ok_str=2 fail_str=1
```

**STOP rule** — if `rc_map` is `0`, the guard passes when it cannot read the partition. That is a guard that
reports green while enforcing nothing, which is the precise failure §53.1 warns about. Do not proceed, do not
create any lane branch, and open `BLOCKER L0-02-02: guard does not fail closed`.

---

### L0-02-03 — Create the override register

**Size:** S · **Dependencies:** `L0-02-02`

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
cat > lane-guard-exceptions.tsv <<'EOF'
# lane-guard-exceptions.tsv — L0-owned root file. THE ONLY OVERRIDE PATH.
# id <TAB> lane <TAB> path <TAB> pr <TAB> expiry <TAB> owner <TAB> deactivation_trigger <TAB> reason
#
# Rules, enforced by lane-guard.sh (exit 2 if any is broken):
#   id      EXC-LG-NNN
#   lane    1..5
#   path    ONE literal path. No globs. Never a guard-critical path.
#   pr      the exact pull-request number this row unblocks. One PR, one row.
#   expiry  YYYY-MM-DD, mandatory (MasterSpec v4.0 §54.2). Inclusive.
#   owner   @github-login of the L0 human accountable for the compensating control.
#   deactivation_trigger  mandatory; the event that closes this row.
#   reason  one line, no tabs.
#
# Adding a row is an L0 act performed on `integration` directly. It is never
# merged from a lane branch: PARTITION.md rule 1 makes that impossible.
#
# The register starts empty. It should usually be empty.
EOF

git add lane-guard-exceptions.tsv
git commit -m "L0-02-03: lane-guard override register (empty)"
git push origin integration
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | File exists | `test -f lane-guard-exceptions.tsv && echo PRESENT` | `PRESENT` |
| 2 | Register is empty | `grep -vc '^#\|^$' lane-guard-exceptions.tsv` | `0` |
| 3 | Guard accepts an empty register | `sh ./lane-guard.sh 0 integration HEAD >/dev/null; echo "rc=$?"` | `rc=0` |
| 4 | Guard rejects a malformed row (rc 2) | see SELF-VERIFY | `rc=2` |
| 5 | Guard rejects a row with no expiry (rc 2) | see SELF-VERIFY | `rc=2` |
| 6 | Guard rejects a row naming a guard-critical path (rc 2) | see SELF-VERIFY | `rc=2` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP_ROOT"
T=$(mktemp -d)
cp lane-guard-exceptions.tsv "$T/clean.tsv"

printf 'EXC-LG-001\t1\tsome/path\n' > "$T/short.tsv"
LG_EXC="$T/short.tsv" sh ./lane-guard.sh 1 integration HEAD >/dev/null 2>&1; rc_short=$?

printf 'EXC-LG-001\t1\tsome/path\t42\t\t@lead\ttrigger\treason\n' > "$T/noexp.tsv"
LG_EXC="$T/noexp.tsv" sh ./lane-guard.sh 1 integration HEAD >/dev/null 2>&1; rc_noexp=$?

printf 'EXC-LG-001\t1\tCODEOWNERS\t42\t2099-01-01\t@lead\ttrigger\treason\n' > "$T/crit.tsv"
LG_EXC="$T/crit.tsv" sh ./lane-guard.sh 1 integration HEAD >/dev/null 2>&1; rc_crit=$?

printf 'EXC-LG-001\t1\tregistries/*\t42\t2099-01-01\t@lead\ttrigger\treason\n' > "$T/glob.tsv"
LG_EXC="$T/glob.tsv" sh ./lane-guard.sh 1 integration HEAD >/dev/null 2>&1; rc_glob=$?

LG_EXC="$T/clean.tsv" sh ./lane-guard.sh 0 integration HEAD >/dev/null 2>&1; rc_clean=$?
rm -rf "$T"
printf 'clean=%s short=%s noexpiry=%s critical=%s glob=%s\n' "$rc_clean" "$rc_short" "$rc_noexp" "$rc_crit" "$rc_glob"
```

Expected output, exactly:

```
clean=0 short=2 noexpiry=2 critical=2 glob=2
```

**STOP rule** — if `critical` is not `2`, an override can be written for the guard's own files, which makes the
override procedure self-amending. Do not proceed. Open `BLOCKER L0-02-03: override register accepts a
guard-critical path`.

---

### L0-02-04 — Author and run the adversarial self-test

**Size:** L · **Dependencies:** `L0-02-02`, `L0-02-03`

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
cat > lane-guard-selftest.sh <<'SELFTEST'
#!/usr/bin/env sh
# lane-guard-selftest.sh — L0-owned root file.
# Adversarial proof that the guard FAILS what it must fail. Builds throwaway
# repositories under a temp dir; touches nothing real. Exits non-zero on any
# case that does not behave exactly as specified.
set -eu
SELF_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
WORK=$(mktemp -d 2>/dev/null || mktemp -d -t lgst)
trap 'rm -rf "$WORK"' EXIT
PASS=0; TOTAL=0

setup() {
  R="$WORK/$1"; mkdir -p "$R"; cd "$R"
  git init -q .
  git config user.email lane-guard@example.invalid
  git config user.name  lane-guard-selftest
  cp "$SELF_DIR/lane-paths.tsv" "$SELF_DIR/lane-owners.tsv" \
     "$SELF_DIR/lane-guard.sh"  "$SELF_DIR/lane-guard-exceptions.tsv" .
  chmod +x lane-guard.sh
  mkdir -p registries reconciler contracts contracts/ci .github/workflows
  echo base > registries/base.yaml
  echo base > reconciler/base.py
  echo base > contracts/base.md
  echo base > contracts/ci/lane-guard.yml.frozen
  echo base > .github/workflows/lane-guard.yml
  echo base > CODEOWNERS
  git add -A >/dev/null; git commit -q -m base
  git branch -f base HEAD
}

expect() {  # expect <num> <label> <lane> <want-rc> <want-grep> [pr]
  TOTAL=$((TOTAL + 1))
  _pr="${6:-none}"
  out=$(LG_PR="$_pr" sh ./lane-guard.sh "$3" base HEAD 2>&1) && rc=0 || rc=$?
  if [ "$rc" = "$4" ] && printf '%s' "$out" | grep -q "$5"; then
    printf 'CASE %s %-32s PASS\n' "$1" "$2"; PASS=$((PASS + 1))
  else
    printf 'CASE %s %-32s FAIL (rc=%s, wanted %s + /%s/)\n' "$1" "$2" "$rc" "$4" "$5"
    printf '%s\n' "$out" | sed 's/^/      /'
  fi
}

setup c01; echo more >> registries/base.yaml; git add -A >/dev/null; git commit -q -m c01
expect 01 same-lane-edit 1 0 'LANE-GUARD OK'

setup c02; echo more >> reconciler/base.py; git add -A >/dev/null; git commit -q -m c02
expect 02 foreign-path-named-owner 1 1 'owner lane   : 3'

setup c03; mkdir -p telemetry/agents; echo x > telemetry/agents/a.yaml
git add -A >/dev/null; git commit -q -m c03
expect 03 unassigned-tree 1 1 'UNASSIGNED-PATH'

setup c04; echo tampered > .github/workflows/lane-guard.yml
git add -A >/dev/null; git commit -q -m c04
expect 04 l2-edits-the-guard 2 1 'GUARD-CRITICAL'

setup c05; echo tampered > CODEOWNERS; git add -A >/dev/null; git commit -q -m c05
expect 05 lane-edits-codeowners 1 1 'GUARD-CRITICAL'

setup c06; echo more >> contracts/base.md; git add -A >/dev/null; git commit -q -m c06
expect 06 contracts-are-l0 1 1 'owner lane   : 0'

setup c07; git mv reconciler/base.py registries/moved.py; git commit -q -m c07
expect 07 rename-out-of-foreign-tree 1 1 'reconciler/base.py'

setup c08; echo x > "registries/a b.yaml"; git add -A >/dev/null; git commit -q -m c08
expect 08 illegal-path-with-space 1 1 'PATH-ILLEGAL'

setup c09
sha=$(printf 'reconciler/base.py' | git hash-object -w --stdin)
git update-index --add --cacheinfo 120000,"$sha",registries/link >/dev/null
git commit -q -m c09
expect 09 symlink-into-foreign-tree 1 1 'SYMLINK-ADDED'

setup c10; git rm -q reconciler/base.py; git commit -q -m c10
expect 10 delete-foreign-file 1 1 'owner lane   : 3'

setup c11; echo more >> reconciler/base.py; git add -A >/dev/null; git commit -q -m c11
printf 'EXC-LG-001\t1\treconciler/base.py\t42\t2099-12-31\t@lead\tlane 3 ships the real file\tselftest\n' \
  >> lane-guard-exceptions.tsv
expect 11 valid-override-honoured 1 0 'LANE-GUARD OVERRIDE' 42

setup c12; echo more >> reconciler/base.py; git add -A >/dev/null; git commit -q -m c12
printf 'EXC-LG-001\t1\treconciler/base.py\t42\t2000-01-01\t@lead\tlane 3 ships the real file\tselftest\n' \
  >> lane-guard-exceptions.tsv
expect 12 expired-override-refused 1 1 'FOREIGN-PATH' 42

setup c13; echo more >> reconciler/base.py; git add -A >/dev/null; git commit -q -m c13
printf 'EXC-LG-001\t1\treconciler/base.py\t42\t2099-12-31\t@lead\tlane 3 ships the real file\tselftest\n' \
  >> lane-guard-exceptions.tsv
expect 13 override-wrong-pr-refused 1 1 'FOREIGN-PATH' 43

setup c14; echo more >> registries/base.yaml; git add -A >/dev/null; git commit -q -m c14
printf 'EXC-LG-002\t1\tCODEOWNERS\t42\t2099-12-31\t@lead\tnever\tselftest\n' \
  >> lane-guard-exceptions.tsv
expect 14 override-refused-on-critical 1 2 'can never be excepted' 42

printf '\nSELFTEST %s/%s ' "$PASS" "$TOTAL"
if [ "$PASS" -eq "$TOTAL" ]; then printf 'PASS\n'; exit 0; fi
printf 'FAIL\n'; exit 1
SELFTEST
chmod +x lane-guard-selftest.sh
sh ./lane-guard-selftest.sh

git add lane-guard-selftest.sh
git commit -m "L0-02-04: adversarial lane-guard self-test, 14 cases"
git push origin integration
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Script parses | `sh -n lane-guard-selftest.sh && echo SYNTAX-OK` | `SYNTAX-OK` |
| 2 | All 14 cases pass | `sh ./lane-guard-selftest.sh \| tail -1` | `SELFTEST 14/14 PASS` |
| 3 | Exit code is 0 | `sh ./lane-guard-selftest.sh >/dev/null; echo "rc=$?"` | `rc=0` |
| 4 | The self-test wrote nothing into the repository | `git status --porcelain \| wc -l` | `0` after the commit |
| 5 | Every case is asserted, none skipped | `grep -c '^expect ' lane-guard-selftest.sh` | `14` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP_ROOT"
sh ./lane-guard-selftest.sh > /tmp/lgst.out 2>&1; rc=$?
printf 'rc=%s tail=%s cases=%s dirty=%s\n' \
  "$rc" "$(tail -1 /tmp/lgst.out)" \
  "$(grep -c '^expect ' lane-guard-selftest.sh)" \
  "$(git status --porcelain | wc -l | tr -d ' ')"
```

Expected output, exactly:

```
rc=0 tail=SELFTEST 14/14 PASS cases=14 dirty=0
```

**STOP rule** — if any case fails, **no lane branch may be created**. Do not edit the expected values to make the
run green; that converts a real finding into a permanent blind spot. Read the failing case's output, fix
`lane-guard.sh`, re-run. If the case that fails is 04, 05 or 14, treat it as urgent: those are the cases that keep
a lane from editing the guard. Open `BLOCKER L0-02-04: lane guard self-test case NN fails`.

---

### L0-02-05 — Generate `CODEOWNERS` from the manifest

**Size:** M · **Dependencies:** `L0-02-01`, `L0-00-01`

Paste the script printed in **§10** into `codeowners-gen.sh`, then:

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
chmod +x codeowners-gen.sh
sh -n codeowners-gen.sh && echo SYNTAX-OK
sh ./codeowners-gen.sh
cat CODEOWNERS

git add codeowners-gen.sh CODEOWNERS
git commit -m "L0-02-05: generate CODEOWNERS from lane-paths.tsv (L0D-LG-5)"
git push origin integration
```

This **supersedes the hand-written `CODEOWNERS` of L0-00-01**. All of L0-00-01's acceptance criteria still hold
except criterion 4, replaced per **L0D-LG-5**: the machine-identity test now inspects the owner column, because a
correct CODEOWNERS contains the path `/reconciler/` and a whole-line grep for `reconciler` can never return `0`.

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Generator runs clean | `sh ./codeowners-gen.sh \| tail -1` | `CODEOWNERS-GEN OK 34 rules` |
| 2 | CODEOWNERS is generated, not hand-edited | `head -1 CODEOWNERS` | `# CODEOWNERS — GENERATED by codeowners-gen.sh. DO NOT HAND-EDIT.` |
| 3 | Mirrors the manifest exactly (symmetric difference empty) | see SELF-VERIFY | `mirror=0` |
| 4 | No machine identity in the **owner column** (replaces L0-00-01 #4) | `awk '!/^#/ && NF>1 {for(i=2;i<=NF;i++) print $i}' CODEOWNERS \| grep -Eci '(\[bot\]|-bot|_bot|renovate|dependabot|github-actions|records-writer)'` | `0` |
| 5 | Every owner token starts with `@` | `awk '!/^#/ && NF>1 {for(i=2;i<=NF;i++) if ($i !~ /^@/) print}' CODEOWNERS \| wc -l` | `0` |
| 6 | No `CODEOWNERS` under `.github/` | `test ! -f .github/CODEOWNERS && echo CLEAN` | `CLEAN` |
| 7 | Guard-critical block is last and owned by lane 0 | `tail -13 CODEOWNERS \| awk '{print $2}' \| sort -u \| wc -l` | `1` |
| 8 | Regeneration is idempotent | `sh ./codeowners-gen.sh >/dev/null; git diff --quiet CODEOWNERS && echo STABLE` | `STABLE` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP_ROOT"
awk -F'\t' '!/^#/ && ($1>=1 && $1<=5) {p=$2; sub(/\*$/,"",p); print "/"p}' lane-paths.tsv \
  | LC_ALL=C sort > /tmp/lg-map.txt
awk '!/^#/ && NF>1 && $1 ~ /\/$/ {print $1}' CODEOWNERS | LC_ALL=C sort -u > /tmp/lg-co.txt
mirror=$(comm -3 /tmp/lg-map.txt <(grep -v '^/contracts/$\|^/docs/$' /tmp/lg-co.txt) | wc -l | tr -d ' ')
printf 'gen=%s mirror=%s machines=%s at=%s dotgithub=%s stable=%s\n' \
  "$(sh ./codeowners-gen.sh | tail -1)" \
  "$mirror" \
  "$(awk '!/^#/ && NF>1 {for(i=2;i<=NF;i++) print $i}' CODEOWNERS | grep -Eci '(\[bot\]|-bot|_bot|renovate|dependabot|github-actions|records-writer)')" \
  "$(awk '!/^#/ && NF>1 {for(i=2;i<=NF;i++) if ($i !~ /^@/) print}' CODEOWNERS | wc -l | tr -d ' ')" \
  "$(test ! -f .github/CODEOWNERS && echo CLEAN || echo DIRTY)" \
  "$(git diff --quiet CODEOWNERS && echo STABLE || echo DRIFTED)"
```

Expected output, exactly:

```
gen=CODEOWNERS-GEN OK 34 rules mirror=0 machines=0 at=0 dotgithub=CLEAN stable=STABLE
```

(34 = 1 default + 18 lane trees + 2 L0 trees + 13 guard-critical files. The SELF-VERIFY uses `bash`'s process
substitution; run it under `bash`, as `make` does.)

**STOP rule** — if `mirror` is non-zero, CODEOWNERS and the guard disagree about who owns something, which means
review routing and merge blocking disagree. Do not hand-patch `CODEOWNERS` to close the gap: fix
`lane-owners.tsv` or `codeowners-gen.sh` and regenerate. Open `BLOCKER L0-02-05: CODEOWNERS does not mirror the
partition`.

---

### L0-02-06 — Freeze the workflow as a contract

**Size:** M · **Dependencies:** `L0-02-02`, `L0-02-03`

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
mkdir -p contracts/ci
# Paste the §7 YAML into contracts/ci/lane-guard.yml.frozen, byte for byte.

cat > contracts/ci/lane-guard.contract.md <<'EOF'
# Contract: the lane-guard workflow

**Owner:** L0. **Frozen** from Phase 0 (PARTITION.md rule 2).

`.github/workflows/lane-guard.yml` in this repository MUST be byte-identical to
`contracts/ci/lane-guard.yml.frozen`. The check named `lane-guard` compares them on
every pull request and fails with class `GUARD-TAMPER` if they differ.

The path `.github/workflows/**` belongs to L2 (PARTITION.md). L2 owns the directory
and does not own this file's bytes (L0D-LG-2). L2 changes it only through a Contract
Change Request: `docs/escalation/CCR.md`.

Rules this contract carries, and their spec anchors:

| Rule | Anchor |
|---|---|
| The job carries no `if:` and no path filter; a skipped required check counts as satisfied | MasterSpec v4.0 §33.2 |
| No third-party GitHub Action is used, so there is no unpinned action | §33.2; L0D-LG-4 |
| `permissions: contents: read` only — least privilege | §33.2 |
| The manifest, owners table, exception register and guard script are read from the BASE ref | §53.1 |
| The check context name is exactly `lane-guard` and never changes | §33.2 (a renamed context leaves branch protection referring to a context nothing emits) |
EOF

git add contracts/ci
git commit -m "L0-02-06: freeze the lane-guard workflow contract (L0D-LG-1)"
git push origin integration

make freeze
cat contracts.sha256
git add contracts.sha256
git commit -m "L0-02-06: record the contract freeze hash"
git push origin integration
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Frozen workflow exists | `test -f contracts/ci/lane-guard.yml.frozen && echo PRESENT` | `PRESENT` |
| 2 | Contract note exists | `test -f contracts/ci/lane-guard.contract.md && echo PRESENT` | `PRESENT` |
| 3 | Job name is exactly `lane-guard` | `grep -c '^    name: lane-guard$' contracts/ci/lane-guard.yml.frozen` | `1` |
| 4 | No `if:` on the job or its step | `grep -Ec '^\s+if:' contracts/ci/lane-guard.yml.frozen` | `0` |
| 5 | No path filter | `grep -Ec '^\s+paths(-ignore)?:' contracts/ci/lane-guard.yml.frozen` | `0` |
| 6 | No third-party action | `grep -Ec '^\s+-?\s*uses:' contracts/ci/lane-guard.yml.frozen` | `0` |
| 7 | Least-privilege token | `grep -c 'contents: read' contracts/ci/lane-guard.yml.frozen` | `1` |
| 8 | Freeze hash recorded and matching | `make promote-check` | `CONTRACTS-FROZEN OK` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP_ROOT"
F=contracts/ci/lane-guard.yml.frozen
printf 'frozen=%s note=%s name=%s ifs=%s paths=%s uses=%s perms=%s promote=%s\n' \
  "$(test -f $F && echo PRESENT || echo MISSING)" \
  "$(test -f contracts/ci/lane-guard.contract.md && echo PRESENT || echo MISSING)" \
  "$(grep -c '^    name: lane-guard$' $F)" \
  "$(grep -Ec '^[[:space:]]+if:' $F)" \
  "$(grep -Ec '^[[:space:]]+paths(-ignore)?:' $F)" \
  "$(grep -Ec '^[[:space:]]+-?[[:space:]]*uses:' $F)" \
  "$(grep -c 'contents: read' $F)" \
  "$(make promote-check 2>&1 | tail -1)"
```

Expected output, exactly:

```
frozen=PRESENT note=PRESENT name=1 ifs=0 paths=0 uses=0 perms=1 promote=CONTRACTS-FROZEN OK
```

**STOP rule** — if `ifs` or `paths` is non-zero, the required check can be skipped, and §33.2 states plainly that
a skipped required check is counted as satisfied by branch protection: the wall reads green while nothing ran.
Remove the condition; do not "guard it with a safe default". Open `BLOCKER L0-02-06: required check is
skippable`.

---

### L0-02-07 — Place the workflow on `integration` (one-time, L0D-LG-3)

**Size:** S · **Dependencies:** `L0-02-06`

Do this **before any `lane/N/*` branch exists**. Confirm that first; if any lane branch exists, this task's
premise has already been violated and the STOP rule applies.

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
git ls-remote --heads origin 'lane/*' | wc -l     # must print 0

mkdir -p .github/workflows
cp contracts/ci/lane-guard.yml.frozen .github/workflows/lane-guard.yml
cmp -s contracts/ci/lane-guard.yml.frozen .github/workflows/lane-guard.yml && echo IDENTICAL

git add .github/workflows/lane-guard.yml
git commit -m "L0-02-07: place the frozen lane-guard workflow (one-time, L0D-LG-3)"
git push origin integration
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | No lane branch existed at placement time | `git ls-remote --heads origin 'lane/*' \| wc -l` | `0` |
| 2 | Workflow installed | `test -f .github/workflows/lane-guard.yml && echo PRESENT` | `PRESENT` |
| 3 | Byte-identical to the contract | `cmp -s contracts/ci/lane-guard.yml.frozen .github/workflows/lane-guard.yml && echo IDENTICAL` | `IDENTICAL` |
| 4 | It is the only workflow L0 has placed | `ls .github/workflows \| wc -l` | `1` |
| 5 | GitHub parsed it — a run appears on the next PR | `gh run list --workflow lane-guard --limit 1 --json name --jq '.[0].name'` | `lane-guard` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP_ROOT"
printf 'lanebranches=%s installed=%s identical=%s count=%s\n' \
  "$(git ls-remote --heads origin 'lane/*' | wc -l | tr -d ' ')" \
  "$(test -f .github/workflows/lane-guard.yml && echo PRESENT || echo MISSING)" \
  "$(cmp -s contracts/ci/lane-guard.yml.frozen .github/workflows/lane-guard.yml && echo IDENTICAL || echo DIFFERS)" \
  "$(ls .github/workflows | wc -l | tr -d ' ')"
```

Expected output, exactly:

```
lanebranches=0 installed=PRESENT identical=IDENTICAL count=1
```

**STOP rule** — if `lanebranches` is not `0`, a lane branch already exists and L0 is now writing into a tree with
an active lane owner. Do not push. Open `BLOCKER L0-02-07: lane branch predates the guard`, delete the lane
branch after confirming with its owner that no work is lost, and re-run. Placing the guard after lanes are
running is the one ordering error this whole file exists to prevent.

---

### L0-02-08 — Make the check required, with zero bypass actors

**Size:** M · **Dependencies:** `L0-02-07`

Set `ORG` to the GitHub organisation login before running.

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org

cat > lane-guard-ruleset.json <<'EOF'
{
  "name": "lane-guard-required",
  "target": "branch",
  "enforcement": "active",
  "bypass_actors": [],
  "conditions": {
    "ref_name": {
      "include": ["refs/heads/integration", "refs/heads/main"],
      "exclude": []
    }
  },
  "rules": [
    {
      "type": "required_status_checks",
      "parameters": {
        "strict_required_status_checks_policy": true,
        "do_not_enforce_on_create": false,
        "required_status_checks": [{ "context": "lane-guard" }]
      }
    },
    { "type": "non_fast_forward" },
    { "type": "deletion" }
  ]
}
EOF

gh api --method POST "repos/$ORG/control-plane/rulesets" \
  --input lane-guard-ruleset.json > /tmp/lg-ruleset.json
RS_ID=$(jq -r '.id' /tmp/lg-ruleset.json); echo "ruleset id = $RS_ID"

gh api "repos/$ORG/control-plane/rulesets/$RS_ID" \
  --jq '{name, enforcement, bypass: (.bypass_actors|length), contexts: [.rules[]|select(.type=="required_status_checks")|.parameters.required_status_checks[].context]}'

git add lane-guard-ruleset.json
git commit -m "L0-02-08: lane-guard required status check, ruleset with no bypass actor (D89)"
git push origin integration
```

**`"bypass_actors": []` is not a default; it is the point.** D89: *"a bypass actor is exempt from every rule in
the ruleset it is listed on … so a compensator sitting inside the bypassed ruleset compensates for nothing."*
This ruleset carries the lane guard and nothing else, exactly so that no future bypass added for some other
purpose can reach it. If a bypass is ever needed for another rule, it goes in a **different** ruleset.

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Ruleset exists and is active | `gh api "repos/$ORG/control-plane/rulesets/$RS_ID" --jq .enforcement` | `active` |
| 2 | Zero bypass actors | `gh api "repos/$ORG/control-plane/rulesets/$RS_ID" --jq '.bypass_actors \| length'` | `0` |
| 3 | The required context is exactly `lane-guard` | `gh api "repos/$ORG/control-plane/rulesets/$RS_ID" --jq '[.rules[]\|select(.type=="required_status_checks")\|.parameters.required_status_checks[].context] \| join(",")'` | `lane-guard` |
| 4 | Covers `integration` and `main` | `gh api "repos/$ORG/control-plane/rulesets/$RS_ID" --jq '.conditions.ref_name.include \| join(",")'` | `refs/heads/integration,refs/heads/main` |
| 5 | Force-push and deletion blocked | `gh api "repos/$ORG/control-plane/rulesets/$RS_ID" --jq '[.rules[].type] \| sort \| join(",")'` | `deletion,non_fast_forward,required_status_checks` |
| 6 | **Negative test:** a PR that violates the partition cannot be merged | see SELF-VERIFY | `mergeable_state=blocked` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP_ROOT"
source "$(git rev-parse --show-toplevel)/contracts/project-config.sh"
check_org
RS_ID=$(gh api "repos/$ORG/control-plane/rulesets" --jq '.[]|select(.name=="lane-guard-required")|.id')

# negative test: a real lane branch that touches a foreign path must be blocked
git checkout -b lane/1/zz-guard-negative-test integration
mkdir -p reconciler && echo "negative test" > reconciler/zz-negative.txt
git add -A && git commit -q -m "negative test: lane 1 touches lane 3"
git push -u origin lane/1/zz-guard-negative-test
PR=$(gh pr create --base integration --head lane/1/zz-guard-negative-test \
       --title "NEGATIVE TEST — do not merge" --body "L0-02-08 acceptance criterion 6" \
       --json number --jq .number)
gh pr checks "$PR" --watch >/dev/null 2>&1 || true

printf 'enforcement=%s bypass=%s context=%s conclusion=%s state=%s\n' \
  "$(gh api "repos/$ORG/control-plane/rulesets/$RS_ID" --jq .enforcement)" \
  "$(gh api "repos/$ORG/control-plane/rulesets/$RS_ID" --jq '.bypass_actors|length')" \
  "$(gh api "repos/$ORG/control-plane/rulesets/$RS_ID" --jq '[.rules[]|select(.type=="required_status_checks")|.parameters.required_status_checks[].context]|join(",")')" \
  "$(gh pr checks "$PR" --json name,state --jq '.[]|select(.name=="lane-guard")|.state')" \
  "$(gh pr view "$PR" --json mergeStateStatus --jq .mergeStateStatus)"

gh pr close "$PR" --delete-branch
git checkout integration
```

Expected output, exactly:

```
enforcement=active bypass=0 context=lane-guard conclusion=FAILURE state=BLOCKED
```

**STOP rule** — if `state` is not `BLOCKED`, the check runs and reports failure but does not stop a merge, which
is the worst of the three possible states: a wall that looks like a wall. Do not create any lane branch. Confirm
the repository is on a plan where branch protection on private repositories is available — **D73 records that
this requires the Team plan and is non-negotiable** — and open `BLOCKER L0-02-08: lane-guard is not blocking`.

---

### L0-02-09 — Publish the runbook and wire the Makefile

**Size:** M · **Dependencies:** `L0-02-04`, `L0-02-05`, `L0-02-08`

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"

# --- Makefile: append the lane-guard targets (Makefile is L0-owned) ---
cat >> Makefile <<'MK'

.PHONY: lane-guard-selftest codeowners guard-verify

lane-guard-selftest:
	@sh ./lane-guard-selftest.sh

codeowners:
	@sh ./codeowners-gen.sh

# The full pre-merge-train assertion the integrator runs before every train.
guard-verify:
	@sh -n lane-guard.sh          && echo "guard-syntax OK"
	@sh ./lane-guard-selftest.sh  | tail -1
	@sh ./codeowners-gen.sh       | tail -1
	@git diff --quiet CODEOWNERS  && echo "codeowners STABLE" || { echo "codeowners DRIFTED"; exit 1; }
	@cmp -s contracts/ci/lane-guard.yml.frozen .github/workflows/lane-guard.yml \
	  && echo "workflow IDENTICAL" || { echo "workflow TAMPERED"; exit 1; }
	@$(MAKE) --no-print-directory promote-check
MK

# --- the runbook ---
mkdir -p docs
cp "C:/D_Drive/PS/MultiProduct/Code/implementation/lanes/L0-02-lane-guard.md" docs/lane-guard.md

git add Makefile docs/lane-guard.md
git commit -m "L0-02-09: lane-guard make targets and published runbook"
git push origin integration

make guard-verify
```

Then add one row to `docs/README.md`'s table (that file is L0-owned, created by L0-00-02):

**Commands**

```bash
set -euo pipefail
cd "$CP_ROOT"
printf '| `lane-guard.md`         | The lane guard: manifest, workflow, error messages, override procedure |\n' >> docs/README.md
git add docs/README.md
git commit -m "L0-02-09: index the lane-guard runbook"
git push origin integration
```

**Acceptance criteria**

| # | Criterion | Proving command | Unambiguous output |
|---|---|---|---|
| 1 | Runbook published | `test -f docs/lane-guard.md && echo PRESENT` | `PRESENT` |
| 2 | Indexed in the docs table | `grep -c 'lane-guard.md' docs/README.md` | `1` |
| 3 | `make lane-guard-selftest` passes | `make lane-guard-selftest \| tail -1` | `SELFTEST 14/14 PASS` |
| 4 | `make codeowners` is idempotent | `make codeowners >/dev/null; git diff --quiet CODEOWNERS && echo STABLE` | `STABLE` |
| 5 | `make guard-verify` passes end to end | `make guard-verify \| tail -1` | `CONTRACTS-FROZEN OK` |
| 6 | `make guard-verify` fails on a tampered workflow | see SELF-VERIFY | `rc=2` and `workflow TAMPERED` |

**SELF-VERIFY**

```bash
set -euo pipefail
cd "$CP_ROOT"
ok=$(make guard-verify 2>&1 | tail -1)
cp .github/workflows/lane-guard.yml /tmp/lg-wf.bak
echo "# tamper" >> .github/workflows/lane-guard.yml
make guard-verify >/tmp/lg-tamper.out 2>&1; rc=$?
cp /tmp/lg-wf.bak .github/workflows/lane-guard.yml
printf 'verify=%s tamper_rc=%s tamper_msg=%s docs=%s indexed=%s\n' \
  "$ok" "$rc" \
  "$(grep -c 'workflow TAMPERED' /tmp/lg-tamper.out)" \
  "$(test -f docs/lane-guard.md && echo PRESENT || echo MISSING)" \
  "$(grep -c 'lane-guard.md' docs/README.md)"
```

Expected output, exactly:

```
verify=CONTRACTS-FROZEN OK tamper_rc=2 tamper_msg=1 docs=PRESENT indexed=1
```

**STOP rule** — if `tamper_msg` is `0`, the local pre-train gate does not notice a modified workflow, and L0's
merge-train step 2 becomes a rubber stamp. Fix the `guard-verify` target before running any train. Open
`BLOCKER L0-02-09: guard-verify does not detect workflow tampering`.

---

## 14. Dependency graph

```
L0-00-01 ──────────────┐
L0-00-03 ──► L0-02-01 ─┼──► L0-02-05 ──┐
L0-00-04 ──► L0-02-02 ─┴──► L0-02-03 ──┴──► L0-02-04 ──┐
                             L0-02-03 ──► L0-02-06 ──► L0-02-07 ──► L0-02-08 ──► L0-02-09
```

| Task | Size | Depends on | Blocks |
|---|---|---|---|
| L0-02-01 lane-owners.tsv | S | L0-00-03 | T02, T05 |
| L0-02-02 lane-guard.sh v2 | L | L0-00-04, T01 | T03, T04, T06 |
| L0-02-03 override register | S | T02 | T04, T06 |
| L0-02-04 adversarial self-test | L | T02, T03 | T09 |
| L0-02-05 generate CODEOWNERS | M | T01, L0-00-01 | T09 |
| L0-02-06 freeze the workflow contract | M | T02, T03 | T07 |
| L0-02-07 place the workflow | S | T06 | T08 |
| L0-02-08 make the check required | M | T07 | T09 |
| L0-02-09 runbook and make targets | M | T04, T05, T08 | — |

**Nothing in lanes L1–L5 may start until L0-02-08's SELF-VERIFY prints `state=BLOCKED`.** That is the moment the
partition stops being a document and becomes a wall.

---

## 15. Where the guard sits in the merge train

L0's train step 2 (charter §9) becomes exact:

| Step | Command | Must print |
|---|---|---|
| 1 | `git fetch --all --prune && git checkout integration && git pull --ff-only` | — |
| 2 | `make guard-verify` | ends `CONTRACTS-FROZEN OK` |
| 3 | for lane N in the frozen order **L1 → L4 → L2 → L3 → L5**: `LANE=N BASE=integration HEAD=origin/lane/N/<branch> make lane-guard` | `LANE-GUARD OK` |
| 4 | `git merge --no-ff origin/lane/N/<branch>` | — |
| 5 | `make guard-verify` again, after the merge | ends `CONTRACTS-FROZEN OK` |

Step 3 is the local re-run of the same script CI ran. It is not redundant: CI judged the branch against
`integration` **at the time the PR ran**, and the train moves `integration` under it. Re-running at merge time is
what makes the check true of the tree that actually lands.

---

## 16. What the lane guard does not do — stated honestly

A control whose limits are undocumented gets trusted past them.

| Not covered | Why | Compensating control |
|---|---|---|
| Content of a file inside a lane's own tree | The guard is a path control, not a semantic one | Contract tests and the merge gate (`protocol/05-merge-gate.md`) |
| A lane importing another lane's source at runtime | Not visible in a path diff | PARTITION.md rule 4; caught by contract tests, not by this guard |
| A lane adding a shared mutable file inside its own tree | Path-legal, partition-hostile | PARTITION.md rule 3; L0 review at the train |
| Whether the *right* human approved | A different check entirely | Reviewer-matrix validation, §23.2: *"fails when the approving reviewer is not the routed one"* |
| `control-plane-records` | One lane owns the whole repository | D107 no-bypass ruleset; D89 credential scoping; reconciler head-SHA anchoring (§12 above) |
| An org admin disabling the ruleset | No repository-level control survives an org admin | The independent control verifier of §53.1, running off the operations VM under a different credential, asserting that ruleset JSON matches the committed template and that the bypass-actor list is exactly what §40.1 and §33.2 declare |

The last row is the important one, and it is the spec's own answer to "who guards the guard": not another check
inside the same repository under the same credential, but a scheduled workflow holding its own read-only
fine-grained credential, writing its result to a surface the operations VM cannot write to, whose **absence for
one cycle is itself a Level 5 finding** (§53.1). Building that verifier is L5's work under `access/**`. The lane
guard is what keeps five agents from colliding for the eight weeks before it exists.
