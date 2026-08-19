#!/bin/sh
set -eu

HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROBLEM=$(CDPATH= cd -- "$HERE/.." && pwd)
cd "$PROBLEM"

python3 compute/build_lift_partitions.py \
  --seed compute/H_r10_n50.txt \
  --seed-partition result/data/partition_p10.json \
  --matrix18 result/data/H_r18_n815.txt \
  --matrix20 result/data/H_r20_n1631.txt \
  --partition18 compute/partition_r18_n815.txt \
  --partition20 compute/partition_r20_n1631.txt \
  --coarsened18 compute/partition_r18_n815_p17.txt \
  --coarsened20 compute/partition_r20_n1631_p14.txt \
  --manifest compute/lift_partition_manifest.json

Q7C_CHECK_DIR=$(mktemp -d)
trap 'rm -rf -- "$Q7C_CHECK_DIR"' EXIT HUP INT TERM

gcc -O3 -std=c11 -Wall -Wextra -Werror \
  compute/verify_radius2_matrix.c \
  -o "$Q7C_CHECK_DIR/verify_radius2_matrix"

"$Q7C_CHECK_DIR/verify_radius2_matrix" \
  result/data/H_r18_n815.txt 18 815 \
  compute/partition_r18_n815.txt 33

"$Q7C_CHECK_DIR/verify_radius2_matrix" \
  result/data/H_r20_n1631.txt 20 1631 \
  compute/partition_r20_n1631.txt 65

"$Q7C_CHECK_DIR/verify_radius2_matrix" \
  result/data/H_r18_n815.txt 18 815 \
  compute/partition_r18_n815_p17.txt 17

"$Q7C_CHECK_DIR/verify_radius2_matrix" \
  result/data/H_r20_n1631.txt 20 1631 \
  compute/partition_r20_n1631_p14.txt 14
