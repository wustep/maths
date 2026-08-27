#!/usr/bin/env bash
# Replay line PP: Christopher–Lloyd (u², v²) time-rescale field of
# the translated radial cubic. Degree 7, four ovals, H(7)≥4 is not
# a dent of 74. Python expands over QQ; rustc expands again with a
# BTreeMap. The dumps are diffed.
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
