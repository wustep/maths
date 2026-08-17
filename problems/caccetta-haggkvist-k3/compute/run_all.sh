#!/bin/sh
# Replay tonight's checkable claims.  Does not rerun the n=18 SAT.
set -e
here=$(dirname "$0")
cd "$here"
echo "== flags4 (must match HKN Table 1) =="
python3 flags4.py | tail -8
echo "== ind/fork (must match (4.14)/(4.15)/fork) =="
python3 ind_fork.py | tail -8
echo "== F4 certificate at 0.34645 =="
python3 verify_certificate.py certs/f4_certificate.json --margin 0.05 --c 0.34645
echo "== DRAT n=12,15,16,17 =="
./drat-trim certs/ch-12-4-sb.cnf certs/ch-12-4-sb.drat | tail -3
./drat-trim certs/ch-15-5-sb.cnf certs/ch-15-5-sb.drat | tail -3
./drat-trim certs/ch-16-6-sb.cnf certs/ch-16-6-sb.drat | tail -3
./drat-trim certs/ch-17-6-sb.cnf certs/ch-17-6-sb.drat | tail -3
echo "all replay checks finished"
