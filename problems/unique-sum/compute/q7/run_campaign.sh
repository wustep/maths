#!/usr/bin/env bash
# One heavy job: dual AP-length ladder at 67, then 71, then 73, then 79.
set -euo pipefail

HERE=$(cd "$(dirname "$0")" && pwd)
PYTHON=${PYTHON:-python3}
LOG=${LOG:-/tmp/unique-sum-q7-campaign.log}
BUILD=${BUILD:-/tmp/unique-sum-q7-build}
mkdir -p "$BUILD"

exec > >(tee -a "$LOG") 2>&1
echo "# campaign start $(date -u +%FT%TZ) log=$LOG"

rustc -D warnings -O "$HERE/verify_exact.rs" -o "$BUILD/exact"
gcc -O3 -march=native -std=c11 -Wall -Wextra -Werror "$HERE/cover_search.c" -o "$BUILD/cover"

run_one() {
    local p="$1" bound="$2"
    echo "# ladder p=$p bound=$bound $(date -u +%FT%TZ)"
    set +e
    "$PYTHON" "$HERE/run_ladder.py" "$BUILD/cover" "$BUILD/exact" "$p" "$bound"
    local rc=$?
    set -e
    echo "# ladder p=$p exit=$rc $(date -u +%FT%TZ)"
    if [ "$rc" -eq 1 ]; then
        echo "SAT_WITNESS p=$p bound=$bound"
        exit 1
    fi
    if [ "$rc" -ne 0 ]; then
        echo "LADDER_INCOMPLETE p=$p exit=$rc"
        exit "$rc"
    fi
}

# Published primes first (matching OEIS is residue). Then 79 if those finish.
run_one 67 15
run_one 71 15
run_one 73 15
echo "# 67/71/73 dual ladders finished $(date -u +%FT%TZ)"
# 79 is absent from OEIS. An exact value here would be a dent.
# Upper search is a separate construction probe; the ladder below assumes
# a candidate bound of 16 (same as 67–73) unless a smaller witness appears.
run_one 79 16
echo "# campaign complete $(date -u +%FT%TZ)"
