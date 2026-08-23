#!/usr/bin/env bash
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
build_dir="$(mktemp -d)"
trap 'rm -rf "$build_dir"' EXIT

python3 "$here/generate_certificate.py"
python3 "$here/verify.py"
gcc -O3 -std=c11 -Wall -Wextra -Werror "$here/verify.c" -o "$build_dir/verify"
"$build_dir/verify" "$here/points.csv"
