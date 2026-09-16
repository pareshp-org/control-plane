#!/usr/bin/env bash
set -eu
cd "$(dirname "$0")/../../.."
bash tools/records/validate-ingest.sh --prometheus | grep -qx "INGEST OK prometheus endpoints=3 profiles=2 exempt=5 posture=private-authenticated"
