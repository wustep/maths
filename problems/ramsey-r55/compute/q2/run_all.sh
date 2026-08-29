#!/bin/sh
# Deterministic q2 replay.  The full two-edit extension pass takes about 10 min.
set -eu
cd "$(dirname "$0")"
mkdir -p certs logs

python3 degree_obstructions.py
python3 verify_encoder.py

gcc -O3 -std=c11 -Wall -Wextra -o two_edit_extend two_edit_extend.c
./two_edit_extend ../refs/r55_42some.g6 328 classify \
  | tee logs/two_edit_classify.txt
grep -q 'final_ok=11136 path0=0 path1=272 path2=10864' \
  logs/two_edit_classify.txt

./two_edit_extend ../refs/r55_42some.g6 328 \
  | tee logs/two_edit_extend.txt
grep -q 'final_ok=11136.*extensions=0' logs/two_edit_extend.txt

./verify_proofs.sh
python3 summarize.py
echo OK
