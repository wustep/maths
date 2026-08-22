#!/bin/sh
# Resume the ball phase: only task files whose output lacks a summary line.
for i in $(seq 0 23); do
  if [ ! -f runs2/balls_$i.jsonl ] || ! grep -q summary runs2/balls_$i.jsonl 2>/dev/null; then echo $i; fi
done | xargs -P "${1:-3}" -I{} python3 nest_search.py runs/tasks/tasks_balls_{}.json runs2/balls_{}.jsonl
