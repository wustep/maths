#!/bin/sh
# Replay q1: parent 17 still verify, thicken binary agrees with thickc
# on a rank-6 triangulation, and any q1 certificates go through the
# exact Fraction verifier.
set -e
here=$(cd "$(dirname "$0")" && pwd)
cd "$here/.."

echo "== parent 17 still outside the 2,367 =="
python3 verify_new.py certs/new_schemes.json
python3 check_rokhlin.py

echo "== compile q1/thicken =="
gcc -O3 -march=native -o q1/thicken q1/thicken.c
test -x zonec || cc -O2 -o zonec zonec.c
test -x ballc || cc -O2 -o ballc ballc.c

echo "== thicken radius-1 agrees with parent thickc on rank 6 =="
python3 export_span.py "deg8/o01-p01-n00/(1).pcom" /tmp/q1_r6.task
./thickc /tmp/q1_r6.task 0 1 /tmp/q1_r6_parent.jsonl
./q1/thicken /tmp/q1_r6.task 0 1 /tmp/q1_r6_q1.jsonl 1
python3 - <<'PY'
import json
def summ(path):
    rows = [json.loads(l) for l in open(path)]
    return next(r for r in rows if r["kind"] == "summary")
a, b = summ("/tmp/q1_r6_parent.jsonl"), summ("/tmp/q1_r6_q1.jsonl")
assert a["evals"] == b["evals"] == 64 * 46, (a["evals"], b["evals"])
assert a["complete"] and b["complete"]
assert a["distinct"] == b["distinct"]
print("thicken/thickc rank-6: evals", a["evals"], "distinct", a["distinct"], "ok")
PY

echo "== bow-tie collection is the nested-box M-scheme =="
python3 q1/even_walk.py probe

if [ -f q1/certs/new_schemes.json ]; then
  echo "== q1 candidates through the exact verifier =="
  python3 verify_new.py q1/certs/new_schemes.json
else
  echo "no q1/certs/new_schemes.json (no new scheme this run)"
fi

if [ -f q1/certs/q1_summary.json ]; then
  echo "== q1 summary =="
  python3 -c "import json; print(json.dumps(json.load(open('q1/certs/q1_summary.json')), indent=2)[:2000])"
fi
echo "q1 replay finished"
