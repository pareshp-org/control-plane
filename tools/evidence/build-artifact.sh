#!/usr/bin/env bash
# ===========================================================================
# Lane 2 - build the artifact once, record its identity, emit its SBOM.
# Section 33.4 (lines 2887-2912): immutable artifact, digest recorded, SAME
#   digest deployed to production, never rebuilt.
# Section 32 item 5 (L2825): the registry digest is recorded at build.
# Section 48.3 (lines 4317-4320): the SBOM is emitted in the same pipeline step.
# Section 96.6 row S18 (L8835) / D78 (L10172): a platform-rebuild
#   product records the equivalent identity instead of a digest.
#
# Environment contract (all read, none defaulted silently):
#   PRODUCT              required
#   IDENTITY_MODE        required: digest | platform-rebuild
#   OUT_DIR              required: directory the identity and SBOM are written to
#   COMMIT_SHA           required: 40 hex
#   IMAGE_REPO           required when IDENTITY_MODE=digest
#   DOCKERFILE           optional, default Dockerfile        (digest mode)
#   BUILD_CONTEXT        optional, default .                 (digest mode)
#   LOCKFILE_PATHS       required when IDENTITY_MODE=platform-rebuild (csv)
#   BUILD_CONFIG_PATHS   required when IDENTITY_MODE=platform-rebuild (csv)
#   SBOM_FILE            required when IDENTITY_MODE=platform-rebuild
#   REPO_ROOT            optional, default .
# ===========================================================================
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
. "$HERE/lib/identity.sh"

: "${PRODUCT:?PRODUCT_UNDECLARED}"
: "${IDENTITY_MODE:?IDENTITY_MODE_UNDECLARED}"
: "${OUT_DIR:?OUT_DIR_UNDECLARED}"
: "${COMMIT_SHA:?COMMIT_SHA_UNDECLARED}"
DOCKERFILE="${DOCKERFILE:-Dockerfile}"
BUILD_CONTEXT="${BUILD_CONTEXT:-.}"
REPO_ROOT="${REPO_ROOT:-.}"
IMAGE_REPO="${IMAGE_REPO:-}"
LOCKFILE_PATHS="${LOCKFILE_PATHS:-}"
BUILD_CONFIG_PATHS="${BUILD_CONFIG_PATHS:-}"
SBOM_FILE="${SBOM_FILE:-}"

identity_mode_valid "$IDENTITY_MODE" || { echo "IDENTITY_MODE_UNDECLARED mode=$IDENTITY_MODE"; exit 1; }
mkdir -p "$OUT_DIR"

case "$IDENTITY_MODE" in

  digest)
    [ -n "$IMAGE_REPO" ] || { echo "IMAGE_REPO_UNDECLARED"; exit 1; }
    [ -f "$REPO_ROOT/$DOCKERFILE" ] || { echo "DOCKERFILE_MISSING path=$DOCKERFILE"; exit 1; }
    META="$OUT_DIR/build-metadata.json"
    # --sbom=true makes the builder emit the SBOM in this same step and store it
    # in the registry against this same digest (Section 48.3).
    docker buildx build \
      --file "$REPO_ROOT/$DOCKERFILE" \
      --tag "${IMAGE_REPO}:${COMMIT_SHA}" \
      --label "org.opencontainers.image.revision=${COMMIT_SHA}" \
      --sbom=true \
      --provenance=mode=max \
      --metadata-file "$META" \
      --push \
      "$REPO_ROOT/$BUILD_CONTEXT"
    DIGEST="$(jq -r '."containerimage.digest" // empty' "$META")"
    VERDICT="$(identity_guard digest "$DIGEST")" || { echo "$VERDICT"; exit 1; }
    IDENTITY="$DIGEST"
    bash "$HERE/assert-sbom-beside-digest.sh" "${IMAGE_REPO}@${DIGEST}" "$OUT_DIR/sbom.json"
    SBOM_OUT="$OUT_DIR/sbom.json"
    ;;

  platform-rebuild)
    # D78: the byte-identical digest is structurally unavailable on a git-push
    # PaaS. The recorded identity stands in for it. The SBOM still has to exist,
    # so the caller supplies the one its own build produced; an absent file is a
    # failure, never a skip (Section 33.2 forbids a silent skip on a gate).
    [ -n "$SBOM_FILE" ] || { echo "SBOM_UNDECLARED mode=platform-rebuild"; exit 1; }
    [ -s "$REPO_ROOT/$SBOM_FILE" ] || { echo "SBOM_MISSING path=$SBOM_FILE"; exit 1; }
    IDENTITY="$(bash "$HERE/compute-platform-identity.sh" \
                 "$REPO_ROOT" "$COMMIT_SHA" "$LOCKFILE_PATHS" "$BUILD_CONFIG_PATHS")"
    VERDICT="$(identity_guard platform-rebuild "$IDENTITY")" || { echo "$VERDICT"; exit 1; }
    cp "$REPO_ROOT/$SBOM_FILE" "$OUT_DIR/sbom.json"
    SBOM_OUT="$OUT_DIR/sbom.json"
    echo "SBOM_PRESENT ref=$IDENTITY file=$SBOM_OUT bytes=$(wc -c < "$SBOM_OUT" | tr -d ' ')"
    ;;

  *)
    echo "IDENTITY_MODE_UNDECLARED mode=$IDENTITY_MODE"
    exit 1
    ;;
esac

printf '%s' "$IDENTITY" > "$OUT_DIR/identity.txt"
{
  printf 'product=%s\n'       "$PRODUCT"
  printf 'identity_mode=%s\n' "$IDENTITY_MODE"
  printf 'identity=%s\n'      "$IDENTITY"
  printf 'image_repo=%s\n'    "$IMAGE_REPO"
  printf 'commit=%s\n'        "$COMMIT_SHA"
  printf 'sbom_file=%s\n'     "$SBOM_OUT"
  printf 'run_id=%s\n'        "${GITHUB_RUN_ID:-local}"
  printf 'run_url=%s\n'       "${GITHUB_SERVER_URL:-local}/${GITHUB_REPOSITORY:-local}/actions/runs/${GITHUB_RUN_ID:-local}"
} > "$OUT_DIR/artifact.env"

echo "DIGEST_RECORDED product=$PRODUCT mode=$IDENTITY_MODE identity=$IDENTITY"
exit 0
