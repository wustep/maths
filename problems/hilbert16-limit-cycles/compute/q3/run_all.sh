#!/bin/sh
# Replay every q3 line. Expected: all OK, exit 0.
set -eu
cd "$(dirname "$0")"
./ff-two-well/run.sh
./gg-pt-lyapunov/run.sh
./hh-qh-melnikov/run.sh
./ii-complex-cube/run.sh
./jj-weak-hilbert/run.sh
./kk-plus-one/run.sh
./ll-invariant-line/run.sh
./oo-five-zeros/run.sh
./pp-christopher-lloyd/run.sh
./qq-t2-radial/run.sh
./rr-kolmogorov/run.sh
./ss-cubic-l2/run.sh
./tt-radial-factor/run.sh
echo "q3 ALL OK"
