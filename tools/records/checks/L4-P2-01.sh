#!/usr/bin/env bash
set -eu
# Check: L4-P2-01 — check.sh is byte-identical to L4-06-tasks.md sec 0.6,
# and CONTRACT.md transcribes sec 0.5. This is transcription, not design
# (see implementation/_RESIDUE.md item 1).
HERE="$(cd "$(dirname "$0")" && pwd)"
CP_DIR="$(cd "$HERE/../../.." && pwd)"

EXPECTED="$(mktemp)"
trap 'rm -f "$EXPECTED"' EXIT
cat > "$EXPECTED" <<'SPEC'
#!/usr/bin/env bash
set -eu
# check.sh — dispatch a per-task check file.
# Normal:  check.sh <TASK-ID>           runs checks/<TASK-ID>.sh
# Audit:   check.sh --audit <TASK-ID>   validates minimum check-file requirements
#                                        before running; the phase-exit gate uses this mode.
AUDIT=0
if [ "${1:-}" = "--audit" ]; then AUDIT=1; shift; fi
T="${1:?usage: check.sh [--audit] <TASK-ID>}"
D="$(cd "$(dirname "$0")" && pwd)"
F="$D/checks/${T}.sh"
if [ ! -f "$F" ]; then echo "CHECK ${T} ERROR no-check-file"; exit 3; fi
if [ "$AUDIT" -eq 1 ]; then
  LINES="$(wc -l < "$F")"
  if [ "$LINES" -lt 10 ]; then
    echo "CHECK ${T} ERROR audit-too-short lines=${LINES} min=10"; exit 3
  fi
  if ! grep -qE '(grep[[:space:]]|\[[[:space:]].*[=!]|[[:space:]]-eq[[:space:]]|[[:space:]]-ne[[:space:]])' "$F"; then
    echo "CHECK ${T} ERROR audit-no-assertion"; exit 3
  fi
  if ! grep -qiE '(negative|fixture.*fail|bad_fixture|neg_fixture|# neg)' "$F"; then
    echo "CHECK ${T} ERROR audit-no-negative-fixture"; exit 3
  fi
fi
if bash "$F" >/dev/null 2>&1; then echo "CHECK ${T} PASS"; exit 0; fi
echo "CHECK ${T} FAIL"; exit 1
SPEC

# --- Assertion 1: check.sh is byte-identical to the section 0.6 verbatim script ---
if ! diff -q "$EXPECTED" "$CP_DIR/tools/records/check.sh" >/dev/null 2>&1; then
  echo "L4-P2-01: check.sh is not byte-identical to L4-06-tasks.md sec 0.6" >&2
  diff -u "$EXPECTED" "$CP_DIR/tools/records/check.sh" >&2 || true
  exit 1
fi

# --- Assertion 2: CONTRACT.md exists and transcribes the sec 0.5 OK/FAIL/ERROR grammar ---
CONTRACT="$CP_DIR/tools/records/CONTRACT.md"
if [ ! -f "$CONTRACT" ]; then
  echo "L4-P2-01: CONTRACT.md is missing" >&2
  exit 1
fi
for TOKEN in '<NAME> OK <counters>' '<NAME> FAIL <counters>' '<NAME> ERROR <reason>' 'exit 0' 'exit 1' 'exit 3'; do
  if ! grep -qF "$TOKEN" "$CONTRACT"; then
    echo "L4-P2-01: CONTRACT.md missing required token: $TOKEN" >&2
    exit 1
  fi
done

# --- Assertion 3 (negative fixture): an unknown task id must ERROR no-check-file, exit 3 ---
# neg_fixture: this id is guaranteed to have no checks/<id>.sh file on disk.
BAD_FIXTURE="ZZZ-NEG-FIXTURE-DOES-NOT-EXIST"
if [ -f "$CP_DIR/tools/records/checks/${BAD_FIXTURE}.sh" ]; then
  echo "L4-P2-01: negative fixture id collides with a real check file" >&2
  exit 1
fi
set +e
OUT="$(bash "$CP_DIR/tools/records/check.sh" "$BAD_FIXTURE" 2>&1)"
RC=$?
set -e
if [ "$RC" -ne 3 ]; then
  echo "L4-P2-01: bad_fixture case exited $RC, expected 3" >&2
  echo "$OUT" >&2
  exit 1
fi
if [ "$OUT" != "CHECK ${BAD_FIXTURE} ERROR no-check-file" ]; then
  echo "L4-P2-01: bad_fixture case printed unexpected output: $OUT" >&2
  exit 1
fi

echo "CHECK L4-P2-01 PASS"
