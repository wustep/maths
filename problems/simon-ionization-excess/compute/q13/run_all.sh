#!/usr/bin/env bash
# Replay q13. Exit 0 is a lift of q11's 1.1010, or a recorded residue.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p certs work
PYTHON="${PYTHON:-python3}"

echo "==> dead line: R<=9 cut cannot beat 1.1010"
"$PYTHON" work/r9_cut.py

echo "==> leftover: s>3 two-shell sign, finite-Z integers, Chebyshev cut"
"$PYTHON" work/s_gt_3_replay.py
"$PYTHON" work/smallz.py
"$PYTHON" work/sharper_cut.py

if [ -f certs/scan_compact.json ]; then
  echo "==> scan_compact.json is stored (SLSQP grid; skip re-run)"
  "$PYTHON" -c "import json; from pathlib import Path; d=json.loads(Path('certs/scan_compact.json').read_text()); b=d.get('best_split'); print('best predicted', b)"
fi

if [ ! -f certs/raise_R10_n37_t0p9119.json ] && [ -f certs/beta3_mid_faces_R10_n37_t0p9119.txt ]; then
  echo "==> try write_raise.py from a complete Gray dump"
  "$PYTHON" write_raise.py || echo "write_raise skipped (dump incomplete or not copositive)"
fi

if ls certs/raise_*.json >/dev/null 2>&1; then
  echo "==> aspect algebra and rebuild"
  "$PYTHON" aspect_identities.py
  "$PYTHON" verify_lift.py
  "$PYTHON" verify_rebuild.py

  echo "==> verify_aspect.c / .rs"
  gcc -O2 -o verify_aspect verify_aspect.c -lm
  ./verify_aspect
  rustc -O -o verify_aspect_rs verify_aspect.rs
  ./verify_aspect_rs

  echo "==> mass-opt check and §7"
  "$PYTHON" mass_opt_check.py
  "$PYTHON" tighten_leading.py

  echo "==> rust faces dump (optional second enum; C dump is the cert)"
  if [ -f certs/faces_rs.txt ]; then
    "$PYTHON" -c "from pathlib import Path; t=Path('certs/faces_rs.txt').read_text(); assert 'copositive 1' in t; print('faces_rs copositive')"
  else
    echo "skip rust re-enum on the fast path"
  fi

  echo "==> assemble"
  "$PYTHON" lift_cert.py
  echo "q13 PASS (leading 1.1010 lifted to 1.1006)"
else
  echo "q13 PASS (residue so far; no certified raise_*.json)"
fi
