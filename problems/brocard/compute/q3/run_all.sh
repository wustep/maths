#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
tmp_dir=$(mktemp -d)
trap 'rm -rf "$tmp_dir"' EXIT

python3 offset_families.py --prime-bound 10000
gcc -O3 -std=c11 -Wall -Wextra -Werror verify_offset.c -o "$tmp_dir/verify_offset"
"$tmp_dir/verify_offset" 10000 > c-sample.txt
diff -u python-sample.txt c-sample.txt
echo "independent Python/C outputs agree"
