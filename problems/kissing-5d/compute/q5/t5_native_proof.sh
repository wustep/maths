#!/bin/sh
# Native CaDiCaL DRAT for the 355-point T^5 36-clique CNF.
# Replay:
#   python3 t5_36_proof.py --cnf-only
#   ./bin/cadical certs/t5_clique36.cnf certs/t5_clique36.native.drat
#   ./bin/drat-trim certs/t5_clique36.cnf certs/t5_clique36.native.drat
set -eu
HERE=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
cd "$HERE"
if [ ! -x ./bin/cadical ]; then
  echo "missing ./bin/cadical" >&2
  exit 1
fi
if [ ! -f certs/t5_clique36.cnf ]; then
  python3 t5_36_proof.py --cnf-only
fi
./bin/cadical certs/t5_clique36.cnf certs/t5_clique36.native.drat | tee certs/t5_clique36.cadical.log
./bin/drat-trim certs/t5_clique36.cnf certs/t5_clique36.native.drat | tee certs/t5_clique36.native.drat-trim.log
