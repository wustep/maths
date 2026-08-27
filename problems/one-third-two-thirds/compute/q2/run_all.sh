#!/bin/bash
# Replay q2 certificates. Exit 0 is the check a stranger runs.
# Full enumerations are the C binaries, not this script.
set -euo pipefail
cd "$(dirname "$0")"

python3 verify_published.py
python3 verify_winners.py

echo "q2 ALL CHECKS PASSED"
