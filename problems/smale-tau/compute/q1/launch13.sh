#!/usr/bin/env bash
# Launch (or resume) the crash-safe 13-step decision on 20!, 21!, 22!, 37#.
# Re-running with the same checkpoint resumes: completed tasks are skipped and
# found programs are restored, so a crash costs only the tasks in flight.
set -euo pipefail
cd "$(dirname "$0")"
ulimit -s unlimited 2>/dev/null || true
export OMP_STACKSIZE=512M
gcc -O3 -march=native -fopenmp -o slp_search slp_search.c
nohup ./slp_search --steps 13 --targets targets13.txt --threads "${THREADS:-8}" --split 6 \
      --checkpoint ck13.txt > decide13.json 2> decide13.log &
echo "launched pid $!  (checkpoint ck13.txt)"
