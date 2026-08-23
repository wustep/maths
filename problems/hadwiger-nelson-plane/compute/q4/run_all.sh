#!/bin/sh
set -eu
cd "$(dirname "$0")"
python3 verify_extension.py
tmp_dir=$(mktemp -d)
gcc -O2 -std=c11 -Wall -Wextra -pedantic -o "$tmp_dir/verify_coloring" ../q1/verify_coloring.c
"$tmp_dir/verify_coloring" rho4_combined.edge rho4_combined.5color.txt 2434 13975
echo "q4 replay complete"
