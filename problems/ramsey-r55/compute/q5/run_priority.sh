#!/usr/bin/env bash
# High-value leftover SAT after q4. Isolated timeouts are residue.
# Usage: ./run_priority.sh [TIME]
set -euo pipefail
cd "$(dirname "$0")"
time_limit="${1:-900}"
export BATCH_JOBS="${BATCH_JOBS:-2}"
export KISSAT_UNSAT="${KISSAT_UNSAT:-1}"
mkdir -p logs certs/proofs

# Wave 1: remaining 5^4, then nearby 5^5, then high-cycle order 3.
# Max-cycle order 2/3/5 last; those timed out through q4.
./run_batch.sh "$time_limit" \
  p5_c4_k4 p5_c4_k1 p5_c4_k2 \
  p5_c5_k1 p5_c5_k2 \
  p3_c13_k6 p3_c13_k5 \
  p3_c12_k4 p3_c12_k5 p3_c12_k6 \
  p3_c11_k3 p3_c11_k4 p3_c11_k5 \
  p3_c10_k2 p3_c10_k3 p3_c10_k4 p3_c10_k5 \
  p2_c21_k9 p2_c21_k10 \
  p3_c14_k6 p3_c14_k7 \
  p5_c8_k4
