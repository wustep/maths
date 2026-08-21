#!/bin/sh
# run_phase.sh <phase> <njobs>  -- runs every runs/tasks/tasks_<phase>_*.json
phase=$1; nj=${2:-8}
ls runs/tasks/tasks_${phase}_*.json | sed "s#.*tasks_${phase}_\([0-9]*\)\.json#\1#" \
  | xargs -P "$nj" -I{} python3 nest_search.py runs/tasks/tasks_${phase}_{}.json runs2/${phase}_{}.jsonl
