#!/bin/sh
# Replay the finished q6 checks.  Does not re-run the long SAT / B&B hunts.
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

"$PY" four_star_color.py
"$PY" five_star_census.py
"$PY" star_cover_min.py
"$PY" dual_more.py
gcc -O3 -std=c11 four_star_extras.c -o four_star_extras -lm
gcc -O3 -std=c11 five_star_extras.c -o five_star_extras -lm
# short smoke: one shard, tiny node budget
./four_star_extras 20 2000 0 210 > four_star_extras_smoke.json || true
if [ -f four_star_extras_s0.json ] && [ -f four_star_extras_s1.json ]; then
  "$PY" merge_four_star.py
fi
"$PY" verify.py
echo "Q6_ALL_OK"
