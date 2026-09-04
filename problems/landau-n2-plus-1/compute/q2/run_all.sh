#!/usr/bin/env bash
# Replay the N=10^7 census. From the problem folder:
#   compute/q2/run_all.sh
# Optional first argument: n_max (default 10000000).
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/.." && pwd)
NMAX=${1:-10000000}

python3 "$ROOT/sieve_n2p1.py" --self-test
gcc -O3 -std=c11 -Wall -Wextra "$HERE/sieve_n2p1.c" -o "$HERE/sieve_n2p1"
"$HERE/sieve_n2p1" --self-test
echo "running C sieve n_max=$NMAX"
"$HERE/sieve_n2p1" "$NMAX" "$HERE"
python3 "$HERE/summarize.py" --dir "$HERE"
python3 "$HERE/check_prefix.py"
gcc -O3 -std=c11 -Wall -Wextra "$HERE/verify_n2p1.c" -o "$HERE/verify_n2p1"
"$HERE/verify_n2p1" "$HERE"
python3 "$ROOT/verify.py" --dir "$HERE"
python3 "$ROOT/plot_counts.py" --dir "$HERE" --fig "$HERE/counts_vs_bh.png"
cp -f "$HERE/counts_vs_bh.png" "$ROOT/../figures/counts_vs_bh.png"
python3 "$HERE/goldbach_other_other.py"
echo "OK n_max=$NMAX"
