#!/bin/sh
set -eu

HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROBLEM=$(CDPATH= cd -- "$HERE/../.." && pwd)
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT HUP INT TERM
cd "$PROBLEM"

python3 compute/q15/build_qm43_m5.py \
  compute/H_R3_r26_n817.txt \
  compute/q15/partition_r26_n817_p33.txt \
  "$WORK/H_r41.txt" "$WORK/manifest_m5.json"
cmp compute/q15/manifest_m5.json "$WORK/manifest_m5.json"
cc -O3 -std=c11 -Wall -Wextra -Werror \
  compute/q15/verify_q15_m5.c -o "$WORK/verify_m5"
"$WORK/verify_m5" \
  compute/H_R3_r26_n817.txt \
  compute/q15/partition_r26_n817_p33.txt \
  compute/q15/partition_r26_n817_p33.txt \
  "$WORK/H_r41.txt"

python3 compute/q15/build_qm43_m7.py \
  compute/H_R3_r26_n817.txt \
  compute/q13/partition_r26_n817_p65.txt \
  "$WORK/partition129.txt" "$WORK/H_r47.txt" "$WORK/manifest_m7.json"
cmp compute/q15/partition_r26_n817_p129.txt "$WORK/partition129.txt"
cmp compute/q15/manifest.json "$WORK/manifest_m7.json"
cc -O3 -std=c11 -Wall -Wextra -Werror \
  compute/q15/verify_q15.c -o "$WORK/verify_m7"
"$WORK/verify_m7" \
  compute/H_R3_r26_n817.txt \
  compute/q13/partition_r26_n817_p34.txt \
  "$WORK/partition129.txt" "$WORK/H_r47.txt"

echo 'PASS q15: ell_2(41,3) <= 26175 and ell_2(47,3) <= 104703'
