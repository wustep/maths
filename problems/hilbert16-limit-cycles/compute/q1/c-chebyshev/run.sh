#!/bin/sh
# Replay the Chebyshev pullback identity and Table 1 / Appendix A
# arithmetic from arXiv:2604.12883v1. Python expands the Section 6
# field and the nine-rectangle algebra; rustc repeats the degree and
# the table; the two JSON cores are diffed.
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
cd "$HERE"
python3 verify.py
rustc --edition 2021 -O -o verify_rs verify.rs
./verify_rs
python3 diff_certs.py
echo "c-chebyshev: ok"
