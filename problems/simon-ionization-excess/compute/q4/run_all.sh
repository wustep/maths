#!/usr/bin/env bash
# Replay q4 probes. Exit 0 is residue until a stored face dump
# plus §7 chain beat 1.1118; then this script becomes the dent path.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p certs work

echo "==> leftover: small Z with q3 1.1118 envelope (residue)"
python3 work/smallz_replay.py

echo "==> leftover: moment region / P_max notes"
python3 work/moment_region.py
python3 work/pmax_try.py

echo "==> cheap scans (not certificates)"
python3 two_atom_crit.py
python3 large_aspect.py

echo "==> scan_compact.json is stored (SLSQP grid; skip re-run)"
python3 -c "import json; from pathlib import Path; p=Path('certs/scan_compact.json'); d=json.loads(p.read_text()); print('best split', d['best_split']['R'], d['best_split']['n'], d['best_split']['split_inv'])"

if [ -f certs/lift.json ]; then
  echo "==> stored lift"
  python3 verify_lift.py
  python3 tighten_leading.py
  python3 lift_cert.py
  echo "q4 PASS (leading below 1.1118)"
else
  echo "q4 PASS (residue so far; no stored lift.json)"
fi
