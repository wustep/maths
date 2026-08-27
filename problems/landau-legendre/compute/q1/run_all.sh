#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT

for tool in python3 rustc cc cmp; do
  command -v "$tool" >/dev/null || {
    echo "missing required tool: $tool" >&2
    exit 1
  }
done

python3 "$SCRIPT_DIR/make_rh_certificate.py" --output "$TMP_DIR/rh_delta.json"
cmp "$TMP_DIR/rh_delta.json" "$SCRIPT_DIR/certs/rh_delta.json"
python3 "$SCRIPT_DIR/verify_rh_certificate.py" "$SCRIPT_DIR/certs/rh_delta.json"

cc -std=c11 -O2 -Wall -Wextra -pedantic \
  "$SCRIPT_DIR/verify_rh_float.c" -lm -o "$TMP_DIR/verify_rh_float"
"$TMP_DIR/verify_rh_float"

python3 "$SCRIPT_DIR/verify_olc_audit.py" \
  --rows "$SCRIPT_DIR/certs/olc_rows.tsv.gz" \
  --summary "$SCRIPT_DIR/certs/olc_public_audit.json"

rustc --edition=2021 -O "$SCRIPT_DIR/generate_edge.rs" -o "$TMP_DIR/generate_edge"
"$TMP_DIR/generate_edge" \
  --start 4294867296 \
  --end 4294967295 \
  --output "$TMP_DIR/edge_witnesses.csv"
cmp "$TMP_DIR/edge_witnesses.csv" "$SCRIPT_DIR/certs/edge_witnesses.csv"
python3 "$SCRIPT_DIR/make_edge_summary.py" \
  --csv "$TMP_DIR/edge_witnesses.csv" \
  --output "$TMP_DIR/edge_summary.json" \
  --top 20
cmp "$TMP_DIR/edge_summary.json" "$SCRIPT_DIR/certs/edge_summary.json"
python3 "$SCRIPT_DIR/verify_edge.py" \
  --csv "$SCRIPT_DIR/certs/edge_witnesses.csv" \
  --summary "$SCRIPT_DIR/certs/edge_summary.json"

echo "PASS landau_legendre_q1"
