#!/usr/bin/env bash
# run-orphan-check.sh — L3-05 orphan detection runner (FD-108/PFD-028)
# Orchestrates the 5 orphan detection surfaces defined in contracts/orphans/decisions.yaml:
#   1. asset_list                       — docs/assets/asset-list.yaml
#   2. delegation_expiry_warning        — assignment records with end_date (see §10.1 17-row table)
#   3. board_snapshot                   — records/board/snapshot.yaml (comparison target for 1 and 4)
#   4. open_work_snapshot               — records/work/open.yaml
#   5. customer_commitment_owner_field  — commitments[].owner vs registries/people
# The numbered "Surface N" sections below are script sections, not a 1:1 map onto
# the 5 names above — board_snapshot and open_work_snapshot are checked as the
# comparison target inside the Surface 1 delegate, and Surface 2 is a canary
# sanity pre-check unrelated to the 5-surface contract.
set -euo pipefail
shopt -s nullglob

echo "=== L3-05 Orphan Detection (FD-108/PFD-028) ==="
echo "Surfaces: asset_list, delegation_expiry_warning, board_snapshot, open_work_snapshot, customer_commitment_owner_field"
echo ""

ORPHANS=0
WARNINGS=0

# Surface 1: assets not on board (delegates to scripts/orphan-detect.sh, which
# itself covers asset_list vs board_snapshot and open_work_snapshot vs
# board_snapshot). Fold its real ORPHANS count into ours instead of just
# echoing its output — a real orphan there must fail this script too.
echo "Surface 1: Asset list vs board snapshot (delegates to scripts/orphan-detect.sh)"
SURFACE1_EXIT=0
SURFACE1_OUTPUT=$(bash scripts/orphan-detect.sh . 2>&1) || SURFACE1_EXIT=$?
echo "$SURFACE1_OUTPUT"
SURFACE1_COUNT=$(printf '%s\n' "$SURFACE1_OUTPUT" | grep -oE '[0-9]+ orphans? found' | tail -n1 | grep -oE '^[0-9]+' || true)
SURFACE1_COUNT=${SURFACE1_COUNT:-0}
if [[ "$SURFACE1_EXIT" -ne 0 && "$SURFACE1_COUNT" -eq 0 ]]; then
  # Non-zero exit is the expected, self-explanatory signal when orphans were
  # found and folded below (its exit and its own printed count agree). A
  # non-zero exit with NO parsed count is unexplained — do not let it read
  # as a silent 0; report it and treat it as a failure of its own.
  echo "  WARNING: scripts/orphan-detect.sh exited non-zero ($SURFACE1_EXIT) but printed no parseable orphan count — treating as an unexplained failure, not a clean pass"
  WARNINGS=$((WARNINGS + 1))
  SURFACE1_COUNT=1
fi
ORPHANS=$((ORPHANS + SURFACE1_COUNT))
echo "  -> folded ${SURFACE1_COUNT} orphan(s) from scripts/orphan-detect.sh into the running total"
echo ""

# Surface 2: canary check (fast sanity check; not one of the 5 contract surfaces,
# but guards the people registry data several of them read).
echo "Surface 2: Canary integrity check"
bash scripts/canary-check.sh registries/people/_canary.yaml
echo ""

# Surface 3: Commitment owners in people registry (customer_commitment_owner_field)
echo "Surface 3: Commitment owner cross-check"
COMMIT_DIR="records/commitments"
PEOPLE_DIR="registries/people"
if [[ -d "$COMMIT_DIR" ]]; then
  ORPHANS_BEFORE_SURFACE3=$ORPHANS
  FILES_CHECKED=0
  for COMMIT_FILE in "$COMMIT_DIR"/*.yaml; do
    [[ -f "$COMMIT_FILE" ]] || continue
    FILES_CHECKED=$((FILES_CHECKED + 1))
    OWNER_ERR=$(mktemp)
    if OWNER=$(COMMIT_FILE_PATH="$COMMIT_FILE" python3 - <<'PYEOF' 2>"$OWNER_ERR"
import os, sys, yaml
path = os.environ["COMMIT_FILE_PATH"]
try:
    d = yaml.safe_load(open(path))
except Exception as e:
    print(f"parse error: {e}", file=sys.stderr)
    sys.exit(1)
if not isinstance(d, dict):
    print(f"expected a YAML mapping at top level, got {type(d).__name__}", file=sys.stderr)
    sys.exit(1)
print(d.get("owner", ""))
PYEOF
    ); then
      : # OWNER extracted (may legitimately be empty if the file has no owner field)
    else
      ERR_MSG=$(tr '\n' ' ' < "$OWNER_ERR" | sed -E 's/[[:space:]]+/ /g; s/[[:space:]]*$//')
      echo "  WARNING: could not extract owner from $(basename "$COMMIT_FILE"): ${ERR_MSG:-unknown parse error}"
      WARNINGS=$((WARNINGS + 1))
      OWNER=""
    fi
    rm -f "$OWNER_ERR"
    if [[ -n "$OWNER" ]] && [[ ! -f "$PEOPLE_DIR/${OWNER}.yaml" ]]; then
      echo "  ORPHAN: commitment $(basename "$COMMIT_FILE") owner '$OWNER' not in people registry"
      ORPHANS=$((ORPHANS + 1))
    fi
  done
  if [[ $FILES_CHECKED -eq 0 ]]; then
    echo "  OK: 0 files checked ($COMMIT_DIR is empty — nothing to cross-check yet)"
  elif [[ $ORPHANS -eq $ORPHANS_BEFORE_SURFACE3 ]]; then
    echo "  OK: $FILES_CHECKED files checked, 0 orphans"
  else
    echo "  $FILES_CHECKED files checked, $((ORPHANS - ORPHANS_BEFORE_SURFACE3)) orphan(s) found"
  fi
else
  echo "  SKIP: $COMMIT_DIR not found"
fi
echo ""

# Surface 4: delegation_expiry_warning. No dedicated check exists yet. Genuinely
# search registries/ and records/ for delegation/assignment records carrying an
# end_date (the field the §10.1 17-row table keys the warning on) rather than
# assuming there's nothing to check and silently omitting the surface.
echo "Surface 4: Delegation expiry warning"
DELEGATION_CANDIDATES=""
for SRC_DIR in registries records; do
  [[ -d "$SRC_DIR" ]] || continue
  MATCHES=$(grep -rIlE 'end_date[[:space:]]*:|[^a-zA-Z_]_?[a-z_]*_delegate([^a-zA-Z_]|$)|cross_review_shadow|temporary_contributor' "$SRC_DIR" 2>/dev/null || true)
  [[ -n "$MATCHES" ]] && DELEGATION_CANDIDATES="${DELEGATION_CANDIDATES}${MATCHES}"$'\n'
done
DELEGATION_CANDIDATES=$(printf '%s' "$DELEGATION_CANDIDATES" | sed '/^$/d' | sort -u)
if [[ -z "$DELEGATION_CANDIDATES" ]]; then
  echo "  SURFACE NOT YET IMPLEMENTED: delegation_expiry_warning — 0 checked (no assignment records with an end_date found under registries/ or records/; assignments.v1.schema.json not yet created — see lanes/L1-05-tasks.md L1-302)"
else
  echo "  Candidate delegation/assignment records found (no automated check wired up yet):"
  printf '%s\n' "$DELEGATION_CANDIDATES" | sed 's/^/    - /'
  echo "  SURFACE NOT YET IMPLEMENTED: delegation_expiry_warning — 0 checked (candidates listed above still need a real check)"
fi
echo ""

echo "=== Orphan Detection Complete: $ORPHANS orphans found, $WARNINGS warning(s) ==="
[[ $ORPHANS -eq 0 && $WARNINGS -eq 0 ]]
