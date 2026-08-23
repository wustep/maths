#!/usr/bin/env bash
set -euo pipefail

here=$(cd "$(dirname "$0")" && pwd)
compute="$here/.."
scratch=$(mktemp -d)
cleanup() {
    rm -f -- "$scratch/n73.txt" "$scratch/verify_lines"
    rmdir -- "$scratch"
}
trap cleanup EXIT

cd "$here"
sha256sum --check SHA256SUMS

python3 "$compute/q3/decode_database.py" --n 73 \
    "$here/n73-rct4.code" "$scratch/n73.txt"
python3 "$compute/verify_n71.py" --n 73 "$scratch/n73.txt"
python3 "$here/prepare_n73_phase.py"
python3 "$here/search_small_repair.py"
python3 "$compute/audit_dimacs.py" "$here/n75-rct4.cnf"

if [[ -f "$here/n75-150.txt" ]]; then
    python3 "$compute/verify_n71.py" --n 75 "$here/n75-150.txt"
    rustc "$compute/q3/verify_lines.rs" -O -o "$scratch/verify_lines"
    "$scratch/verify_lines" "$here/n75-150.txt" 75
    echo "ALL CERTIFICATE CHECKS PASSED"
else
    echo "NO n=75 CERTIFICATE; inspect the committed run metadata for residue"
fi
