#!/usr/bin/env bash
# Replay the β_3^{rad} leading-coefficient attack.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p certs work

echo "==> explore_beta3.py (numerical upper bounds on β_3)"
python3 explore_beta3.py

echo "==> test_faces_small.py (C vs Python face enum, n=12)"
python3 test_faces_small.py

echo "==> certify_beta3.py (intervals + C face enum n=26 R=12)"
python3 certify_beta3.py

echo "==> verify_beta3.rs (independent n=16 rebuild)"
rustc -O -o verify_beta3_rs verify_beta3.rs
./verify_beta3_rs

echo "q2 beta3 replay PASS"
