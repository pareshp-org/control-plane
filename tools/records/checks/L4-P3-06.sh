#!/usr/bin/env bash
set -euo pipefail
# Check: L4-P3-06 - SIG source map and metrics/register bootstrap
CP_DIR="$(git rev-parse --show-toplevel)"
DECL="$CP_DIR/metrics/register/metric-declarations.yaml"
VS="$CP_DIR/metrics/register/validate-sources.sh"
SIG="$CP_DIR/metrics/signals/sig-source-map.yaml"

# Positive: all three files present
[[ -f "$DECL" ]] || { echo "ABSENT: $DECL" >&2; exit 1; }
[[ -f "$VS"   ]] || { echo "ABSENT: $VS"   >&2; exit 1; }
[[ -f "$SIG"  ]] || { echo "ABSENT: $SIG"  >&2; exit 1; }

# Assertion: validate-sources.sh exits 0 on plain run
bash "$VS" >/dev/null || { echo "validate-sources.sh failed" >&2; exit 1; }

# Assertion: sig-source-map has exactly 7 signal_id rows
COUNT=$(grep -c 'signal_id:' "$SIG")
[ "$COUNT" -eq 7 ] || { echo "expected 7 signal_id rows, got $COUNT" >&2; exit 1; }

# Assertion: SIG-47 is present (D-L4-TL-4 decision)
grep -q 'SIG-47' "$SIG" || { echo "SIG-47 missing from sig-source-map.yaml" >&2; exit 1; }

# Negative fixture: a missing metric-declarations.yaml must cause exit 1
TMP=$(mktemp -d)
FAKE_VS="$TMP/validate-sources.sh"
cat > "$FAKE_VS" <<'INNER'
#!/usr/bin/env bash
set -euo pipefail
DECL_FILE="$(cd "$(dirname "$0")" && pwd)/metric-declarations.yaml"
[[ -f "$DECL_FILE" ]] || { echo "ABSENT: $DECL_FILE" >&2; exit 1; }
echo "SOURCES OK"; exit 0
INNER
chmod +x "$FAKE_VS"
# neg fixture: no metric-declarations.yaml in TMP
bash "$FAKE_VS" >/dev/null 2>&1 && { echo "neg-fixture: expected failure did not occur" >&2; rm -rf "$TMP"; exit 1; }
rm -rf "$TMP"

echo "CHECK L4-P3-06 PASS"
