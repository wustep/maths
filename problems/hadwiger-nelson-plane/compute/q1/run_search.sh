#!/bin/sh
set -eu
cd "$(dirname "$0")"
python3 extract_reserve.py
python3 build_candidates.py
HN_PYTHON=${HN_PYTHON:-.venv/bin/python}
if [ ! -x "$HN_PYTHON" ]; then
    echo "create .venv and install python-sat, or set HN_PYTHON" >&2
    exit 1
fi
"$HN_PYTHON" solve_5color.py rho_union.edge rho_union.5color.txt --json rho_union.sat.json
"$HN_PYTHON" solve_5color.py reserve_union.edge reserve_union.5color.txt --json reserve_union.sat.json
