#!/usr/bin/env bash
# Problem-level replay: q1 record, q2 residue, q3 leading lift.
set -euo pipefail
cd "$(dirname "$0")"
echo "==> q1"
( cd q1 && ./run_all.sh )
echo "==> q2"
( cd q2 && ./run_all.sh )
echo "==> q3"
( cd q3 && ./run_all.sh )
echo "simon-ionization-excess compute PASS"
