#!/usr/bin/env bash
set -eu
cd "$(dirname "$0")/../../.."
test -f metrics/ingest/README.md
test -x tools/records/validate-ingest.sh
bash tools/records/validate-ingest.sh --collectors 2>&1 | grep -q "INGEST ERROR missing-limb"
