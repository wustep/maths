#!/usr/bin/env bash
# Launch the 13-step decision on the core targets (20!, 21!, 22!, 29#, 31#).
set -euo pipefail
cd "$(dirname "$0")"
gcc -O3 -march=native -fopenmp -o slp_search slp_search.c
nohup ./slp_search --steps 13 --targets targets13.txt --threads "${THREADS:-8}" --split 6 > decide13.json 2> decide13.log &
echo "launched pid $!"
