#!/bin/sh
# Replay the published-509 certificate.
#   * exact unit-distance rebuild (must get 509 vertices, 2442 edges)
#   * rebuild the 4-color CNF
#   * check the stored DRAT proof with drat-trim
set -eu
cd "$(dirname "$0")"
PY="${PY:-./.venv/bin/python}"
if [ ! -x "$PY" ]; then
  echo "create a venv and pip install sympy python-sat, or set PY=" >&2
  exit 1
fi
"$PY" verify_graph.py 509_parts.vtx --expect-n 509 --expect-m 2442 --edges-out edges_509.txt
"$PY" check_certificate.py 509_parts.vtx color509.drat --expect-n 509 --expect-m 2442 --cnf-out color509.rebuilt.cnf
echo "certificate replayed"
