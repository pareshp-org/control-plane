#!/usr/bin/env bash
# Lane 2 — artifact identity formats.
# Section 32 (L2825): the registry digest is the artifact identity.
# Section 96.6 row S18 (L8835) and D78 (L10172): for a platform-rebuild
# deployment the recorded identity - pinned commit, lockfile and build
# configuration - stands in for the digest throughout the chain.
# Two modes exist. There is no third, and no default.

IDENTITY_MODE_DIGEST="digest"
IDENTITY_MODE_PLATFORM_REBUILD="platform-rebuild"
IDENTITY_RE_DIGEST='^sha256:[0-9a-f]{64}$'
IDENTITY_RE_PLATFORM='^platform-rebuild:v1:[0-9a-f]{64}$'

# identity_mode_valid <mode>
identity_mode_valid() {
  case "$1" in
    "$IDENTITY_MODE_DIGEST") return 0 ;;
    "$IDENTITY_MODE_PLATFORM_REBUILD") return 0 ;;
    *) return 1 ;;
  esac
}

# identity_format_valid <mode> <value>
identity_format_valid() {
  case "$1" in
    "$IDENTITY_MODE_DIGEST")
      printf '%s' "$2" | grep -qE "$IDENTITY_RE_DIGEST" ;;
    "$IDENTITY_MODE_PLATFORM_REBUILD")
      printf '%s' "$2" | grep -qE "$IDENTITY_RE_PLATFORM" ;;
    *) return 1 ;;
  esac
}

# identity_guard <mode> <value>
# The single entry point every Lane 2 tool uses. Prints the fixed verdict
# string and returns non-zero on any doubt (Lane 2 rule P2-B).
identity_guard() {
  if ! identity_mode_valid "$1"; then
    printf 'IDENTITY_MODE_UNDECLARED mode=%s\n' "$1"
    return 1
  fi
  if ! identity_format_valid "$1" "$2"; then
    printf 'IDENTITY_FORMAT_INVALID mode=%s value=%s\n' "$1" "$2"
    return 1
  fi
  return 0
}
