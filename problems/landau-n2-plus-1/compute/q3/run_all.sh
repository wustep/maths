#!/usr/bin/env bash
# Replay the N=10^8 census. From the problem folder:
#   compute/q3/run_all.sh
# Optional first argument: n_max (default 100000000).
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/.." && pwd)
NMAX=${1:-100000000}

python3 "$ROOT/sieve_n2p1.py" --self-test
gcc -O3 -std=c11 -Wall -Wextra "$HERE/sieve_n2p1.c" -o "$HERE/sieve_n2p1"
"$HERE/sieve_n2p1" --self-test

if [ "$NMAX" -ge 100000000 ]; then
    echo "smoke N=2000 (expect primes=209 p2=432)"
    SMOKE=$(mktemp -d)
    "$HERE/sieve_n2p1" 2000 "$SMOKE"
    python3 - "$SMOKE" <<'PY'
import json, sys
m = json.loads(open(sys.argv[1] + "/sieve_meta.json").read())
assert m["count_prime"] == 209, m
assert m["count_p2_omega_eq_2_composite"] == 432, m
assert m["unsplit"] == 0, m
print("smoke OK", m["count_prime"], m["count_p2_omega_eq_2_composite"], "rss_kb", m["rss_kb"])
PY
    rm -rf "$SMOKE"
fi

echo "running C sieve n_max=$NMAX"
"$HERE/sieve_n2p1" "$NMAX" "$HERE"
python3 "$HERE/summarize.py" --dir "$HERE"
python3 "$HERE/check_prefix.py"
gcc -O3 -std=c11 -Wall -Wextra "$HERE/verify_n2p1.c" -o "$HERE/verify_n2p1"
"$HERE/verify_n2p1" "$HERE"
python3 "$HERE/verify_py.py" --dir "$HERE"
python3 "$HERE/plot_from_json.py" --dir "$HERE" --fig "$HERE/counts_vs_bh.png"
cp -f "$HERE/counts_vs_bh.png" "$ROOT/../figures/counts_vs_bh.png"
if [ "$NMAX" -eq 100000000 ]; then
    python3 "$HERE/check_claim.py"
fi
echo "OK n_max=$NMAX"
