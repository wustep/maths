#!/usr/bin/env bash
# Replay q2. Exit 0 is residue, not a dent of 1.1185.
set -euo pipefail
cd "$(dirname "$0")"

echo "==> small-Z envelopes and failed Nc(2)<4 attempts"
python3 envelopes.py
python3 envelopes_check.py
python3 geometric_alpha.py
python3 verify_tetra.py
cc -O2 -o /tmp/verify_tetra_q2 verify_tetra.c && /tmp/verify_tetra_q2
python3 alpha_n.py
python3 alpha_n_check.py
python3 lieb_weights.py
python3 nam_smallz.py
python3 temple_try.py
python3 assemble_cert.py
echo "q2 small-Z PASS (residue; Lieb still best at Z=2,3,4,5)"

echo "==> s>3 radialization"
bash run_s_gt_3.sh

echo "==> beta3 compact / withdrawn lift"
bash run_beta3.sh

echo "q2 PASS (residue; leading coefficient still 1.1185)"
