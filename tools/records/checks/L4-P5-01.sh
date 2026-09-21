#!/usr/bin/env bash
set -eu
cd "$(dirname "$0")/../../.."
bash tools/records/validate-boards.sh --columns | grep -qx "BOARDS OK columns=7 inflight=4 nonstate=2 views=10 modes=2"
