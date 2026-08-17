#!/bin/sh
set -e
cd "$(dirname "$0")"
python3 verify_interval.py
python3 verify_half.py
python3 plot_constants.py
echo "all checks passed"
