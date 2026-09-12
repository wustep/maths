#!/bin/sh
# Six light workers on the remaining 1,108 q8 balls plus one extra-seed worker.
# Each worker is one Python driver + one tiny C evaluator.
set -eu
cd "$(dirname "$0")"
mkdir -p work certs/shards
if [ ! -x work/ball ]; then
  cc -O3 -std=c11 -Wall -Wextra -o work/ball ball.c
fi
export PYTHONUNBUFFERED=1
# Hot leftover of the productive (7,15) seed and its siblings.
python3 search.py --start 82 --stop 170 --output work/shard0.json \
  >work/shard0.log 2>&1 & echo $! >work/shard0.pid
# Remaining (7,15) then (11,11) prefix.
python3 search.py --start 170 --stop 400 --output work/shard1.json \
  >work/shard1.log 2>&1 & echo $! >work/shard1.pid
# Rest of (11,11) into (15,7).
python3 search.py --start 400 --stop 600 --output work/shard2.json \
  >work/shard2.log 2>&1 & echo $! >work/shard2.pid
# Rest of (15,7) up to the (19,3) block.
python3 search.py --start 600 --stop 763 --output work/shard3.json \
  >work/shard3.log 2>&1 & echo $! >work/shard3.pid
# Published (19,3) M-certificates: nest neighbourhood.
python3 search.py --start 763 --stop 886 --output work/shard4.json \
  >work/shard4.log 2>&1 & echo $! >work/shard4.pid
# Seventeen parent additions, including the neighbour of the q8 scheme.
python3 search.py --start 886 --stop 1190 --output work/shard5.json \
  >work/shard5.log 2>&1 & echo $! >work/shard5.pid
# Extra finite handle: one-flip radius-3 around the q8 certificate itself.
python3 search.py --extra --start 0 --stop 100 --output work/shardE.json \
  >work/shardE.log 2>&1 & echo $! >work/shardE.pid
echo "launched $(ls work/shard*.pid | wc -l) workers"
