#!/bin/sh
# Continue q5's odd size-5 first-index shards in q6. Each .next file
# wins over the committed q5 restart point. Run from compute/.
set -e
here=$(cd "$(dirname "$0")" && pwd)
cd "$here/.."
mkdir -p "$here/even_out"

run_shard() {
  lo=$1
  hi=$2
  resume=$3
  out="$here/even_out/odd_skel5_${lo}-${hi}.jsonl"
  if [ -f "$out.next" ]; then
    H16_QDIR="$here" python3 q5/odd_skel.py 5 "$out" --minsize 5 --shard "$lo:$hi"
  else
    H16_QDIR="$here" python3 q5/odd_skel.py 5 "$out" --minsize 5 --shard "$lo:$hi" --resume-from "$resume"
  fi
}

run_shard 2 3 2 &
p0=$!
run_shard 3 7 3 &
p1=$!
run_shard 7 11 7 &
p2=$!
run_shard 20 21 20 &
p3=$!
run_shard 21 24 21 &
p4=$!
run_shard 24 32 24 &
p5=$!
run_shard 45 62 45 &
p6=$!
run_shard 62 189 62 &
p7=$!
wait "$p0"
wait "$p1"
wait "$p2"
wait "$p3"
wait "$p4"
wait "$p5"
wait "$p6"
wait "$p7"

H16_QDIR="$here" python3 q5/write_certs.py odd_skel5
H16_QDIR="$here" python3 q5/collect.py
