#!/usr/bin/env bash
# Charter-named entry point (L4-00-charter.md DoD-8). Delegates to suite 6.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
out="$(sh "$HERE/test/suite-06-rqm.sh")"; rc=$?
echo "$out" | grep -E '^(PASS|FAIL|SKIP) RQ-[1-6] '
n="$(echo "$out" | grep -c '^PASS RQ-[1-6] ')"
if [ "$rc" -eq 0 ] && [ "$n" = "6" ]; then echo "RQM OK 6/6"; exit 0; fi
echo "RQM FAIL $n of 6"; exit 1
