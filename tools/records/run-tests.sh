#!/usr/bin/env bash
# L4 aggregate test runner. One command, seven suites.
# Usage: run-tests.sh --all | --suite <01|02|03|04|05|06|07>
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
CP="$(cd "$HERE/../.." && pwd)"
RC=0
run_one() {
  echo "--- $1"
  sh "$2" || RC=1
}
case "${1:---all}" in
  --all)
    run_one "suite-01-roundtrip"  "$HERE/test/suite-01-roundtrip.sh"
    run_one "suite-02-envelope"   "$HERE/test/suite-02-envelope.sh"
    run_one "suite-03-d88"        "$HERE/test/suite-03-d88.sh"
    run_one "suite-04-banned"     "$HERE/test/suite-04-banned.sh"
    run_one "suite-05-derivation" "$CP/metrics/attention/test-derivation.sh"
    run_one "suite-06-rqm"        "$HERE/test/suite-06-rqm.sh"
    run_one "suite-07-validators" "$HERE/test/suite-07-validators.sh"
    ;;
  --suite)
    case "${2:-}" in
      05) run_one "suite-05-derivation" "$CP/metrics/attention/test-derivation.sh" ;;
      01|02|03|04|06|07) run_one "suite-$2" "$HERE/test/suite-$2"*.sh ;;
      *) echo "usage: run-tests.sh --all | --suite <01..07>"; exit 2 ;;
    esac
    ;;
  *) echo "usage: run-tests.sh --all | --suite <01..07>"; exit 2 ;;
esac
if [ "$RC" -eq 0 ]; then echo "L4 SUITE OK"; else echo "L4 SUITE FAIL"; fi
exit "$RC"
