#!/usr/bin/env bash
# access/secrets/gate/phase2-gate.sh
# The L5 phase 2 exit gate. One command, every check this phase produced.
# Writes access/secrets/gate/phase2.gate.json - deterministic, no timestamp,
# so a re-run produces no diff.
#
#   exit 0  L5-P2 EXIT GATE PASS
#   exit 1  one or more gates failed
set -u
FAILURES=0
RESULTS=""

run () {  # run <id> <command...>
  id="$1"; shift
  if "$@" >/dev/null 2>&1; then
    echo "GATE $id PASS"
    RESULTS="$RESULTS{\"id\":\"$id\",\"status\":\"pass\"},"
  else
    echo "GATE $id FAIL"
    RESULTS="$RESULTS{\"id\":\"$id\",\"status\":\"fail\"},"
    FAILURES=$((FAILURES + 1))
  fi
}

T=access/secrets/testdata
run G01-tier-registry        python access/secrets/tools/validate_tiers.py
run G02-downward-move        bash access/secrets/checks/check-no-downward-move.sh
run G03-fifth-tier-entries   python access/secrets/tools/emit_fifth_tier.py
run G04-envelopes            python access/secrets/tools/emit_envelopes.py
run G05-envelope-evaluator   python access/secrets/envelope/evaluate_envelope.py "$T/envelope/envelopes" "$T/envelope/runs-clean" "$T/envelope/triggers"
run G06-rotation-runbook     bash access/secrets/runbooks/check-runbook.sh
run G07-rotation-gate        bash access/secrets/checks/rotation-complete.sh "$T/rotation/complete.yaml"
run G08-boundaries           bash access/secrets/boundaries/check-boundaries.sh --phase complete
run G09-separation           bash access/secrets/separation/check-separation.sh
run G10-no-api-keys          python access/secrets/checks/no_api_keys.py --profiles "$T/no-api-keys/clean/profile.sh" --scan-root "$T/no-api-keys/clean" --skip-env
run G11-containment          bash access/secrets/incident/check-containment.sh
run G12-publication          python access/secrets/tools/publish_secret_tiers.py --check
run G13-generated-clean      git diff --exit-code -- access/secrets/fifth-tier access/secrets/envelope access/published

printf '{\n  "artifact": "l5-p2-exit-gate",\n  "gates": [%s],\n  "failures": %d\n}\n' \
  "${RESULTS%,}" "$FAILURES" > access/secrets/gate/phase2.gate.json

echo "GATE-FAILURES $FAILURES"
if [ "$FAILURES" -eq 0 ]; then
  echo "L5-P2 EXIT GATE PASS"
  exit 0
fi
echo "L5-P2 EXIT GATE FAIL"
exit 1
