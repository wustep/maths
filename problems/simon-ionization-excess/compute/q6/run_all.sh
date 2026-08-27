#!/usr/bin/env bash
# Replay q6. Exit 0 is a dent of q5's 1.1035, or a recorded residue.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p certs work

echo "==> dead line: R<=9 cut cannot beat 1.1035"
python3 work/r9_cut.py

echo "==> leftover: s>3 two-shell sign and finite-Z integers"
python3 work/s_gt_3_replay.py
python3 work/smallz.py

if [ -f certs/scan_compact.json ]; then
  echo "==> scan_compact.json is stored (SLSQP grid; skip re-run)"
  python3 -c "import json; from pathlib import Path; d=json.loads(Path('certs/scan_compact.json').read_text()); b=d.get('best_split'); print('best predicted', b)"
fi

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
  echo "q6 PASS (leading 1.1035 lifted)"
else
  echo "q6 PASS (residue so far; no certified raise_*.json)"
fi
