#!/usr/bin/env bash
# Lane 2 - digest invariant and artifact chain: the negative-test harness.
# Every case asserts BOTH an exact exit code AND an exact leading verdict token.
# A case that passes for the wrong reason is a failed harness (the same
# discipline Section 31.2 applies to seeded-defect cases, lines 2787-2794).
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
EV="$(cd "$HERE/.." && pwd)"
FIX="$HERE/fixtures"
PASS=0
FAIL=0

GOOD="sha256:$(printf 'a%.0s' $(seq 1 64))"
OTHER="sha256:$(printf 'b%.0s' $(seq 1 64))"
PLAT="platform-rebuild:v1:$(printf 'c%.0s' $(seq 1 64))"

check() { # label expected_exit expected_first_token  -- command...
  local label="$1" xc="$2" tok="$3"; shift 4
  local out rc first
  out="$("$@" 2>&1)"; rc=$?
  first="$(printf '%s' "$out" | head -1 | cut -d' ' -f1)"
  if [ "$rc" = "$xc" ] && [ "$first" = "$tok" ]; then
    printf 'PASS %s\n' "$label"; PASS=$((PASS+1))
  else
    printf 'FAIL %s expected_exit=%s got_exit=%s expected_token=%s got_token=%s\n' \
      "$label" "$xc" "$rc" "$tok" "$first"; FAIL=$((FAIL+1))
  fi
}

G="$EV/assert-staging-verified-identity.sh"

# --- the invariant itself (Section 32, lines 2803-2828) ---------------------
check inv-match-passes            0 DIGEST_INVARIANT_OK          -- bash "$G" "$FIX/records-ok"          alpha digest "$GOOD"
check inv-different-digest-refused 1 DIGEST_INVARIANT_VIOLATION  -- bash "$G" "$FIX/records-violation"   alpha digest "$GOOD"
check inv-unverified-staging-refused 1 NO_STAGING_VERIFIED_RECORD -- bash "$G" "$FIX/records-unverified" alpha digest "$GOOD"
check inv-unknown-product-refused  1 NO_STAGING_VERIFIED_RECORD  -- bash "$G" "$FIX/records-ok"          zulu  digest "$GOOD"
check inv-unparseable-record-refused 1 RECORD_UNPARSEABLE        -- bash "$G" "$FIX/records-unparseable" alpha digest "$GOOD"
check inv-absent-store-refused     1 RECORDS_STORE_ABSENT        -- bash "$G" "$HERE/nonexistent"        alpha digest "$GOOD"
check inv-bad-mode-refused         1 IDENTITY_MODE_UNDECLARED    -- bash "$G" "$FIX/records-ok"          alpha container "$GOOD"
check inv-bad-format-refused       1 IDENTITY_FORMAT_INVALID     -- bash "$G" "$FIX/records-ok"          alpha digest "sha256:short"

# --- the S18 equivalence (Section 96.6 L8835; D78 L10172) -----------
check s18-match-passes             0 DIGEST_INVARIANT_OK         -- bash "$G" "$FIX/records-platform" bravo platform-rebuild "$PLAT"
check s18-digest-in-platform-mode-refused 1 IDENTITY_FORMAT_INVALID -- bash "$G" "$FIX/records-platform" bravo platform-rebuild "$OTHER"
check s18-platform-id-in-digest-mode-refused 1 IDENTITY_FORMAT_INVALID -- bash "$G" "$FIX/records-ok" alpha digest "$PLAT"

# --- never rebuild (invariant 23, line 9484; Section 46.2, lines 4132-4149) --
export PATH="$HERE/stub:$PATH"
P="$EV/assert-artifact-published.sh"
STUB_DOCKER_MODE=ok          check reg-published-passes  0 ARTIFACT_PUBLISHED     -- env STUB_DOCKER_MODE=ok          bash "$P" ghcr.io/org/alpha "$GOOD"
STUB_DOCKER_MODE=unreachable check reg-unreachable-refused 1 ARTIFACT_NOT_RESOLVABLE -- env STUB_DOCKER_MODE=unreachable bash "$P" ghcr.io/org/alpha "$GOOD"

# --- SBOM beside the digest (Section 48.3, lines 4317-4320) ----------------
S="$EV/assert-sbom-beside-digest.sh"
TMP="$(mktemp -d)"
check sbom-present-passes  0 SBOM_PRESENT           -- env STUB_DOCKER_MODE=ok          bash "$S" "ghcr.io/org/alpha@${GOOD}" "$TMP/s1.json"
check sbom-empty-refused   1 SBOM_MISSING           -- env STUB_DOCKER_MODE=empty-sbom  bash "$S" "ghcr.io/org/alpha@${GOOD}" "$TMP/s2.json"
check sbom-unreachable-refused 1 ARTIFACT_NOT_RESOLVABLE -- env STUB_DOCKER_MODE=unreachable bash "$S" "ghcr.io/org/alpha@${GOOD}" "$TMP/s3.json"
check sbom-tag-ref-refused 1 IDENTITY_FORMAT_INVALID -- env STUB_DOCKER_MODE=ok         bash "$S" "ghcr.io/org/alpha:latest" "$TMP/s4.json"

# --- S18 identity computation (D78) ----------------------------------------
C="$EV/compute-platform-identity.sh"
W="$(mktemp -d)"; printf 'l\n' > "$W/lock"; printf 'b\n' > "$W/conf"
SHA40="$(printf 'd%.0s' $(seq 1 40))"
check s18-no-buildconfig-refused 1 PLATFORM_BUILD_CONFIG_UNDECLARED -- bash "$C" "$W" "$SHA40" lock ''
check s18-no-lockfile-refused    1 PLATFORM_LOCKFILE_UNDECLARED     -- bash "$C" "$W" "$SHA40" ''   conf
check s18-bad-commit-refused     1 COMMIT_SHA_INVALID               -- bash "$C" "$W" "nothex"  lock conf
check s18-missing-input-refused  1 PLATFORM_INPUT_MISSING           -- bash "$C" "$W" "$SHA40" absent conf

printf '\nL2 DIGEST-INVARIANT SUITE: pass=%s fail=%s\n' "$PASS" "$FAIL"
if [ "$FAIL" -ne 0 ]; then echo "SUITE_FAIL"; exit 1; fi
if [ "$PASS" -lt 21 ]; then echo "SUITE_UNDERRAN expected_at_least=21 got=$PASS"; exit 1; fi
echo "SUITE_PASS"
exit 0
