#!/usr/bin/env bash
# Appends ONE record file to the records repository. Spec Section 97.2.
# Args: <store> <record-id> <yaml-body-on-stdin>
# <store> is a path segment under records/, e.g. deployments, restore-tests,
# uat, incidents, decisions — the canonical stores of Section 97.2.
set -euo pipefail
[ "$#" -eq 2 ] || { echo "FATAL: emit-record.sh needs 2 args" >&2; exit 1; }
STORE="$1"; RID="$2"
: "${RECORDS_REPO:?FATAL: RECORDS_REPO unset}"
: "${RECORDS_WRITER_TOKEN:?FATAL: RECORDS_WRITER_TOKEN unset}"
BODY="$(cat)"
[ -n "$BODY" ] || { echo "FATAL: empty record body" >&2; exit 1; }
WORK="$(mktemp -d)"
git -c http.extraheader="AUTHORIZATION: bearer ${RECORDS_WRITER_TOKEN}" \
    clone --depth 1 "https://github.com/${RECORDS_REPO}.git" "$WORK/r" >/dev/null 2>&1
mkdir -p "$WORK/r/records/${STORE}"
TARGET="$WORK/r/records/${STORE}/${RID}.yaml"
[ -e "$TARGET" ] && { echo "FATAL: record ${RID} exists; records never edit in place (Section 97.2)" >&2; exit 1; }
printf '%s\n' "$BODY" > "$TARGET"
grep -q '^record_schema_version:' "$TARGET" || { echo "FATAL: record_schema_version missing (Section 97.2)" >&2; exit 1; }
git -C "$WORK/r" add "records/${STORE}/${RID}.yaml"
git -C "$WORK/r" -c user.name="records-writer" -c user.email="records-writer@invalid" \
    -c commit.gpgsign=true commit -S -m "record ${STORE}/${RID}"
git -C "$WORK/r" -c http.extraheader="AUTHORIZATION: bearer ${RECORDS_WRITER_TOKEN}" push origin HEAD
echo "records/${STORE}/${RID}.yaml"
