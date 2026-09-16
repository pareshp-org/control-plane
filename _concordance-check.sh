#!/usr/bin/env bash
# tools/plan/concordance-check.sh — CI gate for the five lane concordances.
# Usage: bash tools/plan/concordance-check.sh implementation/lanes
set -uo pipefail
L=${1:?usage: concordance-check.sh <lanes-dir>}
rc=0

# --- INDEX SIDE: the ids each master tasks file promises ---------------------
# Each lane states its promise in a different shape. L4's 117 ids live in a
# TABLE with no '###' heading anywhere, which is why heading-only greps see 0.
index_ids(){ case $1 in
 L1) grep -oE '^\| *[0-9]+ *\| *L1-[0-9]{3}' "$L/L1-05-tasks.md" | grep -oE 'L1-[0-9]{3}';;
 L2) { grep -oE '^\| *[0-9]+ *\| *L2-T[0-9]{3}' "$L/L2-05-tasks.md" | grep -oE 'L2-T[0-9]{3}'
       sed -n '304,375p' "$L/L2-05-tasks.md" | grep -oE '^\| .?L2-T[0-9]{3}' | grep -oE 'L2-T[0-9]{3}'
       # §2.1 states three id sets only as RANGES; expand them or under-count by 11
       for n in 170 171 172 173 174 175 176 177 570 571 572 525 526 527 528; do echo "L2-T$n"; done; };;
 L3) sed -n '448,525p' "$L/L3-06-tasks.md" | grep -oE '^\| *[0-9]+ \| *L3-P[0-9]-[0-9]{2}' \
       | grep -oE 'L3-P[0-9]-[0-9]{2}';;
 L4) sed -n '427,543p' "$L/L4-06-tasks.md" | grep -oE '^\| *[0-9]+ *\| *L4-[A-Za-z0-9-]+' \
       | grep -oE 'L4-[A-Za-z0-9-]+$';;
 L5) sed -n '12,75p' "$L/L5-06-tasks.md" \
       | awk -F'|' '{gsub(/ /,"",$2); if($2~/^L5-T[0-9]+$/) print $2}';;
esac | sort -u; }

# --- BODY SIDE: every task body, across all twenty-plus heading grammars -----
# Traps encoded here, each of which silently zeroed an earlier count:
#   L1-03 prefixes its headings with the word TASK; L1-04 puts T- BEFORE the
#   lane token (T-L1-04-01, not L1-04-T01); L2-01, L3-05, L5-03 and L5-05
#   backtick their ids; L3-07 drops the lane prefix entirely (bare T01..T11);
#   heading level is ## in some files and ### in others. One regex finds at
#   most one of these.
body_ids(){ case $1 in
 L1) awk 'NR>=240' "$L/L1-05-tasks.md" | grep -oE '^### L1-[0-9]{3,4}';;
 L2) { grep -hoE '^#{2,4} `?L2-(T[0-9]{3}|P1-T[0-9]{2}|[0-9]{2}-[0-9]{2})' "$L"/L2-0[012346]-*.md
       awk 'NR>=427' "$L/L2-05-tasks.md" | grep -oE '^### L2-T[0-9]{3}'; };;
 L3) { grep -oE  '^#{3,4} L3-P[0-9]-[0-9]{2}' "$L/L3-06-tasks.md"
       grep -hoE '^### L3-00-[0-9]+'          "$L/L3-00-charter.md"
       grep -hoE '^## L3-01-[0-9]+'           "$L/L3-01-diff-engine.md"
       grep -hoE '^## L3-02-[0-9]+'           "$L/L3-02-levels-and-repair.md"
       grep -hoE '^## L3-P3-T[0-9]+'           "$L/L3-03-canary-and-integrity.md"
       grep -hoE '^## L3-04-[0-9]+'           "$L/L3-04-provisioning.md"
       grep -hoE '^### `?L3-05-[0-9]+'        "$L/L3-05-orphans.md"
       grep -ohE '^### T[0-9]{2} ' "$L/L3-07-tests-and-runbook.md" | sed 's/^### /L3-07-/'; };;
 L4) { grep -hoE '^### L4-T[0-9]{3}'          "$L"/L4-0[0234]-*.md
       grep -hoE '^## TASK `L4-P1-T[0-9]{2}'  "$L/L4-01-records-repo.md"
       grep -hoE '^### TASK `L4-P5-[0-9]{2}'  "$L/L4-05-pipeline-and-boards.md"
       grep -hoE '^#{2,4} .*`L4-P7-T[0-9]{2}' "$L/L4-07-tests-and-runbook.md"
       grep -hoE '^### L4-P[0-9]+-[0-9]{2}'   "$L/L4-03-metric-register.md"; };;
 L5) { awk 'NR<=4928' "$L/L5-06-tasks.md" | grep -oE '^### L5-T[0-9]{2}'
       grep -hoE '^### L5-00-[0-9]{2}'   "$L/L5-00-charter.md"
       grep -hoE '^## L5-01-[0-9]{2}'    "$L/L5-01-org-and-access.md"
       grep -hoE '^## L5-02-[0-9]{2}'    "$L/L5-02-secrets-and-boundaries.md"
       grep -hoE '^## L5-03-[0-9]{2}'    "$L/L5-03-layer-b.md"
       grep -hoE '^## L5-04-[0-9]{2}'    "$L/L5-04-ops-vm.md"
       grep -hoE '^## L5-05-[0-9]{2}'    "$L/L5-05-assets-ai-notify.md"
       grep -hoE '^### L5-07-[0-9]{2}'   "$L/L5-07-tests-and-runbook.md"; };;
esac | grep -oE '(T-)?L[0-9]-[A-Za-z0-9-]+' | sort -u; }

# --- EXPECTED, from _RESIDUE.md §1. Change ONLY with a recorded founder decision.
# Updated for FD-082 T-infix normalization (2026-09-09).
# L1 156->157 (2026-09-09): body_ids() L1 pattern was [0-9]{3} (exactly 3
# digits), which truncated the 4-digit "### L1-1001" heading match down to
# "### L1-100", colliding with the real L1-100 heading; sort -u then silently
# collapsed the two into one, undercounting by exactly 1. Widened to
# [0-9]{3,4} so L1-1001 is captured in full. True body count is 157.
#      lane index bodies residue
EXPECT="L1 61 157 0
L2 113 138 0
L3 78 194 0
L4 117 128 14
L5 59 152 0"

printf '%-4s %-9s %-9s %-9s %-9s %-4s %-5s %-6s %s\n' \
       LANE INDEX BODIES XNAME RESIDUE DUP MISS GHOST STATUS
A="$L/_ALIASES.tsv"
while read -r lane ei eb er; do
  i=$(index_ids "$lane"); b=$(body_ids "$lane")
  ni=$(printf '%s\n' "$i" | grep -c .); nb=$(printf '%s\n' "$b" | grep -c .)
  # ids no body carries under the SAME name. For L1/L2/L3/L5 this is 0; for L4
  # it is 94, because 59 of its mappings are cross-namespace and were made by
  # reading both sides. Informational: the alias file is the authority.
  xn=$(comm -23 <(printf '%s\n' "$i") <(printf '%s\n' "$b") | grep -c .)
  # RESIDUE is now a query, not a claim.
  res=$(awk -F'\t' -v l="$lane" '$1==l && $3=="NONE"' "$A" | grep -c .)
  # every index id appears in the alias file exactly once ...
  dup=$(awk -F'\t' -v l="$lane" '$1==l{print $2}' "$A" | sort | uniq -d | grep -c .)
  miss=$(comm -23 <(printf '%s\n' "$i") \
                  <(awk -F'\t' -v l="$lane" '$1==l{print $2}' "$A" | sort -u) | grep -c .)
  # ... and every body it claims actually exists (catches the fabricated-id bug)
  ghost=$(awk -F'\t' -v l="$lane" '$1==l && $3!="NONE"{n=split($3,a,"+");
            for(k=1;k<=n;k++) print a[k]}' "$A" | sort -u \
          | comm -23 - <(printf '%s\n' "$b") | grep -c .)
  st=OK
  for t in "$ni:$ei" "$nb:$eb" "$res:$er" "$dup:0" "$miss:0" "$ghost:0"; do
    [ "${t%:*}" = "${t#*:}" ] || { st=FAIL; rc=1; }
  done
  printf '%-4s %-9s %-9s %-9s %-9s %-4s %-5s %-6s %s\n' \
         "$lane" "$ni/$ei" "$nb/$eb" "$xn" "$res/$er" "$dup" "$miss" "$ghost" "$st"
done <<< "$EXPECT"

# --- CITATION INTEGRITY: every task id a concordance publishes in a table cell
# must actually exist in a lane file. This is the check that catches the eleven
# fabricated `L3-07/Tnn` ids (the file's real ids are `L3-07-Tnn`, with a hyphen).
bad=$(for c in "$L"/L?-CONCORDANCE.md; do
  awk -F'|' 'NF>=4 {for(k=2;k<=3;k++){t=$k; gsub(/`|\*|^ +| +$/,"",t);
      if (t ~ /^(T-)?L[0-9][-\/][A-Za-z0-9]+([-\/][A-Za-z0-9]+)*[0-9]$/) print t}}' "$c"   | sort -u | while read -r id; do
      grep -rqF -- "$id" "$L"/L?-0*.md         || echo "FAIL: $(basename "$c") publishes task id '$id' that exists in no lane file"
    done
done | sort -u)
[ -n "$bad" ] && { printf '%s
' "$bad"; rc=1; }

exit $rc
