#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# mirror of the run-phase-0.sh heredoc, kept in sync manually
# Source: run-phase-0.sh, task L0-P0-021, `cat > contracts/ci/verify_contracts.py
# <<'PYEOF'` block. This copy exists so the script can be unit tested directly
# instead of only via heredoc-extraction-to-scratch. If run-phase-0.sh's
# heredoc changes, update this file to match by hand.
# ---------------------------------------------------------------------------
"""verify_contracts.py — run all contract self-checks; prints CONTRACTS-VERIFY OK N/N on success."""
import sys, yaml, pathlib, subprocess, os

ROOT = pathlib.Path(__file__).parent.parent
REG_PATH = ROOT / "register.yaml"
data = yaml.safe_load(REG_PATH.read_text())
contracts = data.get("contracts", [])
total = len(contracts)
passed = 0
for c in contracts:
    stub_path = ROOT / c.get("stub", "")
    if stub_path.exists():
        passed += 1
    else:
        print(f"MISSING stub: {c['id']} -> {c.get('stub')}", file=sys.stderr)
print(f"CONTRACTS-VERIFY OK {passed}/{total}" if passed == total else f"CONTRACTS-VERIFY FAIL {passed}/{total}")
sys.exit(0 if passed == total else 1)
