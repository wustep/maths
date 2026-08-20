#!/bin/sh
set -eu

HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROBLEM=$(CDPATH= cd -- "$HERE/.." && pwd)
TMP_Q8C=$(mktemp -d)
trap 'rm -rf "$TMP_Q8C"' EXIT HUP INT TERM
cd "$PROBLEM"

python3 compute/build_p28_partition.py \
  --parent compute/partition_r28_n26111_p64.txt \
  --output "$TMP_Q8C/partition_r28_n26111_p28.txt"
cmp compute/partition_r28_n26111_p28.txt \
  "$TMP_Q8C/partition_r28_n26111_p28.txt"

gcc -O3 -std=c11 -Wall -Wextra -Werror \
  compute/verify_radius2_matrix.c \
  -o "$TMP_Q8C/verify_radius2_matrix"

"$TMP_Q8C/verify_radius2_matrix" \
  compute/H_r28_n26111.txt 28 26111 \
  compute/partition_r28_n26111_p28.txt 28

N38=$((32 * (26111 + 1) - 1))
test "$N38" -eq 835583
echo "PASS QM_2^2 m=5 direct continuation: 26111 >= 32 >= 28; r=38 n=$N38"
