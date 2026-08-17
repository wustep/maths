#!/bin/sh
set -e
cd "$(dirname "$0")"
PY=./.venv/bin/python
$PY replay_known.py
$PY verify_c7.py
echo "all replay checks passed"
