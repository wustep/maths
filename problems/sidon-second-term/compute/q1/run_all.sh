#!/usr/bin/env bash
# Replay q1 baselines and the rational certificate in this folder.
set -euo pipefail
cd "$(dirname "$0")"

python3 - <<'PY'
from pathlib import Path
import sys
sys.path.insert(0, str(Path('.').resolve().parents[0]))
from vector_smoothing import solve_boundary_qp
ns = {}
exec(Path('../refs/sidon_numerical_search.py').read_text(), ns)
ker, lam = ns['stored_candidates']()[8]
_, _, a4, b4, g4 = solve_boundary_qp(ker, lam, 4)
_, _, a6, b6, g6 = solve_boundary_qp(ker, lam, 6)
print(f'replay R=8 L=4  gamma={g4:.12f}')
print(f'replay R=8 L=6  gamma={g6:.12f}')
if abs(g4 - 0.94349259006) > 5e-11:
    raise SystemExit(f'FAIL L=4 replay {g4}')
if abs(g6 - 0.94349250848) > 5e-11:
    raise SystemExit(f'FAIL L=6 replay {g6}')
print('QP replay PASS')
PY

python3 ../verify_houzhao.py
python3 ../verify_certificate.py ../certs/hz_kernels_L6.json --beat 0.94349259
python3 ../verify_beat_hz.py

CERT=certs/joint_r8_L6.json
python3 ../verify_certificate.py "$CERT" --beat 0.94325
python3 verify_q1.py "$CERT" --beat 0.94325
python3 dump_cert.py "$CERT" certs/joint_r8_L6.txt
gcc -O2 -o verify_q1 verify_q1.c -lgmp
./verify_q1 certs/joint_r8_L6.txt 94325 100000
echo "q1 run_all PASS"
