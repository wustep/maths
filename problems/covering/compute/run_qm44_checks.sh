#!/bin/sh
set -eu

HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROBLEM=$(CDPATH= cd -- "$HERE/.." && pwd)
cd "$PROBLEM"

python3 compute/build_qm44.py \
  --radius2 compute/H_r10_n50.txt \
  --output compute/H_R4_r31_n689.txt \
  --certificate compute/qm44_top_certificate.txt \
  --manifest compute/qm44_build_manifest.json

gcc -O3 -std=c11 -Wall -Wextra -Werror \
  compute/verify_qm44.c \
  -o compute/verify_qm44

compute/verify_qm44 \
  compute/H_R4_r31_n689.txt \
  compute/H_r10_n50.txt \
  compute/qm44_top_certificate.txt
