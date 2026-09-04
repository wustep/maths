#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT

rustc --edition=2021 -O -D warnings \
  "$SCRIPT_DIR/verify_extension.rs" -o "$TMP_DIR/verify_extension"
"$TMP_DIR/verify_extension" "$SCRIPT_DIR/certs/oppermann_extension.tsv"
