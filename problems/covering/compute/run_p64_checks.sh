#!/bin/sh
set -eu

HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROBLEM=$(CDPATH= cd -- "$HERE/.." && pwd)
cd "$PROBLEM"

gcc -O3 -std=c11 -Wall -Wextra -Werror \
  compute/search_partition_merges.c \
  -o compute/search_partition_merges

compute/search_partition_merges \
  compute/H_r28_n26111.txt 28 26111 \
  compute/partition_r28_n26111.txt 66 \
  compute/partition_r28_n26111_p64.txt

gcc -O3 -std=c11 -Wall -Wextra -Werror \
  compute/verify_radius2_matrix.c \
  -o compute/verify_radius2_matrix

compute/verify_radius2_matrix \
  compute/H_r28_n26111.txt 28 26111 \
  compute/partition_r28_n26111_p64.txt 64

N40=$((64 * (26111 + 1) - 1))
test "$N40" -eq 1671167
echo "PASS QM_2^2 m=6 theorem continuation: r=40 n=$N40"
