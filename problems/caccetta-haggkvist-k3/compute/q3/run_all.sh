#!/bin/sh
# Replay q3: F4 certificate still holds, encoder matches known small-n
# SAT/UNSAT including the n=18 k=11 cube, the cyclic construction at
# n=38 d=12 still SAT, and every stored pigeonhole DRAT checks
# against a freshly encoded CNF.
set -e
here=$(cd "$(dirname "$0")" && pwd)
cd "$here"
parent=$(dirname "$here")

echo "== parent F4 certificate at 0.34645 =="
python3 "$parent/verify_certificate.py" "$parent/certs/f4_certificate.json" --margin 0.05 --c 0.34645

echo "== sequential-counter encoding vs known small n and n=21 d=6 =="
python3 regression.py

echo "== stored pigeonhole DRATs against regenerated CNFs =="
python3 verify_keep.py
echo "q3 replay finished"
