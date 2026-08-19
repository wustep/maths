#!/bin/sh
set -eu

HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROBLEM=$(CDPATH= cd -- "$HERE/.." && pwd)
cd "$PROBLEM"

python3 compute/build_qm5.py \
  --seed compute/H_r10_n50.txt \
  --partition result/data/partition_p10.json \
  --outdir compute \
  --manifest compute/qm5_build_manifest.json

gcc -O3 -std=c11 -Wall -Wextra \
  compute/verify_radius2_matrix.c \
  -o compute/verify_radius2_matrix

compute/verify_radius2_matrix \
  compute/H_r18_n815_qm5_seed.txt 18 815 \
  compute/partition_r18_n815_qm5.txt 33
compute/verify_radius2_matrix \
  compute/H_r28_n26111.txt 28 26111 \
  compute/partition_r28_n26111.txt 66
