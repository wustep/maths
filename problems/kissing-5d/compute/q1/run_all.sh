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
"$PY" polar_vertices.py
"$PY" replay_max_vertex.py
"$PY" a4_containing.py
"$PY" dump_q5_tables.py
gcc -O3 -std=c11 integer_q5_44.c -o integer_q5_44
./integer_q5_44 > integer_q5_44.json
"$PY" check_q5_44_empty.py
"$PY" restricted_duals.py
"$PY" szollosi_candidates.py
"$PY" verify.py
echo "Q1_ALL_OK"
