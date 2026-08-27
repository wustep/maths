#!/bin/sh
set -e
cd "$(dirname "$0")"
# Parent replay first (the 2026-08-17 1/2 bound).
python3 ../verify_interval.py
python3 ../verify_half.py
python3 verify_q1.py
echo "q1 all checks passed"
