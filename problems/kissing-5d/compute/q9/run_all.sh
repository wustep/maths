#!/bin/sh
# Replay the finished q9 checks.  Does not re-run the long SAT hunts.
set -eu
HERE=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
cd "$HERE"
ROOT=$(dirname "$HERE")
if [ ! -x "$ROOT/.venv/bin/python" ]; then
  python3 -m venv "$ROOT/.venv"
  "$ROOT/.venv/bin/pip" install sympy scipy matplotlib numpy
fi
PY="$ROOT/.venv/bin/python"
if ! "$PY" -c "import pysat" 2>/dev/null; then
  "$PY" -m pip install python-sat || true
fi

"$PY" ../q8/orbits.py
cp -f ../q8/orbits.json orbits.json
"$PY" write_cnf.py all
"$PY" replay_k30.py
gcc -O3 -std=c11 ../q8/leftover_k30.c -o leftover_k30 -lm
./leftover_k30 20 2000 3 > leftover_k30_smoke.json || true
"$PY" verify.py
echo "Q9_ALL_OK"
