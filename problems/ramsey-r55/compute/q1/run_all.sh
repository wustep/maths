#!/bin/sh
# Deterministic q1 replay. SAT timeouts are recorded, not treated as a bound.
set -eu
cd "$(dirname "$0")"
mkdir -p certs logs

python3 check_groups.py
python3 srg_params.py
python3 c7_sat.py --selftest

gcc -O3 -std=c11 -o cayley_census cayley_census.c
gcc -O3 -std=c11 -o extend_flips extend_flips.c

# Parent circulants at 44 and 45 (already empty in the 2026-08-17 census).
gcc -O3 -std=c11 -o ../circulant_census ../circulant_census.c
../circulant_census 44 | tee logs/circ44.txt | tail -1
../circulant_census 45 | tee logs/circ45.txt | tail -1

for g in c2c22 d22 c11c4 c3c15; do
  echo "=== cayley $g ==="
  ./cayley_census "$g" | tee "logs/cayley_${g}.txt" | tail -2
done

python3 py_cayley.py c11c4
python3 py_cayley.py c3c15
python3 verify_cayley.py

echo "=== aut of the 656 ==="
python3 aut_mckay.py

echo "=== 1-flip then extend ==="
./extend_flips ../refs/r55_42some.g6 | tee logs/extend_flips.txt | tail -3

echo "=== radius-2 1-flips ==="
python3 two_flip.py

echo "=== C7 SAT self-contained n=14 (small) ==="
timeout 60 python3 c7_sat.py --n 14 --no-card --solve || true

echo "=== C7 SAT n=42 (timeout is UNKNOWN, not a bound) ==="
timeout 180 python3 c7_sat.py --n 42 --solve || echo "c7 n=42 timeout/nonzero"

echo "=== C7 SAT n=43 (timeout is UNKNOWN, not a bound) ==="
timeout 180 python3 c7_sat.py --n 43 --solve || echo "c7 n=43 timeout/nonzero"

python3 summarize.py
echo OK
