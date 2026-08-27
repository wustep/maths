#!/bin/sh
# Replay q1 independent checks. Does not rerun the long SAT / anneal searches.
set -e
cd "$(dirname "$0")"
VENV=../.venv/bin/python
if [ ! -x "$VENV" ]; then
  echo "missing compute/.venv; run: python3 -m venv compute/.venv && compute/.venv/bin/pip install python-sat numpy"
  exit 1
fi
$VENV wronskian_slice.py
$VENV verify_q1.py
echo OK
