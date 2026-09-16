#!/usr/bin/env bash
# All three D87 Blocking rows in one call. Exits 4 if any row is Blocking, so a
# caller cannot mistake a Blocking finding for an ordinary failure.
set -euo pipefail
RUN="${1:?usage: run-all-checks.sh <runner-listing.tsv> <resolution.tsv> <admissions.tsv>}"
RES="${2:?}"
ADM="${3:?}"
rc=0
infra/runners/d87/check-ephemeral-registration.sh "$RUN" || rc=4
infra/runners/d87/check-privileged-workflow-tier.sh "$RES" || rc=4
infra/runners/d87/check-no-branch-push-in-privileged.sh "$ADM" || rc=4
if [ "$rc" -eq 0 ]; then echo "D87: PASS (3 rows)"; else echo "D87: BLOCKING"; fi
exit "$rc"
