#!/usr/bin/env bash
# D89: the Renovate auto-merge bypass is split across two repository rulesets and
# lives in the repository's protection configuration. The operations VM never
# carries a ruleset, a bypass actor or a fleet-wide auto-merge default.
set -euo pipefail
bad=$(for f in ops-vm/renovate/*; do
        sed 's|//.*||' "$f" | grep -En 'bypass|ruleset|automerge: *true' | sed "s|^|$f:|" || true
      done)
if [ -n "$bad" ]; then echo "RENOVATE-NO-BYPASS: FAIL"; echo "$bad"; exit 1; fi
echo "RENOVATE-NO-BYPASS: PASS"
