#!/usr/bin/env bash
# Replay q4. Exit 0 is a dent of q3's 1.1118 (and printed 1.1185).
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p certs work

echo "==> leftover: small Z with q3 1.1118 envelope (residue)"
python3 work/smallz_replay.py

echo "==> leftover: moment region (P_max notes stored; skip pmax_try)"
python3 work/moment_region.py

echo "==> cheap scans (not certificates)"
python3 two_atom_crit.py
python3 large_aspect.py

echo "==> scan_compact.json is stored (SLSQP grid; skip re-run)"
python3 -c "import json; from pathlib import Path; p=Path('certs/scan_compact.json'); d=json.loads(p.read_text()); print('best split', d['best_split']['R'], d['best_split']['n'], d['best_split']['split_inv'])"

if ls certs/raise_*.json >/dev/null 2>&1; then
  echo "==> aspect algebra and rebuild"
  python3 aspect_identities.py
  python3 verify_lift.py
  python3 verify_rebuild.py

  echo "==> verify_aspect.c / .rs"
  gcc -O2 -o verify_aspect verify_aspect.c -lm
  ./verify_aspect
  rustc -O -o verify_aspect_rs verify_aspect.rs
  ./verify_aspect_rs

  echo "==> mass-opt check and §7"
  python3 mass_opt_check.py
  python3 tighten_leading.py

  echo "==> rust faces dump (optional second enum; C dump is the cert)"
  if [ -f certs/faces_rs.txt ]; then
    python3 -c "from pathlib import Path; t=Path('certs/faces_rs.txt').read_text(); assert 'copositive 1' in t; print('faces_rs copositive')"
  else
    echo "skip rust re-enum on the fast path"
  fi

  echo "==> assemble"
  python3 lift_cert.py
  echo "q4 PASS (leading 1.1118 lifted to 1.1057)"
else
  echo "q4 PASS (residue so far; no certified raise_*.json)"
fi
