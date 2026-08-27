#!/bin/sh
# Replay every q1 line. Expected: all OK, exit 0.
set -eu
cd "$(dirname "$0")"
./a-quadratic-five/run.sh
./b-cubic-fourteen/run.sh
./c-chebyshev/run.sh
./d-restricted-upper/run.sh
./e-bezout-bautin/run.sh
echo "q1 ALL OK"
