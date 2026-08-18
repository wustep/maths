#!/bin/sh
# q4: harvest diverse 7-hole local optima.  Runs the q2 SA binary with
# distinct deterministic seeds for a fixed budget each, extracts the
# checkpoint configuration, and stores it under optima/.  Dedup and
# k-swap proving happen in Python afterwards (dedupe_optima.py).
set -u
cd "$(dirname "$0")/../.." || exit 2
mkdir -p compute/q4/optima
SECONDS_EACH="${SECONDS_EACH:-420}"
THREADS="${THREADS:-4}"
for seed in 0x1111111111111111 0x2222222222222222 0x3333333333333333 \
            0x4444444444444444 0x5555555555555555 0x6666666666666666 \
            0x7777777777777777 0x8888888888888888 0x9999999999999999 \
            0xAAAAAAAAAAAAAAAA 0xBBBBBBBBBBBBBBBB 0xCCCCCCCCCCCCCCCC; do
    out="compute/q4/optima/ckpt_$seed.json"
    [ -f "$out" ] && continue
    ./compute/q4/search_n49 --seconds "$SECONDS_EACH" --threads "$THREADS" \
        --seed "$seed" --input compute/H_r10_n50.txt --output "$out" \
        > "compute/q4/optima/log_$seed.txt" 2>&1
    tail -n 1 "compute/q4/optima/log_$seed.txt"
done
echo harvest done
