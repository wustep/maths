#!/usr/bin/env bash
# Replay q1 record (do not regress), leftover check, and any q2 certificate.
set -euo pipefail
cd "$(dirname "$0")"

python3 leftover_check.py

# Folder record must still replay.
python3 ../verify_certificate.py ../q1/certs/joint_r8_L6.json --beat 0.94325
python3 verify_q2.py ../q1/certs/joint_r8_L6.json --beat 0.94325

CERT=""
if [[ -f certs/best.json ]]; then
  CERT=certs/best.json
fi

if [[ -n "$CERT" ]]; then
  python3 ../verify_certificate.py "$CERT" --beat 0.94325
  python3 verify_q2.py "$CERT" --beat 0.94325
  python3 dump_cert.py "$CERT" certs/best.txt
  gcc -O2 -o verify_q2 verify_q2.c -lgmp
  # Default stated target; a tighter --beat is documented in README when used.
  ./verify_q2 certs/best.txt 94325 100000
fi

echo "q2 run_all PASS"
