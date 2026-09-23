#!/usr/bin/env bash
# Periodic reconciliation daemon and metrics publisher (Section 53.1, Subsystem M)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OPS_VM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CONTROL_PLANE_ROOT="$(cd "$OPS_VM_DIR/.." && pwd)"

# Source common ops-vm library if present
if [ -f "$OPS_VM_DIR/lib/common.sh" ]; then
  . "$OPS_VM_DIR/lib/common.sh"
fi

# Ensure control-plane is on PYTHONPATH
export PYTHONPATH="$CONTROL_PLANE_ROOT${PYTHONPATH:+:$PYTHONPATH}"

# Detect Python 3
PYTHON="${PYTHON:-}"
if [ -z "$PYTHON" ]; then
  if command -v python3 >/dev/null 2>&1; then
    PYTHON="python3"
  elif command -v python >/dev/null 2>&1; then
    PYTHON="python"
  else
    echo "run-reconcile: FAIL-CLOSED: no python interpreter found" >&2
    exit 3
  fi
fi

# Target metric file
PROM_DIR="${RECONCILER_PROM_DIR:-/var/lib/prometheus/node-exporter}"
PROM_FILE="${RECONCILER_PROM_FILE:-$PROM_DIR/reconciler.prom}"
export RECONCILER_PROM_DIR="$PROM_DIR"
export RECONCILER_PROM_FILE="$PROM_FILE"

# Execute publisher
set +e
"$PYTHON" "$SCRIPT_DIR/reconcile_publisher.py" "$@"
rc=$?
set -e

# Record run per Section 53.1 / Invariant 47
if command -v record_run >/dev/null 2>&1; then
  if [ "$rc" -eq 0 ]; then
    record_run reconcile ok "status=clean exit=0" || true
  elif [ "$rc" -eq 2 ]; then
    record_run reconcile ok "status=blocking_drift exit=2" || true
  else
    record_run reconcile failed "status=failed exit=$rc" || true
  fi
fi

# If failed (exit 3 or crash) and notifier configured, notify
if [ "$rc" -ne 0 ] && [ "$rc" -ne 2 ]; then
  NOTIFIER="$CONTROL_PLANE_ROOT/notify/bin/notify-job-result.sh"
  NOTIFY_ENV="${NOTIFY_ENV_FILE:-$CONTROL_PLANE_ROOT/notify/bin/notify.env}"
  if [ -x "$NOTIFIER" ] && [ -f "$NOTIFY_ENV" ]; then
    "$NOTIFIER" reconcile failed "rc=$rc" || true
  fi
fi

exit "$rc"
