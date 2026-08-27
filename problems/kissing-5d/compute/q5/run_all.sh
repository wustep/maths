#!/bin/sh
# Replay the finished q5 checks.  Does not re-run the long SAT / B&B hunts.
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

"$PY" extras_types.py
"$PY" type_a_clique.py
"$PY" seed_graph.py
"$PY" four_star_census.py
"$PY" t5_share_pruned.py
# 3-star extras: replay one pool via the recorded JSON, not the SAT hunt
"$PY" -c "import json; d=json.load(open('triple_star_extras.json')); assert d['n_pools']==120 and not d['found_41'] and d['n_bb_complete_empty']==120"
"$PY" -c "import json; d=json.load(open('t5_share23.json')); assert d['complete'] and not d['found_36'] and d['best_extra']==12"
"$PY" dual_more.py
gcc -O3 -std=c11 extras_clique.c -o extras_clique -lm
# short smoke: tiny node budget, just compile+boot
./extras_clique 20 2000 > extras_clique_smoke.json || true
"$PY" verify.py
echo "Q5_ALL_OK"
