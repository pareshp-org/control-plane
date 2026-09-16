#!/usr/bin/env bash
# vuln-scan.sh — Python dependency vulnerability scanner (FD-107/PFD-027)
# Usage: bash scripts/security/vuln-scan.sh
#
# NOTE: FD-107 (2026-09-08) decided the *primary* security/SBOM toolchain is
# Trivy (image + dependency scan, sha256-pinned) + Syft (SBOM, spdx-json).
# Trivy wiring is still blocked pending L0 supplying the container image
# digest (PFD-027 Option A) — that part of this stub is NOT yet real.
#
# This script covers the Python-dependency slice on its own: it runs a real
# scan of requirements.txt with pip-audit (preferred) or safety, and fails
# the build (non-zero exit) when either tool reports an actual
# vulnerability. It only falls back to a "nothing to do" message when
# neither scanner is installed.
set -euo pipefail

REQ_FILE="${1:-requirements.txt}"

echo "=== Vulnerability Scan (Python dependencies) ==="
echo "DECIDED (FD-107, 2026-09-08): Trivy — two jobs (image scan + dependency"
echo "scan), sha256-pinned. Not yet wired: digest pinning is still open"
echo "pending L0 supplying the container digest (PFD-027 Option A)."
echo "This script covers the Python-dependency slice via pip-audit/safety."
echo ""

if [ ! -f "${REQ_FILE}" ]; then
  echo "ERROR: requirements file not found: ${REQ_FILE}" >&2
  exit 1
fi

run_scan() {
  # Runs with set -e temporarily relaxed so a non-zero (vulnerabilities
  # found) exit from the scanner doesn't abort the script before we can
  # inspect and propagate it.
  set +e
  "$@"
  local rc=$?
  set -e
  return "${rc}"
}

if command -v pip-audit &>/dev/null; then
  echo "Running pip-audit (primary scanner) against ${REQ_FILE}..."
  run_scan pip-audit -r "${REQ_FILE}"
  rc=$?
  echo ""
  if [ "${rc}" -ne 0 ]; then
    echo "pip-audit found one or more known vulnerabilities (exit ${rc})."
    exit "${rc}"
  fi
  echo "pip-audit: no known vulnerabilities found."

elif command -v safety &>/dev/null; then
  echo "pip-audit not found on PATH; falling back to safety..."
  run_scan safety check -r "${REQ_FILE}"
  rc=$?
  echo ""
  if [ "${rc}" -ne 0 ]; then
    echo "safety found one or more known vulnerabilities (exit ${rc})."
    exit "${rc}"
  fi
  echo "safety: no known vulnerabilities found."

else
  echo "No vulnerability scanner (pip-audit or safety) found on PATH."
  echo "Install one to enable real scanning:"
  echo "  pip install pip-audit   (preferred — PyPI-native, actively maintained)"
  echo "  pip install safety      (fallback)"
  echo ""
  echo "Failing closed: cannot verify Python dependencies are vulnerability-free"
  echo "without a scanner installed."
  exit 1
fi

echo ""
echo "Vulnerability scan passed: no known vulnerabilities detected."
exit 0
