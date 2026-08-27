#!/bin/sh
set -eu
HERE=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
cd "$HERE"
ROOT=$(dirname "$HERE")
if [ ! -x "$ROOT/.venv/bin/python" ]; then
  python3 -m venv "$ROOT/.venv"
  "$ROOT/.venv/bin/pip" install sympy scipy matplotlib numpy
fi
PY="$ROOT/.venv/bin/python"
gcc -O3 -std=c11 clique.c -o clique
gcc -O3 -std=c11 extras_bb.c -o extras_bb -lm
"$PY" sphere_types.py
"$PY" complete_slices.py
"$PY" a4_continuous.py
"$PY" t5_repair.py
"$PY" t5_36.py
# Short C replay; the stored 40M-node hunt is t5_36_c.json.
./clique t5_355_adj.txt 36 2000000 > t5_36_replay.json || true
"$PY" dual_gap.py
"$PY" verify.py
echo "Q3_ALL_OK"
