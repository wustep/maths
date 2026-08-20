#!/bin/sh
set -eu

HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROBLEM=$(CDPATH= cd -- "$HERE/.." && pwd)
cd "$PROBLEM"

python3 compute/recover_mok.py

python3 compute/build_qm43.py \
  --output compute/H_R3_r21_n303.txt \
  --manifest compute/qm43_build_manifest.json

gcc -O3 -std=c11 -Wall -Wextra -Werror \
  compute/verify_radius3_matrix.c \
  -o compute/verify_radius3_matrix

python3 compute/verify_qm43_identity.py \
  --matrix compute/H_R3_r21_n303.txt

compute/verify_radius3_matrix compute/H_R3_r21_n303.txt 21 303
