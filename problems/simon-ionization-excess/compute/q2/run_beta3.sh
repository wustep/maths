#!/usr/bin/env bash
# Replay the β_3 attack. Exit 0 is residue: no leading-coefficient dent.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p certs work

echo "==> certify_beta3.py (withdrawn tail lift; rewrites beta3_rad.json)"
python3 certify_beta3.py

echo "==> explore_beta3.py (numerical upper bounds on β_3)"
python3 explore_beta3.py

echo "==> test_faces_small.py (C vs Python face enum, n=12)"
python3 test_faces_small.py

echo "==> certify_compact.py --quick (aspect≤4, n=18 faces)"
python3 certify_compact.py --quick

echo "==> aspect_try.py (equilibrium / t0-chain / truncation scan)"
python3 aspect_try.py

echo "==> lift_global.py (two-window p12; collapses to fmin)"
python3 lift_global.py

echo "==> verify_beta3.rs (independent n=16 R=4 rebuild)"
rustc -O -o verify_beta3_rs verify_beta3.rs
./verify_beta3_rs

echo "q2 beta3 PASS (residue; 1.1185 not beaten; 1.1168 withdrawn)"
