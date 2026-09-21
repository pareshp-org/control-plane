#!/usr/bin/env bash
# infra/network/check-shell-gate.sh
# The HOST-SIDE half of boundary 2, enforcement E2 (Section 40.3 line 3703).
# Run ON the operations VM, or over ssh:
#   ssh <ops-vm> 'bash -s' < infra/network/check-shell-gate.sh
#
#   exit 0  the shell gate holds
#   exit 1  an assertion fails
#   exit 2  sshd cannot be inspected - FAIL CLOSED (blocker class host-unreachable)
set -u
FAIL=0
CFG=$(sshd -T 2>/dev/null)
if [ -z "$CFG" ]; then
  echo "GATE-CHECK G0 FAIL sshd -T produced nothing"
  echo "RESULT FAIL"
  exit 2
fi
want () {  # want <key> <value> <id>
  got=$(printf '%s\n' "$CFG" | awk -v k="$1" '$1==k {print $2; exit}')
  if [ "$got" = "$2" ]; then
    echo "GATE-CHECK $3 OK $1=$got"
  else
    echo "GATE-CHECK $3 FAIL $1=$got expected=$2"
    FAIL=1
  fi
}
want passwordauthentication no G1
want kbdinteractiveauthentication no G2
want permitrootlogin no G3
want pubkeyauthentication yes G4

# Every authorized key on the host is hardware-backed, and none waives touch.
KEYS=$(cat /home/*/.ssh/authorized_keys /root/.ssh/authorized_keys 2>/dev/null | grep -v '^#' | grep -v '^$' || true)
TOTAL=$(printf '%s\n' "$KEYS" | grep -c . || true)
SK=$(printf '%s\n' "$KEYS" | grep -c 'sk-ssh-ed25519@openssh.com\|sk-ecdsa-sha2-nistp256@openssh.com' || true)
NOTOUCH=$(printf '%s\n' "$KEYS" | grep -c 'no-touch-required' || true)
if [ "$TOTAL" = "0" ]; then
  echo "GATE-CHECK G5 FAIL no authorized keys found to inspect"
  FAIL=1
elif [ "$TOTAL" = "$SK" ]; then
  echo "GATE-CHECK G5 OK all $TOTAL authorized keys are hardware-backed"
else
  echo "GATE-CHECK G5 FAIL $((TOTAL - SK)) of $TOTAL authorized keys are not hardware-backed"
  FAIL=1
fi
if [ "$NOTOUCH" = "0" ]; then
  echo "GATE-CHECK G6 OK no-touch-required absent"
else
  echo "GATE-CHECK G6 FAIL $NOTOUCH keys waive the touch requirement"
  FAIL=1
fi

# The gate sits ON TOP OF the private path; the host must not answer publicly.
PUB=$(ss -lntp 2>/dev/null | awk '$4 ~ /(^0\.0\.0\.0:22$|^\[::\]:22$)/' | wc -l | tr -d ' ')
if [ "$PUB" = "0" ]; then
  echo "GATE-CHECK G7 OK sshd is not bound to a wildcard address"
else
  echo "GATE-CHECK G7 FAIL sshd answers on a wildcard address; the private path of Section 51.4 is not in front of it"
  FAIL=1
fi

echo "GATE-FAILURES $FAIL"
if [ "$FAIL" -eq 0 ]; then echo "RESULT PASS"; exit 0; else echo "RESULT FAIL"; exit 1; fi
