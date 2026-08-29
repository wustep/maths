#!/usr/bin/env bash
# Leftover SAT after q7. Isolated timeouts are residue.
# Usage: ./run_priority.sh [TIME]
set -euo pipefail
cd "$(dirname "$0")"
time_limit="${1:-3600}"
export BATCH_JOBS="${BATCH_JOBS:-2}"
export KISSAT_UNSAT="${KISSAT_UNSAT:-1}"
mkdir -p logs certs/proofs

# Skip 5^5 k=1 (unstored 3.9GB trim) and the 3600s timeouts.
# Hunt leftover names that never got a long unsat run.
./run_batch.sh "$time_limit" \
  p5_c2_k1 p5_c1_k1 \
  p3_c11_k4 p3_c11_k3 \
  p3_c10_k5 p3_c10_k4 p3_c10_k3 \
  p3_c9_k4 p3_c9_k3 \
  p3_c8_k4 p3_c8_k3 \
  p2_c19_k9 p2_c18_k9 \
  p5_c3_k3 p5_c3_k1 \
  p3_c12_k4 p3_c11_k5 \
  p2_c20_k10 \
  p3_c12_k6 p3_c13_k5 \
  p5_c4_k1 p5_c4_k2 \
  p5_c8_k4
