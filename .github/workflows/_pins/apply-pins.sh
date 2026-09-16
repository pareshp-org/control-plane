#!/usr/bin/env bash
# Replaces every __PIN_<KEY>__ token in .github/workflows/*.yml with the SHA
# recorded in pins.env, appending the human-readable tag as a comment.
# Idempotent: a file with no tokens is left byte-identical.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# shellcheck disable=SC1091
set -a; . .github/workflows/_pins/pins.env; set +a
KEYS="ACTIONS_CHECKOUT ACTIONS_SETUP_PYTHON ACTIONS_UPLOAD_ARTIFACT ACTIONS_DOWNLOAD_ARTIFACT
ACTIONS_GITHUB_SCRIPT DOCKER_SETUP_BUILDX DOCKER_LOGIN DOCKER_BUILD_PUSH"
for f in .github/workflows/*.yml; do
  [ -e "$f" ] || continue
  for key in $KEYS; do
    shavar="PIN_${key}_SHA"; tagvar="PIN_${key}_TAG"
    sha="${!shavar:-}"; tag="${!tagvar:-}"
    [ -z "$sha" ] && continue
    sed -i "s|__PIN_${key}__|${sha} # ${tag}|g" "$f"
  done
done
echo "pins applied"
