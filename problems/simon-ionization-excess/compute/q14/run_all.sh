#!/usr/bin/env bash
# Replay q14. Exit 0 certifies a printed leading below q13's 1.1006.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p certs
PYTHON="${PYTHON:-python3}"
export PYTHON

echo "==> validate frozen q13 prerequisite"
(
  cd ../q13
  "$PYTHON" verify_rebuild.py
  "$PYTHON" aspect_identities.py
  gcc -O2 -o verify_aspect verify_aspect.c -lm
  ./verify_aspect
  rustc -O -o verify_aspect_rs verify_aspect.rs
  ./verify_aspect_rs
)

echo "==> interval finite-range reweighting bound"
"$PYTHON" span_bound.py

echo "==> independent stdlib Decimal reconstruction"
"$PYTHON" verify_span.py

echo "==> independent Rust reconstruction"
rustc -O -o verify_span_rs verify_span.rs
./verify_span_rs

echo "==> HPS Section 7 printer"
"$PYTHON" tighten_leading.py

echo "==> assemble"
"$PYTHON" lift_cert.py
echo "q14 PASS (printed leading 1.1006 lifted to 1.1002)"
