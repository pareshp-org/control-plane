#!/usr/bin/env bash
set -eu
cd "$(dirname "$0")/../../.."
bash tools/records/validate-boards.sh --ready | grep -qx "BOARDS OK ready=10 pipeline=7 exempt=3"
