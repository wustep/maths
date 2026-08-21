#!/bin/sh
# Replay for q10: prescribed-automorphism (Kramer-Mesner) search at r = 10.
set -e
cd "$(dirname "$0")/../.."
BIN=$(mktemp -d)/os
gcc -O2 -o "$BIN" compute/q10/orbit_search.c

python3 compute/q10/setup.py 30 /tmp/q10_inst30.json
python3 compute/q10/setup.py 21 /tmp/q10_inst21.json
cmp /tmp/q10_inst30.json compute/q10/instance_30.json
cmp /tmp/q10_inst21.json compute/q10/instance_21.json

echo "--- encoding control: orbit masks vs flat syndrome sweep ---"
"$BIN" --kind 30 --selftest 400
"$BIN" --kind 21 --selftest 400

echo "--- positive control: sigma-invariant covering at n = 63 ---"
P=$(python3 -c "import json;d=json.load(open('compute/q10/instance_21.json'));print(*d['forced_pairs'][0])")
"$BIN" --kind 21 --orbits 9 --pair $P

echo "--- the search: n = 49, every conjugacy class, exhaustive ---"
for K in 30 21; do
  python3 -c "
import json,subprocess,sys
d=json.load(open('compute/q10/instance_$K.json'))
for p in d['forced_pairs']:
    r=subprocess.run(['$BIN','--kind','$K','--orbits','7','--pair',str(p[0]),str(p[1])])
    assert r.returncode==3, 'expected EXHAUSTED'
"
done
echo "q10 checks OK"
