#!/usr/bin/env bash
# Replay q3. Exit 0 is a dent of the printed leading 1.1185,
# using the q2 R=12 compact certificate plus the mass-opt lift.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p certs work

echo "==> leftover: small Z (residue; Lieb still best integers)"
python3 work/smallz_replay.py
python3 work/smallz_check.py

echo "==> leftover: s>3 and Newton–Toeplitz (residue)"
python3 work/toeplitz_probe.py

echo "==> aspect algebra"
python3 aspect_identities.py
python3 verify_lift.py

echo "==> verify_aspect.c"
gcc -O2 -o verify_aspect verify_aspect.c -lm
./verify_aspect

echo "==> verify_aspect.rs"
rustc -O -o verify_aspect_rs verify_aspect.rs
./verify_aspect_rs

echo "==> mass-opt check and atomic trial"
python3 mass_opt_check.py
python3 trial_atomic.py

echo "==> HPS §7 with lifted β3"
python3 tighten_leading.py

echo "==> assemble"
python3 lift_cert.py

echo "q3 PASS (leading 1.1185 lifted to 1.1118; not the aspect-≤4 1.1087)"
