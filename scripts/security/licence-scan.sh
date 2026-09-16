#!/usr/bin/env bash
# licence-scan.sh — Python dependency licence inventory & policy scanner (FD-107/PFD-027)
# Usage: bash scripts/security/licence-scan.sh [--product <id>] [--outdir <dir>]
#        [--fail-on "<comma-separated licences>"] [--allow-only "<comma-separated licences>"]
#
# NOTE: FD-107 (2026-09-08) decided the security/SBOM toolchain is Trivy
# (image + dependency scan, sha256-pinned) + Syft (SBOM, spdx-json).
# PFD-027 was titled "Security, Licence, and SBOM Scanner Tool Selection"
# but FD-107's recorded answer only resolves the security/SBOM half — no
# FD/PFD in this repo names a licence-checker tool or a disallowed-licence
# policy. Per the lane charter (lanes/L0-00-charter.md §6.2, row C-10) a
# tool not already named in the spec, and any policy content, are L0-only
# decisions an execution lane may not make on its own.
#
# So this script does the part that is not a policy call: it runs a real
# scan of the installed Python dependency set with pip-licenses and writes
# a genuine licence inventory (JSON) to records/licences/. It never
# hard-codes a disallowed-licence list — consistent with the analogous
# licence-scan job the CI templates already spec out (lanes/L2-05-tasks.md,
# task L2-T104, acceptance criterion 3: "No licence class list is
# hard-coded in the workflow file"). Pass --fail-on / --allow-only
# (forwarded verbatim to pip-licenses — see its --help for exact licence-
# name spelling) once L0 has decided the policy; until then the job
# produces an inventory only and exits 0.
set -euo pipefail

PRODUCT="all"
OUTDIR="records/licences"
FAIL_ON=""
ALLOW_ONLY=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --product) PRODUCT="$2"; shift 2;;
    --outdir) OUTDIR="$2"; shift 2;;
    --fail-on) FAIL_ON="$2"; shift 2;;
    --allow-only) ALLOW_ONLY="$2"; shift 2;;
    *) shift;;
  esac
done

echo "=== Licence Scan: $PRODUCT ==="
echo "DECIDED (FD-107, 2026-09-08): security/SBOM toolchain is Trivy + Syft."
echo "No FD/PFD names a licence-checker tool or a disallowed-licence policy;"
echo "per lanes/L0-00-charter.md C-10 both are L0-only decisions. This"
echo "script runs a real pip-licenses inventory and enforces a policy only"
echo "when one is explicitly supplied via --fail-on/--allow-only."
echo ""

if ! command -v pip-licenses &>/dev/null; then
  echo "No licence scanner (pip-licenses) found on PATH." >&2
  echo "Install it to enable real scanning:" >&2
  echo "  pip install -r requirements-dev.txt   (includes pip-licenses)" >&2
  echo "" >&2
  echo "Failing closed: cannot verify Python dependency licences without a" >&2
  echo "scanner installed." >&2
  exit 1
fi

mkdir -p "$OUTDIR"
JSON_OUT="$OUTDIR/${PRODUCT}.licences.json"
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

echo "Running pip-licenses against the installed environment..."
pip-licenses --format=json --with-authors --with-urls --with-description --order=license > "$JSON_OUT"
echo "Inventory written: $JSON_OUT ($TIMESTAMP)"
echo ""
echo "Summary:"
pip-licenses --order=license --summary

if [[ -z "$FAIL_ON" && -z "$ALLOW_ONLY" ]]; then
  echo ""
  echo "No --fail-on/--allow-only supplied: inventory-only mode, exiting 0."
  echo "Findings are printed above for manual/technical-debt review; no"
  echo "disallowed-licence policy has been decided by L0 to enforce here."
  exit 0
fi

echo ""
echo "Applying supplied licence policy..."
POLICY_ARGS=()
[[ -n "$FAIL_ON" ]] && POLICY_ARGS+=(--fail-on "$FAIL_ON")
[[ -n "$ALLOW_ONLY" ]] && POLICY_ARGS+=(--allow-only "$ALLOW_ONLY")

set +e
pip-licenses "${POLICY_ARGS[@]}" >/dev/null
rc=$?
set -e

if [[ $rc -ne 0 ]]; then
  echo "Licence scan FAILED: one or more packages violate the supplied policy (exit ${rc})." >&2
  exit "$rc"
fi

echo "Licence scan passed: all packages satisfy the supplied policy."
exit 0
