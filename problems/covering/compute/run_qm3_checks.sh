#!/bin/sh
set -eu

HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROBLEM=$(CDPATH= cd -- "$HERE/.." && pwd)
cd "$PROBLEM"

python3 compute/build_qm3.py \
  --seed compute/H_r10_n50.txt \
  --partition result/data/partition_p10.json \
  --outdir compute \
  --manifest compute/qm3_build_manifest.json

gcc -O3 -std=c11 -Wall -Wextra \
  compute/verify_radius2_matrix.c \
  -o compute/verify_radius2_matrix

compute/verify_radius2_matrix compute/H_r22_n3325.txt 22 3325
compute/verify_radius2_matrix compute/H_r24_n6653.txt 24 6653
compute/verify_radius2_matrix compute/H_r26_n13309.txt 26 13309
