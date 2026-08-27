#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
tmp_dir=$(mktemp -d)
trap 'rm -rf "$tmp_dir"' EXIT

python3 verify.py --dump "$tmp_dir/python.txt"
rustc -D warnings -C opt-level=2 verify.rs -o "$tmp_dir/verify-rs"
(
  cd "$(pwd)"
  "$tmp_dir/verify-rs" --dump "$tmp_dir/rust.txt"
)
diff -u "$tmp_dir/python.txt" "$tmp_dir/rust.txt"
echo "Python and Rust dumps agree"
echo "OK"
