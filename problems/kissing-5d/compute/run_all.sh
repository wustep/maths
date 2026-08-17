#!/bin/sh
set -eu
HERE=$(dirname "$0")
cd "$HERE"
if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
  .venv/bin/pip install sympy scipy matplotlib
fi
PY="./.venv/bin/python"
"$PY" verify_configs.py
"$PY" extend_d5.py
"$PY" levenshtein.py
"$PY" d4_equator.py
"$PY" q5_extend.py
"$PY" restricted_lp.py
"$PY" exact_duals.py
"$PY" verify_certificates.py
"$PY" integer_d5.py
"$PY" check_integer_hits.py
"$PY" more_duals.py
"$PY" construct_search.py
"$PY" plot_dual.py
echo "ALL_OK"
