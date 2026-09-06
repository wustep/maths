#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT

for tool in python3 cc cmp; do
  command -v "$tool" >/dev/null || {
    echo "missing required tool: $tool" >&2
    exit 1
  }
done

python3 "$SCRIPT_DIR/../q1/verify_rh_certificate.py" \
  "$SCRIPT_DIR/../q1/certs/rh_delta.json"

python3 "$SCRIPT_DIR/make_certificate.py" \
  --output "$TMP_DIR/rh_delta_taylor.json"
cmp "$TMP_DIR/rh_delta_taylor.json" \
  "$SCRIPT_DIR/certs/rh_delta_taylor.json"
python3 "$SCRIPT_DIR/verify_certificate.py" \
  "$SCRIPT_DIR/certs/rh_delta_taylor.json"

cc -std=c11 -O2 -Wall -Wextra -pedantic \
  "$SCRIPT_DIR/verify_float.c" -lm -o "$TMP_DIR/verify_float"
"$TMP_DIR/verify_float"

echo "PASS landau_legendre_q3"
