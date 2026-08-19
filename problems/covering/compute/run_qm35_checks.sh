#!/bin/sh
set -eu

HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROBLEM=$(CDPATH= cd -- "$HERE/.." && pwd)
cd "$PROBLEM"

python3 compute/build_qm35.py \
  --radius2 compute/H_r10_n50.txt \
  --output compute/H_R3_r26_n817.txt \
  --manifest compute/qm35_build_manifest.json

gcc -O3 -std=c11 -Wall -Wextra -Werror \
  compute/verify_three_sum.c \
  -o compute/verify_three_sum

gcc -O3 -std=c11 -Wall -Wextra -Werror \
  compute/verify_radius3_matrix.c \
  -o compute/verify_radius3_matrix

compute/verify_three_sum compute/H_r10_n50.txt 10 50
compute/verify_radius3_matrix compute/H_R3_r26_n817.txt 26 817
