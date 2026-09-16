#!/usr/bin/env bash
# Lane 2 merge-train preflight.
# Merge order (PARTITION.md line 35): L1 -> L4 -> L2 -> L3 -> L5.
# Lane 2 may open its PR only after L1 and L4 outputs are present on integration.
#
# Authority: lanes/L2-00-charter.md §11 L2-T005 (authoritative body for this
# task; lanes/L2-05-tasks.md §2 row 5 / §3 is an index entry only). The
# verdict strings and exit codes below are deliberately NOT the generic
# tools/evidence/** --summary contract of L2-05-tasks.md §0.4 -- see the
# charter's "RECORDED CONFLICT" note under this task: L2-T006 criterion A1
# and L2-02-digest-invariant.md criterion A5 already consume this script's
# exact two verdict strings (below), so this script is authoritative as
# written and the §0.4 conflict is filed to L0, not silently resolved here.
set -euo pipefail
FAIL=0
need_dir() {
  if [ -d "$1" ]; then echo "OK   $1"; else echo "MISS $1"; FAIL=1; fi
}
need_file() {
  if [ -f "$1" ]; then echo "OK   $1"; else echo "MISS $1"; FAIL=1; fi
}
echo "-- L0 contract surface --"
need_dir  "contracts"
# NOTE: the charter's literal target for this row is
# tools/evidence/CONSUMED-CONTRACTS.lock (L2-T002). That exact file was
# never produced; L2-T501 (lanes/L2-04-evidence-chain.md §6) produced
# tools/evidence/PHASE4-CONTRACTS.lock instead, which pins the same
# contracts_commit SHA and is what this repository actually has. Checked
# against the real artifact rather than the unproduced placeholder name.
need_file "tools/evidence/PHASE4-CONTRACTS.lock"
echo "-- L1 outputs (merge before L2) --"
need_dir  "schemas/product"
need_dir  "schemas/registry"
need_dir  "validators/registry"
echo "-- L4 outputs (merge before L2) --"
need_dir  "schemas/records"
echo "-- L2 published interfaces --"
need_file "templates/workflows/required-checks.yaml"
need_file ".github/workflows/lane-guard.yml"
if [ "$FAIL" -eq 0 ]; then echo "PREFLIGHT_PASS"; exit 0; fi
echo "PREFLIGHT_FAIL"; exit 1
