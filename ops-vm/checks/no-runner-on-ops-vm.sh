#!/usr/bin/env bash
# Host side of RUNNER-PLACEMENT-1 (Section 49.1): this VM runs no CI runner.
# Section 45.2's "CI keeps running when the VM is lost" depends on it.
set -euo pipefail
bad=0
if systemctl list-units --type=service --all --no-legend 2>/dev/null \
   | grep -Eq 'actions\.runner|github-runner'; then
  echo "a GitHub Actions runner service is installed on the operations VM"; bad=1
fi
if [ -d /opt/actions-runner ] || [ -d /home/runner/actions-runner ]; then
  echo "a runner installation directory exists on the operations VM"; bad=1
fi
if [ "$bad" -eq 0 ]; then echo "NO-RUNNER-ON-OPS-VM: PASS"; else echo "NO-RUNNER-ON-OPS-VM: FAIL"; exit 1; fi
