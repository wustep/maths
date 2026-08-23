#!/bin/sh
# Replay the shape-5 profile, then the four remaining searches.
set -e
cd "$(dirname "$0")/.."
python3 q1/analyze_profile.py
gcc -O3 -o q1/search_translates q1/search_translates.c
gcc -O3 -o q1/search_plateau q1/search_plateau.c
gcc -O3 -o q1/search_cosets q1/search_cosets.c
./q1/search_translates R367.txt | tee q1/translate_log.txt
./q1/search_plateau R367.txt | tee q1/plateau_log.txt
python3 q1/search_cosets_sample.py
gcc -O3 -o q1/search_ejection q1/search_ejection.c
./q1/search_ejection R367.txt | tee q1/ejection_log.txt
python3 q1/search_core_puncture.py
python3 q1/search_4support.py
python3 verify_set.py R367.txt --min-size 367
if ls q1/R3*.txt >/dev/null 2>&1; then
  for f in q1/R3*.txt; do
    python3 verify_set.py "$f" --min-size 368 || true
  done
fi
