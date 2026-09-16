#!/usr/bin/env bash
set -eu
cd "$(dirname "$0")/../../.."
bash tools/records/validate-boards.sh --horizons | grep -qx "BOARDS OK horizons=3 h1cols=4 h3items=9"
