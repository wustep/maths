#!/bin/sh
# Replay everything that does not need the (gitignored) search logs.
set -e
cd "$(dirname "$0")"
echo "== notation tests =="
python3 notation.py
echo "== engine sanity (classical Harnack schemes, degrees 1-8) =="
python3 sanity.py
echo "== published-record tables self-check =="
python3 record.py
echo "== certificates =="
python3 tcurve.py verify certs/*.json
echo "== census replay (downloads deg8.pcoms.txz on first run) =="
python3 replay_census.py
echo "all replays done"
