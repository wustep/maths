#!/bin/sh
set -eu
HERE=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
ROOT=$(dirname "$HERE")
if [ ! -x "$ROOT/.venv/bin/python" ]; then
  python3 -m venv "$ROOT/.venv"
  "$ROOT/.venv/bin/pip" install sympy scipy matplotlib numpy
fi
if ! "$ROOT/.venv/bin/python" -c "import pysat" 2>/dev/null; then
  "$ROOT/.venv/bin/pip" install python-sat
fi
echo "venv ready"
