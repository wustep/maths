#!/bin/sh
# Replay the Harnack recurrence H(n)+Har(m) on the published seeds
# used in q1/c-chebyshev, plus the Chebyshev table already on
# arXiv:2604.12883v1. Python writes the integer tables; rustc
# recomputes Har and the comparisons; the two JSON cores are diffed.
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
cd "$HERE"
python3 verify.py
rustc --edition 2021 -O -o verify_rs verify.rs
./verify_rs
python3 diff_certs.py
echo "p-harnack-recurrence: ok"
