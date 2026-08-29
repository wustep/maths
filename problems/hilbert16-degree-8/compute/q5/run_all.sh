#!/bin/sh
# Replay q5: parent 17 still verify; bow-tie collection is the
# nested-box M-scheme; any q5 certificates go through the exact
# Fraction verifier.
set -e
here=$(cd "$(dirname "$0")" && pwd)
cd "$here/.."

echo "== parent 17 still outside the 2,367 =="
python3 verify_new.py certs/new_schemes.json
python3 check_rokhlin.py

echo "== bow-tie collection is the nested-box M-scheme =="
python3 q5/even_walk.py probe

echo "== skip-prefix walk agrees with a short full BFS =="
python3 q5/even_walk.py check-skip 80 40

if [ -f q5/certs/new_schemes.json ]; then
  echo "== q5 candidates through the exact verifier =="
  python3 verify_new.py q5/certs/new_schemes.json
else
  echo "no q5/certs/new_schemes.json (no new scheme this run)"
fi

if [ -f q5/certs/q5_summary.json ]; then
  echo "== q5 summary =="
  python3 -c "import json; print(json.dumps(json.load(open('q5/certs/q5_summary.json')), indent=2)[:2000])"
fi
echo "q5 replay finished"
