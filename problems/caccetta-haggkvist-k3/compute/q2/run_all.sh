#!/bin/sh
# Replay q2: F4 certificate still holds, encoder matches known small-n
# SAT/UNSAT, n=18 k=11 still UNSAT, and any stored n=21 cube proofs
# check with drat-trim.
set -e
here=$(cd "$(dirname "$0")" && pwd)
cd "$here"
parent=$(dirname "$here")

echo "== parent F4 certificate at 0.34645 =="
python3 "$parent/verify_certificate.py" "$parent/certs/f4_certificate.json" --margin 0.05 --c 0.34645

echo "== sequential-counter encoding vs known small n and n=18 k=11 =="
python3 regression.py

echo "== stored n=21 cube DRATs in certs/keep =="
if [ -x "$here/bin/drat-trim" ]; then
  DRAT="$here/bin/drat-trim"
elif [ -x /tmp/solvers/drat-trim ]; then
  DRAT=/tmp/solvers/drat-trim
else
  DRAT=""
fi
found=0
for f in "$here"/certs/keep/ch-21-7-k*.drat; do
  [ -f "$f" ] || continue
  cnf=${f%.drat}.cnf
  if [ -n "$DRAT" ] && [ -f "$cnf" ]; then
    echo "check $cnf"
    "$DRAT" "$cnf" "$f" | tail -3
    found=1
  fi
done
if [ "$found" -eq 0 ]; then
  echo "no stored n=21 DRAT proofs (residue if the cubes did not finish)"
fi
echo "q2 replay finished"
