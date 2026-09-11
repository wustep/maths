#!/bin/sh
set -eu

HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROBLEM=$(CDPATH= cd -- "$HERE/../.." && pwd)
BUILD_DIR=$(mktemp -d)
trap 'rm -rf "$BUILD_DIR"' EXIT HUP INT TERM
cd "$PROBLEM"

python3 compute/q13/build_qm43.py \
  --seed compute/H_R3_r26_n817.txt \
  --radius2 compute/H_r10_n50.txt \
  --radius2-partition result/data/partition_p10.json \
  --coarse-partition compute/q13/partition_r26_n817_p34.txt \
  --refined-partition compute/q13/partition_r26_n817_p65.txt \
  --output compute/q13/H_R3_r44_n52351.txt \
  --manifest compute/q13/manifest.json

cc -O3 -std=c11 -Wall -Wextra -Werror \
  compute/q13/verify_q13.c \
  -o "$BUILD_DIR/verify_q13"

"$BUILD_DIR/verify_q13" \
  compute/H_R3_r26_n817.txt \
  compute/q13/partition_r26_n817_p34.txt \
  compute/q13/partition_r26_n817_p65.txt \
  compute/q13/H_R3_r44_n52351.txt

echo "PASS q13: ell_2(44,3) <= 52351"
