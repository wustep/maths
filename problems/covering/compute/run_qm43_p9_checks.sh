#!/bin/sh
set -eu

HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROBLEM=$(CDPATH= cd -- "$HERE/.." && pwd)
cd "$PROBLEM"

python3 compute/recover_mok.py
python3 compute/verify_H_OK_p9.py

python3 compute/build_qm43_p9.py \
  --output compute/H_R3_r18_n151.txt \
  --manifest compute/qm43_p9_build_manifest.json

gcc -O3 -std=c11 -Wall -Wextra -Werror \
  compute/verify_radius3_matrix.c \
  -o compute/verify_radius3_matrix

# Exhaustive radius-3 sweep of the n=151 matrix (2^18 syndromes).
./compute/verify_radius3_matrix compute/H_R3_r18_n151.txt 18 151

echo "PASS qm43_p9 checks"
