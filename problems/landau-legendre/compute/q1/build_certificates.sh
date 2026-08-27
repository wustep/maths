#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
OUTPUT_DIR=${1:?usage: build_certificates.sh OUTPUT_DIR [OLC_REPO]}
OLC_REPO=${2:-}
TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT
mkdir -p "$OUTPUT_DIR"

python3 "$SCRIPT_DIR/make_rh_certificate.py" --output "$OUTPUT_DIR/rh_delta.json"
rustc --edition=2021 -O "$SCRIPT_DIR/generate_edge.rs" -o "$TMP_DIR/generate_edge"
"$TMP_DIR/generate_edge" \
  --start 4294867296 \
  --end 4294967295 \
  --output "$OUTPUT_DIR/edge_witnesses.csv"
python3 "$SCRIPT_DIR/make_edge_summary.py" \
  --csv "$OUTPUT_DIR/edge_witnesses.csv" \
  --output "$OUTPUT_DIR/edge_summary.json" \
  --top 20

if [[ -n "$OLC_REPO" ]]; then
  python3 "$SCRIPT_DIR/audit_olc.py" \
    --repo "$OLC_REPO" \
    --rows-output "$OUTPUT_DIR/olc_rows.tsv.gz" \
    --summary-output "$OUTPUT_DIR/olc_public_audit.json"
fi

echo "WROTE $OUTPUT_DIR"
