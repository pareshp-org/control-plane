#!/usr/bin/env bash
# access/secrets/checks/no-api-keys.sh
# The onboarding and quarterly run (Section 40.2 line 3691, Section 36.6,
# Section 98.2 Phase 1 line 9015, invariant 84).
# Profile paths come from the contract; this wrapper never hard-codes one.
#   exit 0  clean
#   exit 1  an API key is present somewhere it must not be
#   exit 2  a named profile could not be read - FAIL CLOSED
set -eu
PROFILES=$(python -c "import yaml;c=yaml.safe_load(open('contracts/access/access-inputs.yaml',encoding='utf-8'));print(','.join(((c.get('checks') or {}).get('api_key_free') or {}).get('shell_profile_paths') or []))")
python access/secrets/checks/no_api_keys.py --profiles "$PROFILES" --scan-root "${1:-.}"
