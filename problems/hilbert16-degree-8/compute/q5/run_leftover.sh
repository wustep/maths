#!/bin/sh
# Launch the q4 leftover: even-BFS remainder and odd size 5.
# Run from problems/hilbert16-degree-8/compute. Does not re-run
# leftover thicken or the finished depth-3 three-split.
set -e
here=$(cd "$(dirname "$0")" && pwd)
cd "$here/.."
mkdir -p q5/even_out
echo "odd size 5 shard 0:11"
python3 q5/odd_skel.py 5 q5/even_out/odd_skel5_0-11.jsonl --minsize 5 --shard 0:11
echo "odd size 5 shard 11:32"
python3 q5/odd_skel.py 5 q5/even_out/odd_skel5_11-32.jsonl --minsize 5 --shard 11:32
echo "odd size 5 shard 32:189"
python3 q5/odd_skel.py 5 q5/even_out/odd_skel5_32-189.jsonl --minsize 5 --shard 32:189
echo "even BFS remainder after 1,200,000"
python3 q5/even_walk.py bfs q5/even_out/bfs.jsonl 8000000 1200000
python3 q5/write_certs.py
python3 q5/collect.py
