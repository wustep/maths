#!/bin/sh
# Replay every certificate in this folder. Expected: all OK, exit 0.
set -eu
cd "$(dirname "$0")"
./q1/run_all.sh
./q2/run_all.sh
echo "hilbert16-limit-cycles ALL OK"
