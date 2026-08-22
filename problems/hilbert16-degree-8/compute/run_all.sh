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
echo "== hand certificate =="
python3 tcurve.py verify certs/harnack_d8.json
echo "== census replay (downloads deg8.pcoms.txz on first run) =="
python3 replay_census.py
echo "== Harnack splits + Haas decomposition of the 38 M-certificates =="
python3 haas.py
python3 prep.py
echo "== dent: T-curves outside the 2,367 =="
python3 verify_new.py
echo "== independent topology check (Rokhlin / Gudkov-Krakhnov-Kharlamov) =="
python3 check_rokhlin.py
echo "== where the census is thin =="
python3 hole_map.py
echo "== C searcher agrees with the Python sweep (ranks 6, 10, 12, 13, 16) =="
cc -O2 -o zonec zonec.c
cc -O2 -o ballc ballc.c
for c in "deg8/o01-p01-n00/(1).pcom" \
         "deg8/o10-p09-n01/(1v1(1(7))).pcom" \
         "deg8/o13-p03-n10/(1(1)v1(2)v1(7)).pcom" \
         "deg8/o11-p10-n01/(2v1(1(7))).pcom" \
         "deg8/o13-p03-n10/(2(1)v1(8)).pcom"; do
  python3 validate_zonec.py "$c"
done
echo "all replays done"

# The searches themselves (hours, logs are gitignored; results are the
# certs/*.json committed here):
#   python3 zonec_drive.py <w> 3 6 runs4          every census triangulation
#   python3 walk_drive.py  <w> <seed> 100000 runs5  regular tris outside it
#   python3 ball_drive.py  <w> <n> 4 runs5 1200   radius-4 balls, all 2,367
#   BALL_KEYS=... BALL_TAG=m python3 ball_deep.py 6 runs5 <w> <n>
#   python3 report.py                             compact status
