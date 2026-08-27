#!/bin/sh
# Replay every q2 line, then q1. Expected: all OK, exit 0.
set -eu
cd "$(dirname "$0")"
./f-homogeneous/run.sh
./i-lienard/run.sh
./o-iterated-squaring/run.sh
./p-harnack-recurrence/run.sh
./q-pt-darboux/run.sh
echo "q2 ALL OK"
