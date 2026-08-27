#!/bin/sh
set -eu
HERE=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
cd "$HERE"
ROOT=$(dirname "$HERE")
if [ ! -x "$ROOT/.venv/bin/python" ]; then
  python3 -m venv "$ROOT/.venv"
  "$ROOT/.venv/bin/pip" install sympy scipy matplotlib
fi
PY="$ROOT/.venv/bin/python"
"$PY" dump_t5_pool.py
gcc -O3 -std=c11 clique41.c -o clique41
# 41-clique on the 355-point remainder (basis vectors peeled).
# The 36-clique hunt that would give a 41-set via the five universal
# basis vectors does not finish in this replay and is residue.
./clique41 t5_355_adj.txt > t5_clique.json
gcc -O3 -std=c11 sphere_clique.c -o sphere_clique -lm
./sphere_clique 2 > sphere_d2.json
"$PY" layer_replace.py
./clique41 q5cap_adj.txt > q5cap_clique.json
"$PY" unrestricted_dual.py
"$PY" verify.py
echo "Q2_ALL_OK"
