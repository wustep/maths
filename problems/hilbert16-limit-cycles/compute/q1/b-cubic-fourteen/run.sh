#!/bin/sh
set -eu
cd "$(dirname "$0")"
python3 verify.py --write certificate.json
python3 verify.py --check certificate.json
rustc -O --edition 2021 -o verify_rs verify.rs
./verify_rs
echo "b-cubic-fourteen OK"
