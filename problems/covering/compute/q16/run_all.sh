#!/bin/sh
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROBLEM=$(CDPATH= cd -- "$HERE/../.." && pwd)
BUILD_DIR=$(mktemp -d)
trap 'rm -rf "$BUILD_DIR"' EXIT HUP INT TERM
cd "$PROBLEM"
python3 compute/q16/build_qm43_m5.py
cc -O3 -std=c11 -Wall -Wextra -Werror compute/q16/verify_q16.c -o "$BUILD_DIR/verify_q16"
"$BUILD_DIR/verify_q16" compute/H_R3_r26_n817.txt \
  compute/q16/partition_r26_n817_p33.txt compute/q16/H_R3_r41_n26175.txt
cc -O3 -std=c11 -Wall -Wextra -Werror compute/q16/delete_screen.c -o "$BUILD_DIR/delete_screen"
"$BUILD_DIR/delete_screen" compute/H_R3_r26_n817.txt \
  compute/q16/partition_r26_n817_p33.txt
"$BUILD_DIR/delete_screen" compute/H_R3_r26_n817.txt \
  compute/q16/partition_r26_n817_p33.txt plain
echo "PASS q16: ell_2(41,3) <= 26175"
