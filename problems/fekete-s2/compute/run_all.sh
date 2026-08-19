#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 known.py
python3 verify_replay.py
echo
echo "To search (deterministic seeds):"
echo "  python3 optimize.py 7 8 9 10 14 19 24 32 33 46 48"
