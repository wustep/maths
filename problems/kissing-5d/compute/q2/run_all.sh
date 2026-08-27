#!/bin/sh
set -eu
HERE=$(dirname "$0")
cd "$HERE"
ROOT=$(dirname "$HERE")
if [ ! -x "$ROOT/.venv/bin/python" ]; then
  python3 -m venv "$ROOT/.venv"
  "$ROOT/.venv/bin/pip" install sympy scipy matplotlib
fi
PY="$ROOT/.venv/bin/python"
"$PY" dump_t5_pool.py
gcc -O3 -std=c11 clique41.c -o clique41
./clique41 t5_adj.txt > t5_clique.json
gcc -O3 -std=c11 sphere_clique.c -o sphere_clique -lm
./sphere_clique 2 > sphere_d2.json
"$PY" layer_replace.py
"$PY" unrestricted_dual.py
"$PY" verify.py
echo "Q2_ALL_OK"
