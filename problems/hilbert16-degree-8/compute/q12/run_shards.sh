#!/bin/sh
# One light worker on the 93 leftover one-flip balls.
# One Python driver plus one tiny C evaluator.
set -eu
cd "$(dirname "$0")"
mkdir -p work certs
if [ ! -x work/ball ]; then
  cc -O3 -std=c11 -Wall -Wextra -o work/ball ball.c
fi
export PYTHONUNBUFFERED=1
python3 search.py --start 0 --stop 93 --output work/shard0.json \
  >work/shard0.log 2>&1 & echo $! >work/shard0.pid
echo "launched $(ls work/shard*.pid | wc -l) workers"
