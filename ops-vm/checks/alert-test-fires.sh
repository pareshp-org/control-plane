#!/usr/bin/env bash
# Section 51.4 post-patch item: alert rules fire a test alert. Fires the rule and
# asserts the designated channel accepted it; asserts nothing about content.
set -euo pipefail
BASE="${1:?usage: alert-test-fires.sh <grafana-base-url> <api-token>}"
TOKEN="${2:?}"
code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 20 \
  -H "Authorization: Bearer $TOKEN" -X POST "$BASE/api/alertmanager/grafana/config/api/v1/receivers/test" \
  -H 'Content-Type: application/json' \
  --data '{"receivers":[{"name":"designated-channel"}]}')
case "$code" in
  2*) echo "ALERT-TEST: PASS" ;;
  *)  echo "ALERT-TEST: FAIL (http $code)"; exit 1 ;;
esac
