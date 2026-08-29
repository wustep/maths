#!/usr/bin/env bash
# Run leftover representatives with bounded parallelism.
# Usage: ./run_batch.sh TIME NAMES...
set -euo pipefail
cd "$(dirname "$0")"
time_limit="${1:?time limit in seconds}"
shift
if [[ $# -eq 0 ]]; then
  echo "usage: $0 TIME NAME..." >&2
  exit 2
fi
PYTHON="${PYTHON:-./.venv/bin/python}"
KISSAT="${KISSAT:-../q2/work/kissat-bin}"
DRAT="${DRAT:-../q2/work/drat-trim-bin}"
jobs=0
max="${BATCH_JOBS:-4}"
for name in "$@"; do
  if [[ -f "certs/${name}.json" ]]; then
    status=$(python3 -c "import json; print(json.load(open('certs/${name}.json'))['status'])")
    if [[ "$status" == "UNSAT" || "$status" == "SAT" ]]; then
      echo "skip $name ($status)"
      continue
    fi
  fi
  echo "start $name time=$time_limit unsat=${KISSAT_UNSAT:-1}"
  extra=()
  if [[ "${KISSAT_UNSAT:-1}" == "1" ]]; then
    extra+=(--unsat)
  fi
  "$PYTHON" prove_direct.py \
    --name "$name" \
    --kissat "$KISSAT" \
    --drat-trim "$DRAT" \
    --time "$time_limit" \
    "${extra[@]}" \
    > "logs/${name}_batch.txt" 2>&1 &
  jobs=$((jobs + 1))
  if [[ "$jobs" -ge "$max" ]]; then
    wait -n
    jobs=$((jobs - 1))
  fi
done
wait
echo "batch done"
