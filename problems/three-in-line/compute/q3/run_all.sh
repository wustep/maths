#!/usr/bin/env bash
set -euo pipefail

here=$(cd "$(dirname "$0")" && pwd)
witness="$here/../n71-142.txt"
scratch=$(mktemp -d)
cleanup() {
    rm -f -- "$scratch/decoded.txt" "$scratch/verify_lines"
    rmdir -- "$scratch"
}
trap cleanup EXIT

cd "$here"
sha256sum --check SHA256SUMS
python3 decode_database.py n71-rct4.code "$scratch/decoded.txt"
cmp --silent "$scratch/decoded.txt" "$witness"
echo "MATCH decoded database entry == committed witness"

python3 ../verify_n71.py "$witness"
rustc verify_lines.rs -O -o "$scratch/verify_lines"
"$scratch/verify_lines" "$witness"

echo "ALL CHECKS PASSED"
