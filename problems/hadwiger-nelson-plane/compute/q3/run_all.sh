#!/bin/sh
set -eu
cd "$(dirname "$0")"
python3 verify_decomposition.py
tmp_dir=$(mktemp -d)
gcc -O2 -std=c11 -Wall -Wextra -pedantic -o "$tmp_dir/verify_coloring" ../q1/verify_coloring.c
"$tmp_dir/verify_coloring" combined_union.edge combined_union.5color.txt 2010 11766
echo "q3 replay complete"
