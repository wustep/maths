#!/bin/sh
# Replay q4: F4 certificate still holds, encoder matches known small-n
# SAT/UNSAT including the n=18 k=11 cube, the cyclic construction at
# n=73 d=24 still SAT, and every stored pigeonhole DRAT checks
# against a freshly encoded CNF.
set -e
here=$(cd "$(dirname "$0")" && pwd)
cd "$here"
parent=$(dirname "$here")

echo "== parent F4 certificate at 0.34645 =="
python3 "$parent/verify_certificate.py" "$parent/certs/f4_certificate.json" --margin 0.05 --c 0.34645

echo "== q4 F4 CKLS-fork certificate at 0.34640 =="
python3 verify_q4_certificate.py certs/keep/f4_or_new_certificate.json --margin 0.05

echo "== leftover-cube covering count =="
python3 count_obstruction.py --self-test

echo "== sequential-counter encoding vs known small n and n=21 d=6 =="
python3 regression.py

echo "== stored pigeonhole DRATs against regenerated CNFs =="
python3 verify_keep.py
echo "q4 replay finished"
