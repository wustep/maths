#!/usr/bin/env bash
# Full q3 certificate replay.  Requires python-sat in .venv.
set -euo pipefail
cd "$(dirname "$0")"

if [[ ! -x ../q2/work/drat-trim-bin ]]; then
  ../q2/build_tools.sh
fi
if [[ ! -x .venv/bin/python ]]; then
  echo "missing .venv; install python-sat as described in README.md" >&2
  exit 2
fi

.venv/bin/python verify_direct_p7.py \
  --drat-trim ../q2/work/drat-trim-bin \
  --proof-dir certs/proofs \
  --work-dir work/replay-direct

pids=()
for shard in 0 1 2 3 4 5 6 7; do
  .venv/bin/python verify_p7_proofs.py \
    --drat-trim ../q2/work/drat-trim-bin \
    --neighborhoods certs/p7_neighborhoods.json \
    --manifest certs/p7_proofs.json \
    --proof-dir certs/proofs \
    --work-dir "work/replay-${shard}" \
    --archive-shard "$shard" &
  pids+=("$!")
done
for pid in "${pids[@]}"; do
  wait "$pid"
done

.venv/bin/python summarize.py
echo OK
