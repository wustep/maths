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
# pysat is the environment package; fall back to venv if present.
if "$PY" -c "import pysat" 2>/dev/null; then
  :
else
  "$PY" -m pip install python-sat || true
fi
gcc -O3 -std=c11 n1_le32.c -o n1_le32 -lm
"$PY" color_d4.py
./n1_le32 8 8 > n1_le32.json
"$PY" t5_omega.py
if [ -f dual_exact.py ]; then
  "$PY" dual_exact.py
fi
if [ -f construct41.py ]; then
  "$PY" construct41.py
fi
"$PY" verify.py
echo "Q4_ALL_OK"
