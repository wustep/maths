#!/bin/sh
# Replay the support bound, then the remaining 8-coset / Hamming-11 / ejection
# searches. A 367-set is not a new bound.
set -e
cd "$(dirname "$0")/.."
python3 verify_set.py R367.txt --min-size 367
python3 q2/bound_support.py
gcc -O3 -o q2/search_cosets_exact q2/search_cosets_exact.c
gcc -O3 -o q2/search_hamming11 q2/search_hamming11.c
gcc -O3 -o q2/search_ejection q2/search_ejection.c
./q2/search_cosets_exact | tee q2/coset_exact_log.txt
./q2/search_hamming11 R367.txt | tee q2/hamming11_log.txt
python3 q2/search_hamming11_sat.py
./q2/search_ejection R367.txt 250000 16 | tee q2/ejection_log.txt
python3 verify_set.py R367.txt --min-size 367
if ls q2/R3*.txt >/dev/null 2>&1; then
  for f in q2/R3*.txt; do
    python3 verify_set.py "$f" --min-size 368 || true
  done
fi
