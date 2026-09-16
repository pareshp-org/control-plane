#!/usr/bin/env bash
# access/secrets/host/check-credential-store.sh
# The HOST-SIDE half of boundary 2, enforcement E1 (Section 40.3 line 3703).
# Run ON the operations VM, or over ssh:
#   ssh <ops-vm> 'bash -s' < access/secrets/host/check-credential-store.sh
#
#   exit 0  every host assertion holds
#   exit 1  an assertion fails
#   exit 2  the host cannot be inspected - FAIL CLOSED (blocker class host-unreachable)
set -u
STORE=/var/lib/ops-vm/creds
USER_EXPECTED=cp-creds
FAIL=0

if [ ! -d "$STORE" ]; then
  echo "HOST-CHECK H1 FAIL store directory $STORE absent"
  echo "RESULT FAIL"
  exit 2
fi

OWNER=$(stat -c '%U' "$STORE" 2>/dev/null || echo UNKNOWN)
MODE=$(stat -c '%a' "$STORE" 2>/dev/null || echo UNKNOWN)
if [ "$OWNER" = "$USER_EXPECTED" ]; then echo "HOST-CHECK H1 OK owner=$OWNER"; else echo "HOST-CHECK H1 FAIL owner=$OWNER expected=$USER_EXPECTED"; FAIL=1; fi
if [ "$MODE" = "700" ]; then echo "HOST-CHECK H2 OK mode=$MODE"; else echo "HOST-CHECK H2 FAIL mode=$MODE expected=700"; FAIL=1; fi

LOOSE=$(find "$STORE" -type f ! -perm 600 2>/dev/null | wc -l | tr -d ' ')
if [ "$LOOSE" = "0" ]; then echo "HOST-CHECK H3 OK no-loose-modes"; else echo "HOST-CHECK H3 FAIL $LOOSE files not mode 600"; FAIL=1; fi

# The credential reaches the service through systemd credentials, not through a
# file the service unit cats in an ExecStart line.
UNITS=$(systemctl list-units --type=service --all --no-legend 2>/dev/null | awk '{print $1}' | grep -c '^reconcile-' || true)
CREDS=$(systemctl cat 'reconcile-*.service' 2>/dev/null | grep -c -E 'LoadCredential=|SetCredential=' || true)
if [ "$UNITS" = "0" ]; then
  echo "HOST-CHECK H4 FAIL no reconcile-* service units on this host"
  FAIL=1
elif [ "$CREDS" -ge 1 ]; then
  echo "HOST-CHECK H4 OK systemd-credential-delivery"
else
  echo "HOST-CHECK H4 FAIL no LoadCredential=/SetCredential= in reconcile-* units"
  FAIL=1
fi

# No credential value in the system manager environment.
ENVHITS=$(systemctl show-environment 2>/dev/null | grep -c -i -E 'token|secret|api_key|password' || true)
if [ "$ENVHITS" = "0" ]; then echo "HOST-CHECK H5 OK clean-manager-environment"; else echo "HOST-CHECK H5 FAIL $ENVHITS credential-shaped entries in the manager environment"; FAIL=1; fi

# The store path is audited, and the audit leaves the host.
AUDIT=$(auditctl -l 2>/dev/null | grep -c "$STORE" || true)
if [ "$AUDIT" -ge 1 ]; then echo "HOST-CHECK H6 OK store-path-audited"; else echo "HOST-CHECK H6 FAIL no audit rule on $STORE"; FAIL=1; fi

echo "HOST-FAILURES $FAIL"
if [ "$FAIL" -eq 0 ]; then echo "RESULT PASS"; exit 0; else echo "RESULT FAIL"; exit 1; fi
