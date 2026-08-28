#!/bin/sh
# Replay q33 leftover cubes from n=142. Parent F4 certificates stay in q4.
set -e
here=$(cd "$(dirname "$0")" && pwd)
cd "$here"
parent=$(dirname "$here")

echo "== parent F4 certificate at 0.34645 =="
python3 "$parent/verify_certificate.py" "$parent/certs/f4_certificate.json" --margin 0.05 --c 0.34645

echo "== q4 F4 CKLS-fork certificate at 0.34640 =="
python3 "$parent/q4/verify_q4_certificate.py" "$parent/q4/certs/keep/f4_or_new_certificate.json" --margin 0.05

echo "== sequential-counter encoding vs known small n and n=21 d=6 =="
python3 regression.py

echo "== stored pigeonhole DRATs against regenerated CNFs =="
python3 verify_keep.py
echo "q33 replay finished"
