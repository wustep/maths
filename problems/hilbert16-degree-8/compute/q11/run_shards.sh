#!/bin/sh
# Two light workers on the 205 leftover one-flip balls.
# Each worker is one Python driver + one tiny C evaluator.
set -eu
cd "$(dirname "$0")"
mkdir -p work certs
if [ ! -x work/ball ]; then
  cc -O3 -std=c11 -Wall -Wextra -o work/ball ball.c
fi
export PYTHONUNBUFFERED=1
python3 search.py --start 0 --stop 103 --output work/shard0.json \
  >work/shard0.log 2>&1 & echo $! >work/shard0.pid
python3 search.py --start 103 --stop 205 --output work/shard1.json \
  >work/shard1.log 2>&1 & echo $! >work/shard1.pid
echo "launched $(ls work/shard*.pid | wc -l) workers"
