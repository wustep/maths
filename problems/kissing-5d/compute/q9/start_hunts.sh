#!/bin/sh
# Start leftover SAT hunts. Does not claim a result.
# Cadical writes binary DRAT; Kissat is a probe without a proof.
set -eu
HERE=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
cd "$HERE"
ROOT=$(dirname "$HERE")
PY="$ROOT/.venv/bin/python"
sh setup_solvers.sh
"$PY" write_cnf.py all

mkdir -p certs
if [ ! -f certs/five_k30_n0_5.hunt.started ]; then
  : > certs/five_k30_n0_5.hunt.started
  nohup ./bin/cadical certs/five_k30_n0_5.cnf certs/five_k30_n0_5.native.drat \
    > certs/five_k30_n0_5.cadical.log 2>&1 &
  echo "started cadical leftover-tight k=30 pid $!"
fi
if [ ! -f certs/n1_k19_star5_no21_no13.hunt.started ]; then
  : > certs/n1_k19_star5_no21_no13.hunt.started
  nohup ./bin/kissat certs/n1_k19_star5_no21_no13.cnf \
    > certs/n1_k19_star5_no21_no13.kissat.log 2>&1 &
  echo "started kissat global |U|=19 pid $!"
fi
echo "hunts launched (or already marked started)"
