#!/bin/sh
# Replay the 2-sample {b,1} ceiling, the protocol hunts, Ellis, and the mesh.
set -e
cd "$(dirname "$0")"
PY="${PY:-python3}"

echo "== ceiling (analytic 2-sample barrier) =="
"$PY" ceiling.py

echo "== verify_ceiling.c (independent min of f) =="
gcc -O3 -std=c11 -o verify_ceiling verify_ceiling.c -lm
./verify_ceiling

echo "== replay Ellis (Gilmer Conjecture 1 is false) =="
"$PY" replay_ellis.py

echo "== hunt mixes (β, Example 5, maxent) =="
"$PY" hunt_mixes.py

echo "== hunt protocols (half-target, scaled a(t)) =="
"$PY" hunt_protocols.py

echo "== hunt 3-atomic / 2-mixture residue =="
"$PY" hunt_three.py

echo "== verify.py =="
"$PY" verify.py

if [ -f certs/hunt_mixes.json ]; then
  echo "== plot =="
  "$PY" plot_ceiling.py
fi

echo "ALL DONE"
