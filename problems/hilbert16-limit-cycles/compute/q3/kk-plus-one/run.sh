#!/usr/bin/env bash
# Replay line KK: Gasull–Santana +1 algebra on the radial cubic.
# Python dump versus Rust dump, then diff. Exit 0.
set -euo pipefail

cd "$(dirname "$0")"
tmp_dir=$(mktemp -d)
trap 'rm -rf "$tmp_dir"' EXIT

python3 verify.py --dump "$tmp_dir/python.txt"

if command -v rustc >/dev/null 2>&1; then
  rustc --edition 2021 -D warnings -C opt-level=2 verify.rs -o "$tmp_dir/verify-rs"
  (
    cd "$(pwd)"
    "$tmp_dir/verify-rs" --dump "$tmp_dir/rust.txt"
  )
  diff -u "$tmp_dir/python.txt" "$tmp_dir/rust.txt"
  echo "Python and Rust dumps agree"
else
  echo "rustc not on PATH; python-only replay (documented)"
fi

echo "OK"
