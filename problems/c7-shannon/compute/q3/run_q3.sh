#!/bin/sh
# Replay the published 367-set, then finish the leftover 8-coset
# Cayley graphs. A 367-set is not a new bound.
set -e
cd "$(dirname "$0")/.."
python3 verify_set.py R367.txt --min-size 367
python3 q2/bound_support.py
gcc -O3 -o q3/search_cosets_finish q3/search_cosets_finish.c -lm
./q3/search_cosets_finish | tee q3/coset_finish_log.txt
python3 q3/sat_leftover_cosets.py
python3 verify_set.py R367.txt --min-size 367
if ls q3/R3*.txt >/dev/null 2>&1; then
  for f in q3/R3*.txt; do
    python3 verify_set.py "$f" --min-size 368 || true
  done
fi
