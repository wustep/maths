#!/usr/bin/env bash
set -euo pipefail

HERE=$(cd "$(dirname "$0")" && pwd)
PYTHON=${PYTHON:-python3}

"$PYTHON" "$HERE/verify_green_m_p.py"
"$PYTHON" "$HERE/q3/verify_upper.py"

PLOT_PYTHON=$PYTHON
if ! "$PLOT_PYTHON" -c 'import matplotlib, numpy' >/dev/null 2>&1; then
    if [ ! -x "$HERE/.venv/bin/python" ]; then
        "$PYTHON" -m venv "$HERE/.venv"
    fi
    if ! "$HERE/.venv/bin/python" -c 'import matplotlib, numpy' >/dev/null 2>&1; then
        "$HERE/.venv/bin/pip" install matplotlib numpy
    fi
    PLOT_PYTHON="$HERE/.venv/bin/python"
fi
"$PLOT_PYTHON" "$HERE/plot_m_p.py"
