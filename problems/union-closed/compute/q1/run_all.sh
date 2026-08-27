#!/bin/sh
# Replay the analytic first-crossing, the Python mesh, and the C mesh.
set -e
cd "$(dirname "$0")"
PY="${PY:-python3}"

echo "== solve_crossing (analytic b*, c*) =="
"$PY" solve_crossing.py

echo "== verify.py (published + analytic + mesh) =="
"$PY" verify.py

echo "== verify.c (independent mesh) =="
gcc -O3 -std=c11 -o verify_c verify.c -lm
./verify_c

if [ -f scan_beta.json ]; then
  echo "== plot =="
  "$PY" plot_curve.py
fi

echo "ALL DONE"
