#!/bin/sh
set -eu

HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROBLEM=$(CDPATH= cd -- "$HERE/.." && pwd)
cd "$PROBLEM"

python3 compute/build_qm21.py \
  --seed result/data/H_r18_n815.txt \
  --partition compute/partition_r18_n815_p17.txt \
  --output compute/H_r26_n13070.txt \
  --labels compute/partition_r26_n13070_p17.txt \
  --manifest compute/qm21_build_manifest.json

gcc -O3 -std=c11 -Wall -Wextra -Werror \
  compute/verify_radius2_matrix.c \
  -o compute/verify_radius2_matrix

python3 compute/verify_qm21_identity.py \
  --seed result/data/H_r18_n815.txt \
  --seed-partition compute/partition_r18_n815_p17.txt \
  --matrix compute/H_r26_n13070.txt

compute/verify_radius2_matrix result/data/H_r18_n815.txt 18 815 \
  compute/partition_r18_n815_p17.txt 17

compute/verify_radius2_matrix compute/H_r26_n13070.txt 26 13070
