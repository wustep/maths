#!/usr/bin/env bash
# Replay q2 small-Z attempts. Exit 0 is residue, not a dent.
set -euo pipefail
cd "$(dirname "$0")"
python3 envelopes.py
python3 envelopes_check.py
python3 geometric_alpha.py
python3 alpha_n.py
python3 alpha_n_check.py
python3 lieb_weights.py
python3 nam_smallz.py
python3 temple_try.py
python3 assemble_cert.py
echo "q2 run_all.sh PASS (residue; no certified finite-Z dent)"
