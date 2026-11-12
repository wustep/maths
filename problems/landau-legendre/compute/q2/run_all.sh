#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
Q1_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/../q1" && pwd)
TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT

for tool in python3 factor rustc cmp; do
  command -v "$tool" >/dev/null || {
    echo "missing required tool: $tool" >&2
    exit 1
  }
done

"$Q1_DIR/run_all.sh"
python3 "$SCRIPT_DIR/generate_extension.py" \
  --end 70500000010000 \
  --factor-timeout 60 \
  --output "$TMP_DIR/oppermann_extension.tsv"
cmp "$TMP_DIR/oppermann_extension.tsv" "$SCRIPT_DIR/certs/oppermann_extension.tsv"
"$SCRIPT_DIR/verify.sh"

echo "PASS landau_legendre_q2"
