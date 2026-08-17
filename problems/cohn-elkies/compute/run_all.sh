#!/bin/sh
# Rebuild the exact certificate and replay the independent verifier.
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
VENV=${CE_VENV:-/tmp/ce-venv}
if [ ! -x "$VENV/bin/python" ]; then
    python3 -m venv "$VENV"
    "$VENV/bin/pip" install sympy mpmath numpy
fi
cd "$HERE"
PYTHONUNBUFFERED=1 "$VENV/bin/python" make_certificate.py
PYTHONUNBUFFERED=1 "$VENV/bin/python" verify.py
echo "run_all: ok"
