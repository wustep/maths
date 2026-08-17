#!/bin/sh
set -e
cd "$(dirname "$0")"
python3 check_kernel.py
python3 check_si_group.py
python3 track_bedert.py
python3 verify_certificate.py
python3 hankel_det.py
echo ALL OK
