#!/bin/sh
# Replay the finished q7 checks.  Does not re-run the long SAT / B&B hunts.
# Those certificates are native CaDiCaL DRAT + drat-trim; rebuild a CNF with
#   python3 write_cnf.py all-certs
# and check a stored proof with
#   python3 native_sat.py certs/five_k32_n2_1.cnf --proof --trim
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

"$PY" orbits.py
"$PY" star_cover_min.py
"$PY" replay_five_star.py
"$PY" dual_more.py
gcc -O3 -std=c11 leftover_global.c -o leftover_global -lm
# short smoke: tiny node budget, just compile+boot
./leftover_global 20 2000 0 > leftover_global_smoke.json || true
"$PY" verify.py
echo "Q7_ALL_OK"
