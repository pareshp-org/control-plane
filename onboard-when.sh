#!/usr/bin/env sh
# =============================================================================
# onboard-when.sh — L0-owned. The ONLY writer of a resolved date in the
# onboarding track. Mechanical form of D99 (MasterSpec v4.0 L10192):
# "an Onboarding track whose per-product phases are relative to the subsystems
# they consume. Pre-onboarding deadlines are set from the Onboarding track,
# not from the labels."
# Store: docs/onboarding (override with OB_ROOT for fixtures).
# Plan: implementation/lanes/L0-07-onboarding-track.md L0-07-04.
# =============================================================================
set -u
OB="${OB_ROOT:-docs/onboarding}"

usage() {
  echo "usage: onboard-when.sh resolve <expr> | set <token> <YYYY-MM-DD> <who> | lint | check" >&2
  exit 2
}

is_date() {
  case "$1" in
    [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]) return 0 ;;
    *) return 1 ;;
  esac
}

anchor_date() {                       # $1 = token
  f="$OB/anchors/$1.tsv"
  if [ ! -f "$f" ]; then echo "MISSING"; return; fi
  v=$(awk -F'	' '$1=="date"{print $2}' "$f")
  if [ -z "$v" ]; then echo "UNSET"; else echo "$v"; fi
}

resolve_one() {                       # $1 = TOKEN[+Nw]
  e="$1"
  case "$e" in
    *+*w) tok=$(printf '%s' "$e" | sed 's/+.*$//')
          off=$(printf '%s' "$e" | sed 's/^.*+//; s/w$//') ;;
    *)    tok="$e"; off=0 ;;
  esac
  case "$off" in ''|*[!0-9]*) echo "BAD-EXPRESSION"; return ;; esac
  d=$(anchor_date "$tok")
  case "$d" in
    MISSING) echo "UNKNOWN-TOKEN"; return ;;
    UNSET)   echo "UNANCHORED";   return ;;
  esac
  if is_date "$d"; then
    date -u -d "$d +$off weeks" +%Y-%m-%d
  else
    echo "BAD-ANCHOR"
  fi
}

resolve() {                           # $1 = expr, possibly max(e1,e2)
  e="$1"
  case "$e" in
    max\(*\))
      inner=$(printf '%s' "$e" | sed 's/^max(//; s/)$//')
      a=$(printf '%s' "$inner" | sed 's/,.*$//')
      b=$(printf '%s' "$inner" | sed 's/^[^,]*,//')
      ra=$(resolve_one "$a"); rb=$(resolve_one "$b")
      for r in "$ra" "$rb"; do
        case "$r" in UNANCHORED|UNKNOWN-TOKEN|BAD-EXPRESSION|BAD-ANCHOR) echo "$r"; return ;; esac
      done
      printf '%s
%s
' "$ra" "$rb" | sort | tail -1
      ;;
    *) resolve_one "$e" ;;
  esac
}

lint() {
  # An absolute week label in an expression-bearing file is the exact failure D99
  # forbids. Floor rows are NOT scanned: floor rows are dated (Section 96.6 L8802,
  # this plan section 3.1). Only plan.tsv and deadline.tsv carry expressions.
  hits=0
  for f in "$OB"/products/*/plan.tsv "$OB"/products/*/deadline.tsv; do
    [ -f "$f" ] || continue
    if grep -nEi 'week[s]?[ _-]?[0-9]' "$f" >/dev/null 2>&1; then
      grep -nEi 'week[s]?[ _-]?[0-9]' "$f" | sed "s|^|ABSOLUTE-LABEL $f:|"
      hits=$((hits+1))
    fi
  done
  echo "WHEN-LINT files_with_labels=$hits"
  [ "$hits" -eq 0 ] || return 1
  return 0
}

check() {
  bad=0; n=0
  for f in "$OB"/products/*/deadline.tsv; do
    [ -f "$f" ] || continue
    slot=$(basename "$(dirname "$f")")
    src=$(awk -F'	' '$1=="source_expr"{print $2}' "$f")
    got=$(awk -F'	' '$1=="resolved"{print $2}' "$f")
    [ "$src" = "UNSET" ] && continue
    n=$((n+1))
    want=$(resolve "$src")
    if [ "$want" != "$got" ]; then
      echo "STALE-RESOLUTION slot=$slot expr=$src recorded=$got recomputed=$want"
      bad=$((bad+1))
    fi
  done
  echo "WHEN-CHECK resolved=$n stale=$bad"
  [ "$bad" -eq 0 ] || return 1
  return 0
}

[ $# -ge 1 ] || usage
cmd="$1"; shift
case "$cmd" in
  resolve) [ $# -eq 1 ] || usage; resolve "$1" ;;
  set)
    [ $# -eq 3 ] || usage
    tok="$1"; d="$2"; who="$3"
    f="$OB/anchors/$tok.tsv"
    [ -f "$f" ] || { echo "NO-SUCH-ANCHOR $tok — create the anchor file first (L0-07-01/T11)" >&2; exit 1; }
    is_date "$d" || { echo "NOT-A-DATE $d" >&2; exit 1; }
    printf 'token	%s
date	%s
declared_by	%s
' "$tok" "$d" "$who" > "$f"
    echo "ANCHORED $tok=$d by=$who"
    ;;
  lint|--lint)   lint ;;
  check|--check) check ;;
  *) usage ;;
esac
