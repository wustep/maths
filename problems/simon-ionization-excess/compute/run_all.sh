#!/usr/bin/env bash
# Problem-level replay: q1 record, q2 residue, q3–q5 leading lifts.
set -euo pipefail
cd "$(dirname "$0")"
echo "==> q1"
( cd q1 && ./run_all.sh )
echo "==> q2"
( cd q2 && ./run_all.sh )
echo "==> q3"
( cd q3 && ./run_all.sh )
echo "==> q4"
( cd q4 && ./run_all.sh )
echo "==> q5"
( cd q5 && ./run_all.sh )
echo "simon-ionization-excess compute PASS"
