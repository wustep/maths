#!/bin/sh
# Separate entry point: success audits coverage, not a new scheme.
set -eu
cd "$(dirname "$0")"
python3 coverage.py
