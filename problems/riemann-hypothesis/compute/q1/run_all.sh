#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT

for tool in python3 cc; do
  command -v "$tool" >/dev/null || {
    echo "missing required tool: $tool" >&2
    exit 1
  }
done

python3 "$SCRIPT_DIR/verify.py"
cc -std=c17 -O2 -Wall -Wextra -pedantic \
  "$SCRIPT_DIR/verify.c" -lm -o "$TMP_DIR/verify_riemann_q1"
"$TMP_DIR/verify_riemann_q1"

echo "PASS riemann_hypothesis_q1"
