#!/usr/bin/env bash
# Problem-level replay: q1 record, then q2 residue.
set -euo pipefail
cd "$(dirname "$0")"
echo "==> q1"
( cd q1 && ./run_all.sh )
echo "==> q2"
( cd q2 && ./run_all.sh )
echo "simon-ionization-excess compute PASS"
