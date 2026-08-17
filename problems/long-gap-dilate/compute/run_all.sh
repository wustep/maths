#!/bin/sh
# Replay the independent checks. Does not rerun the long SAT census.
set -e
cd "$(dirname "$0")/.."
VENV=compute/.venv/bin/python
$VENV compute/verify.py
$VENV compute/verify_sat_witnesses.py
$VENV compute/enum_diagonal.py
python3 compute/plot_ratios.py
echo OK
