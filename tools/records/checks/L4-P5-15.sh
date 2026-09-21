#!/usr/bin/env bash
set -eu
cd "$(dirname "$0")/../../.."
bash tools/records/validate-ingest.sh --collectors | grep -qx "INGEST OK collectors=3 nightly=2 scrape=1"
