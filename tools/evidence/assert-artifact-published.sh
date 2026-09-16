#!/usr/bin/env bash
# Lane 2 - artifact publication check.
# Invariant 23 (line 9484) and Section 46.2 (lines 4132-4149): never rebuild an
# artifact to work around registry unavailability. This script therefore has no
# success path other than "the requested digest resolves in the registry".
# usage: assert-artifact-published.sh <image_repo> <digest>
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
. "$HERE/lib/identity.sh"

if [ "$#" -ne 2 ]; then
  echo "USAGE_ERROR assert-artifact-published.sh <image_repo> <digest>"
  exit 2
fi
REPO="$1"; DIGEST="$2"

[ -n "$REPO" ] || { echo "IMAGE_REPO_UNDECLARED"; exit 1; }
VERDICT="$(identity_guard digest "$DIGEST")" || { echo "$VERDICT"; exit 1; }

if docker buildx imagetools inspect "${REPO}@${DIGEST}" >/dev/null 2>&1; then
  echo "ARTIFACT_PUBLISHED ref=${REPO}@${DIGEST}"
  exit 0
fi

echo "ARTIFACT_NOT_RESOLVABLE ref=${REPO}@${DIGEST}"
echo "DO_NOT_REBUILD invariant=23 spec=Section-46.2 action=wait-for-the-registry"
exit 1
