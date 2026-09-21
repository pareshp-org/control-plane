#!/usr/bin/env bash
# Section 36.6 / invariant 84: "env | grep -i api_key must return empty".
# Prints variable NAMES only. Never prints a value.
set -u
names="$(env | sed -n 's/^\([A-Za-z_][A-Za-z0-9_]*\)=.*/\1/p' \
         | grep -i 'api_key' | sort | tr '\n' ' ')"
names="${names% }"
if [ -n "$names" ]; then
  count="$(printf '%s\n' $names | wc -l | tr -d ' ')"
  echo "NO-API-KEYS: FAIL ($count variables: $names)"
  echo "REMEDY: unset the variable and remove it from the shell profile or"
  echo "REMEDY: the repository .env file. Do not weaken this check."
  exit 1
fi
echo "NO-API-KEYS: PASS"
exit 0
