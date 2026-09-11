#!/bin/sh
# Replay the published-509 certificate.
#   * exact unit-distance rebuild (must get 509 vertices, 2442 edges)
#   * if color509.drat is local, rebuild the 4-color CNF and check it
set -eu
cd "$(dirname "$0")"
PY="${PY:-./.venv/bin/python}"
if [ ! -x "$PY" ]; then
  echo "create a venv and pip install sympy python-sat, or set PY=" >&2
  exit 1
fi
"$PY" verify_graph.py 509_parts.vtx --expect-n 509 --expect-m 2442 --edges-out edges_509.txt
if [ -f color509.drat ]; then
  "$PY" check_certificate.py 509_parts.vtx color509.drat --expect-n 509 --expect-m 2442 --cnf-out color509.rebuilt.cnf
  echo "certificate replayed"
else
  echo "color509.drat not in tree; graph rebuilt. See STORAGE.md to regenerate the coloring proof."
fi
