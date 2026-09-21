#!/usr/bin/env bash
# ops-vm/layer-b/session/render-session-ini.sh
# Writes the two frozen contract values into the [auth] block of the Layer B-M
# grafana.ini. Idempotent: running it twice produces the same file.
# It never invents a duration. A missing contract value is a hard stop.
set -euo pipefail
CONTRACT="contracts/access/access-inputs.yaml"
INI="ops-vm/layer-b/grafana.ini"
if [ ! -f "$CONTRACT" ]; then
  echo "CONTRACT_MISSING $CONTRACT (L0 Phase-0 frozen input not yet published)"
  exit 2
fi
[ -f "$INI" ] || { echo "INI_MISSING"; exit 2; }

MAXLIFE=$(yq -r '.layer_b.session.max_lifetime_duration // ""' "$CONTRACT")
MAXIDLE=$(yq -r '.layer_b.session.max_inactive_lifetime_duration // ""' "$CONTRACT")
[ -n "$MAXLIFE" ] || { echo "CONTRACT_VALUE_MISSING layer_b.session.max_lifetime_duration"; exit 2; }
[ -n "$MAXIDLE" ] || { echo "CONTRACT_VALUE_MISSING layer_b.session.max_inactive_lifetime_duration"; exit 2; }

python3 - "$INI" "$MAXLIFE" "$MAXIDLE" <<'PY'
import sys
path, maxlife, maxidle = sys.argv[1], sys.argv[2], sys.argv[3]
lines = open(path, encoding="utf-8").read().split("\n")
out, in_auth = [], False
for line in lines:
    s = line.strip()
    if s.startswith("[") and s.endswith("]"):
        in_auth = (s == "[auth]")
        out.append(line); continue
    if in_auth and s.split("=")[0].strip() == "login_maximum_lifetime_duration":
        out.append("login_maximum_lifetime_duration = " + maxlife); continue
    if in_auth and s.split("=")[0].strip() == "login_maximum_inactive_lifetime_duration":
        out.append("login_maximum_inactive_lifetime_duration = " + maxidle); continue
    out.append(line)
open(path, "w", encoding="utf-8").write("\n".join(out))
PY
echo "SESSION_INI_RENDERED $MAXLIFE $MAXIDLE"
