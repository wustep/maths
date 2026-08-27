#!/usr/bin/env bash
# Replay line O: adj(DΦ) identity, degree, real-sheet count, and the
# k=1..6 arithmetic for iterated complex squaring. Python expands
# over QQ; rustc expands again with a BTreeMap. The dumps are diffed.
set -euo pipefail
cd "$(dirname "$0")"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

python3 verify.py --dump "$tmp/python.txt"
rustc --edition 2021 -D warnings -C opt-level=2 verify.rs -o "$tmp/verify-rs"
"$tmp/verify-rs" --dump "$tmp/rust.txt"
diff -u "$tmp/python.txt" "$tmp/rust.txt"
echo "Python and Rust dumps agree"
echo "OK"
