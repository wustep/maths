#!/bin/sh
set -eu
cd "$(dirname "$0")"
python3 verify_exact.py
tmp_dir=$(mktemp -d)
gcc -O2 -std=c11 -Wall -Wextra -pedantic -o "$tmp_dir/verify_coloring" ../q1/verify_coloring.c
"$tmp_dir/verify_coloring" rho3_union.edge rho3_union.5color.txt 1357 6860
echo "q2 replay complete"
