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
"$PY" a4_containing.py
"$PY" integer_restricted.py
"$PY" restricted_duals.py
"$PY" szollosi_candidates.py
"$PY" verify.py
echo "Q1_ALL_OK"
