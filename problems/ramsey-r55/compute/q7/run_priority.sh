#!/usr/bin/env bash
# Leftover SAT after q6. Isolated timeouts are residue.
# Usage: ./run_priority.sh [TIME]
set -euo pipefail
cd "$(dirname "$0")"
time_limit="${1:-3600}"
export BATCH_JOBS="${BATCH_JOBS:-2}"
export KISSAT_UNSAT="${KISSAT_UNSAT:-1}"
mkdir -p logs certs/proofs

# Wave 1: 5^5 at k=1 remains UNKNOWN after 3600s; lengthen first.
# Wave 2: remaining order-5 that timed out at 1800s (5^3).
# Wave 3: high-cycle order 3 that timed out at 1800s.
# Wave 4: leftover order-5 that only saw 180s --plain.
# The five max-cycle formulas and other q5/q6 1800s timeouts are last.
./run_batch.sh "$time_limit" \
  p5_c5_k1 \
  p5_c3_k3 p5_c3_k1 \
  p3_c12_k6 p3_c13_k5 \
  p5_c2_k2 p5_c2_k1 \
  p5_c1_k1 \
  p3_c12_k4 p3_c12_k5 \
  p3_c11_k3 p3_c11_k4 p3_c11_k5 \
  p3_c10_k2 p3_c10_k3 p3_c10_k4 p3_c10_k5 \
  p2_c21_k9 p2_c21_k10 \
  p3_c13_k6 p3_c14_k6 p3_c14_k7 \
  p5_c4_k1 p5_c4_k2 \
  p5_c8_k4
