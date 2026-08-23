#!/bin/sh
set -eu
cd "$(dirname "$0")"
python3 verify_exact.py
tmp_dir=$(mktemp -d)
gcc -O2 -std=c11 -Wall -Wextra -pedantic -o "$tmp_dir/verify_coloring" verify_coloring.c
"$tmp_dir/verify_coloring" rho_union.edge rho_union.5color.txt 933 4651
"$tmp_dir/verify_coloring" reserve_union.edge reserve_union.5color.txt 1186 7440
echo "q1 replay complete"
