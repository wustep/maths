#!/bin/sh
# Replay q7 without re-running the long searches. Run from compute/.
set -e
here=$(cd "$(dirname "$0")" && pwd)
cd "$here/.."

echo "== parent 17 still outside the 2,367 =="
python3 verify_new.py certs/new_schemes.json
python3 check_rokhlin.py

echo "== q5/q7 collection encoder checks =="
python3 q7/even_walk.py probe
python3 q7/even_walk.py check-skip 80 40

echo "== q7 C/Python collection evaluator cross-check =="
python3 q7/odd5_export.py
gcc -O3 -std=gnu11 -Wall -Wextra -Wno-unused-function \
  -o q7/odd5c q7/odd5c.c
mkdir -p q7/work
q7/odd5c q7/work/odd5.task 160 161 q7/work/replay_trace.jsonl 0 1
python3 q7/odd5_collect.py --validate-log q7/work/replay_trace.jsonl

echo "== q7 even-component count =="
python3 q7/even_components.py

if [ -f q7/certs/new_schemes.json ]; then
  echo "== q7 candidates through the exact verifier =="
  python3 verify_new.py q7/certs/new_schemes.json
else
  echo "no q7/certs/new_schemes.json (no certified candidate)"
fi

if [ -f q7/certs/odd_skel5.json ]; then
  echo "== q7 odd size-5 certificate =="
  python3 -c "import json; r=json.load(open('q7/certs/odd_skel5.json')); assert r['complete'] and r['evals']==37632123; print(r['evals'], 'tuples,', r['distinct_schemes'], 'schemes,', len(r['hits_on_open_nests']), 'hits')"
fi

if [ -f q7/certs/even_component_17v1_2v1_1.json ]; then
  echo "== q7 nested-box even component =="
  python3 -c "import json; r=json.load(open('q7/certs/even_component_17v1_2v1_1.json')); assert r['complete'] and r['evals']==25292736; print(r['evals'], 'collections,', r['distinct'], 'schemes,', r['hits'], 'hits')"
fi

echo "q7 replay finished"
