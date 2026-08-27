#!/bin/sh
# Replay line A: drop H(2) ≥ 5, certify Shi V1 = V2 = 0, V3 = 35625/8.
set -eu
cd "$(dirname "$0")"

python3 lyapunov.py
python3 verify.py

gcc -O3 -std=c11 -Wall -Wextra -Werror -o verify_c verify.c
./verify_c

echo "a-quadratic-five OK"
