#!/bin/sh
# Replay the published-constant audit, the {b,1} first-crossing, and the
# official verifier.  Mixture hunt and small-n enum are optional residue.
set -e
cd "$(dirname "$0")"
PY="${PY:-/tmp/ucvenv/bin/python}"
if [ ! -x "$PY" ]; then
  PY=python3
fi
echo "== solve_published =="
"$PY" solve_published.py
echo "== verify (claimed 0.38285) =="
"$PY" verify.py
if [ -f first_crossing.json ]; then
  echo "== plot =="
  "$PY" plot_crossing.py
fi
echo "ALL DONE"
