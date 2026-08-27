#!/bin/sh
# Replay the analytic margin, failed joint handle, and two q3 meshes.
set -e
cd "$(dirname "$0")"
PY="${PY:-python3}"

echo "== analytic margin =="
"$PY" solve_margin.py

echo "== shared-union joint-entropy probe =="
"$PY" probe_joint.py

echo "== Python row-boundary mesh =="
"$PY" verify.py

echo "== C exhaustive mesh =="
gcc -O3 -std=c11 -o verify_c verify.c -lm
./verify_c

echo "== compare certificates =="
"$PY" compare.py

echo "ALL DONE"
