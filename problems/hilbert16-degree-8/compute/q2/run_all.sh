#!/bin/sh
# Replay q2: parent 17 still verify, thicken binary agrees with thickc
# on a rank-6 triangulation, and any q2 certificates go through the
# exact Fraction verifier.
set -e
here=$(cd "$(dirname "$0")" && pwd)
cd "$here/.."

echo "== parent 17 still outside the 2,367 =="
python3 verify_new.py certs/new_schemes.json
python3 check_rokhlin.py

echo "== compile q2/thicken =="
gcc -O3 -march=native -o q2/thicken q2/thicken.c
test -x zonec || cc -O2 -o zonec zonec.c

echo "== thicken radius-1 agrees with parent thickc on rank 6 =="
python3 export_span.py "deg8/o01-p01-n00/(1).pcom" /tmp/q2_r6.task
./thickc /tmp/q2_r6.task 0 1 /tmp/q2_r6_parent.jsonl
./q2/thicken /tmp/q2_r6.task 0 1 /tmp/q2_r6_q2.jsonl 1
python3 - <<'PY'
import json
def summ(path):
    rows = [json.loads(l) for l in open(path)]
    return next(r for r in rows if r["kind"] == "summary")
a, b = summ("/tmp/q2_r6_parent.jsonl"), summ("/tmp/q2_r6_q2.jsonl")
assert a["evals"] == b["evals"] == 64 * 46, (a["evals"], b["evals"])
assert a["complete"] and b["complete"]
assert a["distinct"] == b["distinct"]
print("thicken/thickc rank-6: evals", a["evals"], "distinct", a["distinct"], "ok")
PY

echo "== bow-tie collection is the nested-box M-scheme =="
python3 q2/even_walk.py probe

if [ -f q2/certs/new_schemes.json ]; then
  echo "== q2 candidates through the exact verifier =="
  python3 verify_new.py q2/certs/new_schemes.json
else
  echo "no q2/certs/new_schemes.json (no new scheme this run)"
fi

if [ -f q2/certs/q2_summary.json ]; then
  echo "== q2 summary =="
  python3 -c "import json; print(json.dumps(json.load(open('q2/certs/q2_summary.json')), indent=2)[:2000])"
fi
echo "q2 replay finished"
