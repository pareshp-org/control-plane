#!/usr/bin/env bash
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"; CP="$(cd "$HERE/../../.." && pwd)"
. "$HERE/lib.sh"
N="$HERE/normalise.py"
TMP="${L4_TMP:?}/rt"; rm -rf "$TMP"; mkdir -p "$TMP"

i=0
for f in "$CP"/tools/records/fixtures/valid/verbatim/*.yaml \
         $(find "$CP/tools/records/fixtures/valid/generated" -name '*.yaml' 2>/dev/null | sort); do
  i=$((i+1)); id=$(printf 'RT-%02d' "$i")
  a="$(python3 "$N" "$f")"
  python3 -c "import sys,yaml,json; yaml.safe_dump(json.loads(sys.argv[1]), open(sys.argv[2],'w',encoding='utf-8'), sort_keys=True, default_flow_style=False)" "$a" "$TMP/rt.yaml"
  b="$(python3 "$N" "$TMP/rt.yaml")"
  assert_eq "$id" "$a" "$b"
done

# RT read-side default: absent version reads as 1.
sed '/^record_schema_version:/d' "$CP/tools/records/fixtures/valid/verbatim/incident.yaml" > "$TMP/no-rsv.yaml"
got="$(python3 -c "import yaml;d=yaml.safe_load(open('$TMP/no-rsv.yaml'));print(d.get('record_schema_version',1))")"
assert_eq "RT-RSV-DEFAULT" "1" "$got"

sed '/^event_schema_version:/d' "$CP/tools/records/fixtures/valid/verbatim/event.yaml" > "$TMP/no-esv.yaml"
got="$(python3 -c "import yaml;d=yaml.safe_load(open('$TMP/no-esv.yaml'));print(d.get('event_schema_version',1))")"
assert_eq "RT-ESV-DEFAULT" "1" "$got"

# Every generated record states the version explicitly (writer side).
if [ -d "$CP/tools/records/fixtures/valid/generated/records" ]; then
  miss="$(grep -rL '^record_schema_version:' "$CP/tools/records/fixtures/valid/generated/records" | wc -l | tr -d ' ')"
else
  miss=0
fi
assert_eq "RT-WRITER-STATES-RSV" "0" "$miss"

summary "01-roundtrip"
