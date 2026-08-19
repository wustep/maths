#!/bin/sh
set -eu

HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROBLEM=$(CDPATH= cd -- "$HERE/.." && pwd)
cd "$PROBLEM"

python3 compute/build_qm35.py \
  --radius2 compute/H_r10_n50.txt \
  --radius2 result/data/H_r18_n815.txt \
  --radius2 result/data/H_r20_n1631.txt \
  --output compute/H_R3_r26_n817.txt \
  --output compute/H_R3_r38_n13102.txt \
  --output compute/H_R3_r41_n26206.txt \
  --manifest compute/qm35_build_manifest.json

gcc -O3 -std=c11 -Wall -Wextra -Werror \
  compute/verify_three_sum.c \
  -o compute/verify_three_sum

gcc -O3 -std=c11 -Wall -Wextra -Werror \
  compute/verify_radius2_matrix.c \
  -o compute/verify_radius2_matrix

gcc -O3 -std=c11 -Wall -Wextra -Werror \
  compute/verify_radius3_matrix.c \
  -o compute/verify_radius3_matrix

compute/verify_three_sum compute/H_r10_n50.txt 10 50
compute/verify_radius2_matrix compute/H_r10_n50.txt 10 50
compute/verify_radius2_matrix result/data/H_r18_n815.txt 18 815
compute/verify_radius2_matrix result/data/H_r20_n1631.txt 20 1631

compute/verify_radius3_matrix compute/H_R3_r26_n817.txt 26 817

python3 compute/verify_qm35_identity.py \
  --radius2 compute/H_r10_n50.txt \
  --matrix compute/H_R3_r26_n817.txt \
  --m 5 \
  --published 818

python3 compute/verify_qm35_identity.py \
  --radius2 result/data/H_r18_n815.txt \
  --matrix compute/H_R3_r38_n13102.txt \
  --m 9 \
  --published 13118

python3 compute/verify_qm35_identity.py \
  --radius2 result/data/H_r20_n1631.txt \
  --matrix compute/H_R3_r41_n26206.txt \
  --m 10 \
  --published 26238
