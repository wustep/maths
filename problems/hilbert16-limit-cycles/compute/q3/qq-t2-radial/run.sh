#!/usr/bin/env bash
# Replay the T2 Chebyshev pullback of the §6 radial cubic
# (arXiv:2604.12883v1). Python expands the degree-7 field and the
# four-rectangle algebra; rustc expands again with a BTreeMap.
# The dumps are diffed.
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
