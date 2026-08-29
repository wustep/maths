#!/usr/bin/env bash
# Full q6 certificate replay.  Requires python-sat in .venv.
set -euo pipefail
cd "$(dirname "$0")"

if [[ ! -x ../q2/work/drat-trim-bin ]]; then
  ../q2/build_tools.sh
fi
if [[ ! -x .venv/bin/python ]]; then
  echo "missing .venv; install python-sat as described in README.md" >&2
  exit 2
fi

.venv/bin/python cases.py >/dev/null
.venv/bin/python verify_direct.py \
  --drat-trim ../q2/work/drat-trim-bin \
  --proof-dir certs/proofs \
  --work-dir work/replay-direct

if [[ -f certs/cube_proofs.json ]]; then
  .venv/bin/python verify_cubes.py \
    --drat-trim ../q2/work/drat-trim-bin \
    --work-dir work/replay-cubes
fi

.venv/bin/python summarize.py
echo OK
