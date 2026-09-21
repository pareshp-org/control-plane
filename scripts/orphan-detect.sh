#!/usr/bin/env bash
# orphan-detect.sh — L5 orphan detection (FD-108/PFD-028)
#
# Implements 3 of the 5 surfaces defined in contracts/orphans/decisions.yaml
# (delegation_expiry_warning and customer_commitment_owner_field are out of
# scope for this script; the latter is already covered by
# scripts/l3/run-orphan-check.sh Surface 3 and validators/registry rule R12):
#
#   Surface 1 (asset_list, contracts/orphans/decisions.yaml `asset_list`):
#     every `asset_id` in docs/assets/asset-list.yaml must be referenced by
#     something real — a board_snapshot item or an open_work_snapshot item —
#     else it is an orphaned asset with no consumer.
#
#   Surface 2 (board_snapshot vs asset_list/open_work_snapshot):
#     every item placed on records/board/snapshot.yaml must trace back to a
#     real asset (by asset_id) or a real open-work item (by id); an item
#     that resolves to neither is an orphaned board entry.
#
#   Surface 3 (open_work_snapshot):
#     every item in records/work/open.yaml must have a valid owner — a
#     non-empty `assignee` (the schemas/work/open.v1.schema.json owner
#     field) that resolves to a real entry in registries/people/.
#
# Reference-field convention: since neither contracts/orphans/decisions.yaml
# nor schemas/board/snapshot.v1.schema.json defines a per-item shape for
# board_snapshot entries, a board item (dict or bare scalar id) is matched
# against known ids via any of: asset_id, id, work_id, item_id.
#
# Usage: bash scripts/orphan-detect.sh [--root <path>]
set -euo pipefail

ROOT="${1:-.}"
ASSET_LIST="$ROOT/docs/assets/asset-list.yaml"
BOARD_SNAPSHOT="$ROOT/records/board/snapshot.yaml"
OPEN_WORK="$ROOT/records/work/open.yaml"
PEOPLE_DIR="$ROOT/registries/people"

echo "=== Orphan Detection (FD-108/PFD-028) ==="
echo "Root: $ROOT"
echo "Surface 1: asset_list vs board_snapshot/open_work_snapshot"
echo "Surface 2: board_snapshot vs asset_list/open_work_snapshot"
echo "Surface 3: open_work_snapshot owner validity"
echo ""

PYOUT="$(python3 - "$ASSET_LIST" "$BOARD_SNAPSHOT" "$OPEN_WORK" "$PEOPLE_DIR" <<'PYEOF'
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("S1|SKIP|PyYAML not installed — cannot parse YAML")
    print("S2|SKIP|PyYAML not installed — cannot parse YAML")
    print("S3|SKIP|PyYAML not installed — cannot parse YAML")
    sys.exit(0)

asset_list_path, board_path, open_work_path, people_dir = (
    Path(p) for p in sys.argv[1:5]
)


def load_yaml(path):
    """Returns (data, found, error). found=False means file absent.
    error is set (data=None) when the file exists but fails to parse —
    a corrupt input must never silently read as zero orphans."""
    if not path.exists():
        return None, False, None
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - report, don't crash the run
        return None, True, str(exc)
    return data, True, None


def ref_ids(item):
    """Candidate id(s) a board/work item could be identified by."""
    ids = set()
    if isinstance(item, dict):
        for key in ("asset_id", "id", "work_id", "item_id"):
            v = item.get(key)
            if v:
                ids.add(str(v))
    elif item is not None:
        ids.add(str(item))
    return ids


asset_data, asset_found, asset_err = load_yaml(asset_list_path)
board_data, board_found, board_err = load_yaml(board_path)
work_data, work_found, work_err = load_yaml(open_work_path)

assets = []
if asset_found and not asset_err and isinstance(asset_data, dict):
    assets = asset_data.get("assets") or []

board_items = []
if board_found and not board_err and isinstance(board_data, dict):
    for col in (board_data.get("columns") or []):
        if isinstance(col, dict):
            board_items.extend(col.get("items") or [])

work_items = []
if work_found and not work_err and isinstance(work_data, dict):
    work_items = work_data.get("items") or []

asset_ids = {
    str(a["asset_id"]) for a in assets if isinstance(a, dict) and a.get("asset_id")
}
work_ids = {
    str(i["id"]) for i in work_items if isinstance(i, dict) and i.get("id")
}

# ---------------------------------------------------------------- Surface 1
if asset_err:
    print(f"S1|SKIP|{asset_list_path}: parse error — {asset_err}")
elif not asset_found:
    print(f"S1|SKIP|{asset_list_path} not found")
elif not isinstance(asset_data, dict):
    print(f"S1|ORPHAN|{asset_list_path}: malformed document (expected a mapping)")
elif not assets:
    print("S1|OK|no assets declared (asset list empty)")
else:
    referenced = set()
    for item in board_items:
        referenced |= ref_ids(item)
    for item in work_items:
        referenced |= ref_ids(item)
    n_orphans = 0
    for a in assets:
        if not isinstance(a, dict):
            print(f"S1|ORPHAN|malformed asset entry: {a!r}")
            n_orphans += 1
            continue
        aid = a.get("asset_id")
        if not aid:
            print(f"S1|ORPHAN|asset entry missing asset_id: {a!r}")
            n_orphans += 1
            continue
        if str(aid) not in referenced:
            print(
                f"S1|ORPHAN|asset_id '{aid}' is not referenced by any "
                f"board_snapshot or open_work_snapshot item"
            )
            n_orphans += 1
    if n_orphans == 0:
        print(f"S1|OK|all {len(assets)} asset(s) referenced")

# ---------------------------------------------------------------- Surface 2
if board_err:
    print(f"S2|SKIP|{board_path}: parse error — {board_err}")
elif not board_found:
    print(f"S2|SKIP|{board_path} not found")
elif not isinstance(board_data, dict):
    print(f"S2|ORPHAN|{board_path}: malformed document (expected a mapping)")
elif not board_items:
    print("S2|OK|no board items (board snapshot empty)")
else:
    known = asset_ids | work_ids
    n_orphans = 0
    for item in board_items:
        ids = ref_ids(item)
        if not ids or not (ids & known):
            print(
                f"S2|ORPHAN|board item {item!r} does not trace back to a "
                f"known asset_id or open-work id"
            )
            n_orphans += 1
    if n_orphans == 0:
        print(f"S2|OK|all {len(board_items)} board item(s) trace back")

# ---------------------------------------------------------------- Surface 3
if work_err:
    print(f"S3|SKIP|{open_work_path}: parse error — {work_err}")
elif not work_found:
    print(f"S3|SKIP|{open_work_path} not found")
elif not isinstance(work_data, dict):
    print(f"S3|ORPHAN|{open_work_path}: malformed document (expected a mapping)")
elif not work_items:
    print("S3|OK|no open work items (open work empty)")
else:
    people_dir_found = people_dir.is_dir()
    people_ids = set()
    if people_dir_found:
        for f in sorted(people_dir.glob("*.yaml")):
            if f.name.startswith("_"):
                continue
            try:
                d = yaml.safe_load(f.read_text(encoding="utf-8"))
            except Exception:
                continue
            if isinstance(d, dict) and d.get("id"):
                people_ids.add(str(d["id"]))
            else:
                people_ids.add(f.stem)
    n_orphans = 0
    for item in work_items:
        if not isinstance(item, dict):
            print(f"S3|ORPHAN|malformed work item: {item!r}")
            n_orphans += 1
            continue
        item_id = item.get("id", "?")
        owner = item.get("assignee") or item.get("owner")
        if not owner:
            print(f"S3|ORPHAN|work item '{item_id}' has no owner (assignee)")
            n_orphans += 1
        elif people_dir_found and str(owner) not in people_ids:
            print(
                f"S3|ORPHAN|work item '{item_id}' owner '{owner}' not found "
                f"in registries/people/"
            )
            n_orphans += 1
        elif not people_dir_found:
            print(
                f"S3|SKIP|work item '{item_id}' owner '{owner}' set but "
                f"{people_dir} not found — cannot verify"
            )
    if n_orphans == 0:
        print(f"S3|OK|all {len(work_items)} open work item(s) have a valid owner")
PYEOF
)"

ORPHANS=0
S1_LINES=0
S2_LINES=0
S3_LINES=0

echo "-- Surface 1: asset_list --"
while IFS='|' read -r SURFACE LEVEL MSG; do
  [[ -z "$SURFACE" ]] && continue
  [[ "$SURFACE" != "S1" ]] && continue
  S1_LINES=$((S1_LINES + 1))
  if [[ "$LEVEL" == "ORPHAN" ]]; then
    printf '  ORPHAN: %s\n' "$MSG"
    ORPHANS=$((ORPHANS + 1))
  else
    printf '  %s: %s\n' "$LEVEL" "$MSG"
  fi
done <<< "$PYOUT"
[[ "$S1_LINES" -eq 0 ]] && echo "  (no output)"

echo ""
echo "-- Surface 2: board_snapshot --"
while IFS='|' read -r SURFACE LEVEL MSG; do
  [[ -z "$SURFACE" ]] && continue
  [[ "$SURFACE" != "S2" ]] && continue
  S2_LINES=$((S2_LINES + 1))
  if [[ "$LEVEL" == "ORPHAN" ]]; then
    printf '  ORPHAN: %s\n' "$MSG"
    ORPHANS=$((ORPHANS + 1))
  else
    printf '  %s: %s\n' "$LEVEL" "$MSG"
  fi
done <<< "$PYOUT"
[[ "$S2_LINES" -eq 0 ]] && echo "  (no output)"

echo ""
echo "-- Surface 3: open_work_snapshot --"
while IFS='|' read -r SURFACE LEVEL MSG; do
  [[ -z "$SURFACE" ]] && continue
  [[ "$SURFACE" != "S3" ]] && continue
  S3_LINES=$((S3_LINES + 1))
  if [[ "$LEVEL" == "ORPHAN" ]]; then
    printf '  ORPHAN: %s\n' "$MSG"
    ORPHANS=$((ORPHANS + 1))
  else
    printf '  %s: %s\n' "$LEVEL" "$MSG"
  fi
done <<< "$PYOUT"
[[ "$S3_LINES" -eq 0 ]] && echo "  (no output)"

echo ""
echo "Orphan detection: ${ORPHANS} orphans found"
[[ "$ORPHANS" -eq 0 ]]
