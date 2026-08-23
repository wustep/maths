#!/bin/sh
set -eu
cd "$(dirname "$0")"
python3 build.py
HN_PYTHON=${HN_PYTHON:-../q1/.venv/bin/python}
if [ ! -x "$HN_PYTHON" ]; then
    echo "create ../q1/.venv and install python-sat, or set HN_PYTHON" >&2
    exit 1
fi
"$HN_PYTHON" ../q1/solve_5color.py rho4_combined.edge rho4_combined.5color.txt --json rho4_combined.sat.json
