#!/usr/bin/env bash
set -eu
cd "$(dirname "$0")/../../.."
bash tools/records/validate-ingest.sh --scorecard | grep -qx "INGEST OK scorecard conditions=2 pending=2 arming=unarmed"
