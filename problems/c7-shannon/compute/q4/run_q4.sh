#!/bin/sh
# Replay the published 367-set, then the q4 searches that a stranger
# can rerun. A 367-set is not a new bound.
set -e
cd "$(dirname "$0")/.."
python3 verify_set.py R367.txt --min-size 367
gcc -O3 -o q4/search_1dim_cosets q4/search_1dim_cosets.c -lm
./q4/search_1dim_cosets | tee q4/onedim_log.txt
gcc -O3 -o q4/search_cyclic_orbits q4/search_cyclic_orbits.c
./q4/search_cyclic_orbits | tee q4/cyclic_log.txt
gcc -O3 -o q4/search_hamming13_four q4/search_hamming13_four.c
./q4/search_hamming13_four R367.txt | tee q4/hamming13_four_log.txt
gcc -O3 -o q4/search_hamming15 q4/search_hamming15.c
./q4/search_hamming15 R367.txt | tee q4/hamming15_log.txt
python3 verify_set.py R367.txt --min-size 367
if ls q4/R3*.txt >/dev/null 2>&1; then
  for f in q4/R3*.txt; do
    python3 verify_set.py "$f" --min-size 368 || true
  done
fi
