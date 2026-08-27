#!/bin/sh
# Replay q1 certificates. Regenerates them first so a stranger can
# check the search, then verifies the listed holes and the failure
# families.
set -e
here=$(cd "$(dirname "$0")" && pwd)
cd "$here"
export PYTHONPATH="$here/..${PYTHONPATH:+:$PYTHONPATH}"

echo "== polynomial size obstruction =="
python3 poly_obstruction.py

echo "== infinite failure families =="
python3 infinite_family.py

echo "== closed-form / two-factor census =="
python3 search.py

echo "== replay listed holes =="
python3 verify.py
echo "q1 replay finished"
