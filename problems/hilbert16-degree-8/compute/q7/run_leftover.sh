#!/bin/sh
# Finish leftover odd size-5 (all 189 first indices) then the tractable
# even components. One heavy job at a time; no giant seen/queue pickle.
set -e
here=$(cd "$(dirname "$0")" && pwd)
cd "$here/.."
mkdir -p "$here/even_out" "$here/work"

python3 q7/odd5_export.py
gcc -O3 -std=gnu11 -Wall -Wextra -Wno-unused-function \
  -o q7/odd5c q7/odd5c.c
gcc -O3 -std=gnu11 -Wall -Wextra -Wno-unused-function \
  -o q7/evenc q7/evenc.c

run_shard() {
  lo=$1
  hi=$2
  echo "odd size 5 shard $lo:$hi"
  q7/odd5c q7/work/odd5.task "$lo" "$hi" \
    "$here/even_out/odd5c_${lo}-${hi}.jsonl"
}

# Sequential. The q5 leftover was incomplete first-index blocks
# 0-11 / 11-32 / 32-189; this re-evaluates the whole space in C.
run_shard 0 11
run_shard 11 32
run_shard 32 189

python3 q7/odd5_collect.py
python3 q7/thicken_witnesses.py
if [ -f q7/certs/new_schemes.json ]; then
  python3 verify_new.py q7/certs/new_schemes.json
fi

echo "tractable even component a=10 (126336)"
python3 q7/even_drive.py '<10v1<2v1<8>>>'
echo "tractable even component a=17 nested box (25292736)"
python3 q7/even_drive.py '<17v1<2v1<1>>>'

python3 q7/write_certs.py
python3 q7/collect.py
