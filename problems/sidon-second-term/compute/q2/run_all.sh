#!/usr/bin/env bash
# Replay q1 record (do not regress), leftover check, and any q2 certificate.
set -euo pipefail
cd "$(dirname "$0")"

python3 leftover_check.py

# Folder record must still replay.
python3 ../verify_certificate.py ../q1/certs/joint_r8_L6.json --beat 0.94325
python3 verify_q2.py ../q1/certs/joint_r8_L6.json --beat 0.94325

CERT=certs/r11_m48_L6.json
python3 ../verify_certificate.py "$CERT" --beat 0.94301
python3 verify_q2.py "$CERT" --beat 0.94301
python3 dump_cert.py "$CERT" certs/r11_m48_L6.txt
gcc -O2 -o verify_q2 verify_q2.c -lgmp
./verify_q2 certs/r11_m48_L6.txt 94301 100000

echo "q2 run_all PASS"
