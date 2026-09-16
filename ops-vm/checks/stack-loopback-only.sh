#!/usr/bin/env bash
# Every published stack port is on 127.0.0.1 (Section 51.4).
set -euo pipefail
bad=$(grep -oE '"[0-9.:]+:[0-9]+:[0-9]+"' ops-vm/stack/compose.shared.yml | grep -v '"127\.0\.0\.1:' || true)
if [ -n "$bad" ]; then echo "STACK-LOOPBACK: FAIL"; echo "$bad"; exit 1; fi
echo "STACK-LOOPBACK: PASS"
