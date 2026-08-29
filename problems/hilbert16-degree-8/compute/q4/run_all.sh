#!/bin/sh
# Replay q4: parent 17 still verify; bow-tie collection is the
# nested-box M-scheme; any q4 certificates go through the exact
# Fraction verifier.
set -e
here=$(cd "$(dirname "$0")" && pwd)
cd "$here/.."

echo "== parent 17 still outside the 2,367 =="
python3 verify_new.py certs/new_schemes.json
python3 check_rokhlin.py

echo "== bow-tie collection is the nested-box M-scheme =="
python3 q4/even_walk.py probe

if [ -f q4/certs/new_schemes.json ]; then
  echo "== q4 candidates through the exact verifier =="
  python3 verify_new.py q4/certs/new_schemes.json
else
  echo "no q4/certs/new_schemes.json (no new scheme this run)"
fi

if [ -f q4/certs/q4_summary.json ]; then
  echo "== q4 summary =="
  python3 -c "import json; print(json.dumps(json.load(open('q4/certs/q4_summary.json')), indent=2)[:2000])"
fi
echo "q4 replay finished"
