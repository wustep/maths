#!/bin/sh
# Replay q6 without re-running the long searches. Run from compute/.
set -e
here=$(cd "$(dirname "$0")" && pwd)
cd "$here/.."

echo "== parent 17 still outside the 2,367 =="
python3 verify_new.py certs/new_schemes.json
python3 check_rokhlin.py

echo "== q5 collection encoder checks =="
python3 q5/even_walk.py probe
python3 q5/even_walk.py check-skip 80 40

echo "== q6 even-component count =="
python3 q6/even_components.py

if [ -f q6/certs/new_schemes.json ]; then
  echo "== q6 candidates through the exact verifier =="
  python3 verify_new.py q6/certs/new_schemes.json
else
  echo "no q6/certs/new_schemes.json (no certified candidate)"
fi

if [ -f q6/certs/odd_skel5.json ]; then
  echo "== q6 odd size-5 certificate =="
  python3 -c "import json; r=json.load(open('q6/certs/odd_skel5.json')); assert r['complete'] and r['evals']==37632123; print(r['evals'], 'tuples,', r['distinct_schemes'], 'schemes,', r['hits_on_open_nests'], 'hits')"
fi

if [ -f q6/certs/even_component_a10.json ]; then
  echo "== q6 completed small even component =="
  python3 -c "import json; r=json.load(open('q6/certs/even_component_a10.json')); assert r['complete'] and r['evals']==126336; print(r['evals'], 'collections,', r['distinct'], 'schemes,', r['hits'], 'hits')"
fi

echo "q6 replay finished"
