#!/usr/bin/env sh
# =============================================================================
# onboard-floor.sh — L0-owned. The universal-floor burn-down and the
# paper-floor detector. MasterSpec v4.0 Section 96.6 (spec L8802):
# nine items x every live product = seventy-two tracked obligations, each row
# carrying a named executor (Section 95.4) and a date.
# usage: onboard-floor.sh [--asof YYYY-MM-DD] [--slot NN]
# =============================================================================
set -u
OB="${OB_ROOT:-docs/onboarding}"
ASOF=$(date -u +%Y-%m-%d)
ONLY=""
while [ $# -gt 0 ]; do
  case "$1" in
    --asof) ASOF="$2"; shift 2 ;;
    --slot) ONLY="$2"; shift 2 ;;
    *) echo "usage: onboard-floor.sh [--asof YYYY-MM-DD] [--slot NN]" >&2; exit 2 ;;
  esac
done

# older <a> <b> — true when ISO date a is strictly earlier than ISO date b.
# Uses sort, not test '<', because POSIX test has no string-ordering operator.
older() {
  [ "$1" != "$2" ] || return 1
  [ "$(printf '%s\n%s\n' "$1" "$2" | sort | head -1)" = "$1" ]
}

total=0; closed=0; paper=0; red=0; unexec=0
for d in "$OB"/products/*/; do
  slot=$(basename "$d")
  [ -z "$ONLY" ] || [ "$ONLY" = "$slot" ] || continue
  for f in "$d"floor/*.tsv; do
    [ -f "$f" ] || continue
    item=$(awk -F'	'     '$1=="item"{print $2}'          "$f" | tr -d '\r')
    st=$(awk -F'	'       '$1=="status"{print $2}'        "$f" | tr -d '\r')
    ev=$(awk -F'	'       '$1=="evidence"{print $2}'      "$f" | tr -d '\r')
    dt=$(awk -F'	'       '$1=="date"{print $2}'          "$f" | tr -d '\r')
    ex=$(awk -F'	'       '$1=="executor"{print $2}'      "$f" | tr -d '\r')
    ar=$(awk -F'	'       '$1=="accepted_risk"{print $2}' "$f" | tr -d '\r')
    total=$((total+1))
    [ "$ex" = "UNSET" ] && unexec=$((unexec+1))
    if [ "$st" = "closed" ]; then
      closed=$((closed+1))
      if [ "$ev" = "UNSET" ]; then
        echo "PAPER-FLOOR slot=$slot item=$item — closed with no evidence (Section 96.6 L8802)"
        paper=$((paper+1))
      fi
    else
      if [ "$dt" != "UNSET" ] && older "$dt" "$ASOF" && [ "$ar" = "UNSET" ]; then
        echo "RED-FLOOR slot=$slot item=$item date=$dt — outstanding past its date with no dated accepted risk"
        red=$((red+1))
      fi
    fi
  done
done

open=$((total-closed))
echo "FLOOR total=$total closed=$closed open=$open paper=$paper red=$red unexecuted=$unexec asof=$ASOF"
[ "$paper" -eq 0 ] && [ "$red" -eq 0 ] || exit 1
exit 0
