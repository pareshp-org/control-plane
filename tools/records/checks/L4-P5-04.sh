#!/usr/bin/env bash
set -eu
cd "$(dirname "$0")/../../.."
PY="${L4_PY:-python}"
bash tools/records/validate-boards.sh --estimate-capture | grep -qx "BOARDS OK estimate-capture=1 exempt=3"
"$PY" tools/records/estimate_capture.py --transition in_progress --item-class normal_planned_work --band M 2>&1 \
  | grep -q "ESTIMATE FAIL not-the-capture-point:in_progress"
"$PY" tools/records/estimate_capture.py --transition ready_confirmation --band M 2>&1 \
  | grep -q "ESTIMATE ERROR missing-item-class"
"$PY" tools/records/estimate_capture.py --transition ready_confirmation --item-class incident 2>&1 \
  | grep -q "ESTIMATE OK exempt=incident"
