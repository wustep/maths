#!/bin/bash
# Replay q1 certificates. Exit 0 is the check a stranger runs.
set -euo pipefail
cd "$(dirname "$0")"

python3 verify_gupta.py
python3 ladders.py --replay
python3 verify_table.py

python3 -c "
import json
from pathlib import Path
blob = json.loads(Path('extend_w10.json').read_text())
assert blob['n11_below_6_17'] == 0
assert blob['n11_best'] == [6, 17]
print('extend_w10.json n=11 OK', blob['n11_count'], 'extensions')
"

python3 -c "
import json
from pathlib import Path
blob = json.loads(Path('three_rail.json').read_text())
for row in blob['exhaustive']:
    assert row['n_below_6_17'] == 0
    assert row['min_delta'][0] * 3 >= row['min_delta'][1]
print('three_rail exhaustive OK', [r['n'] for r in blob['exhaustive']])
"

python3 -c "
import json
from pathlib import Path
blob = json.loads(Path('interval_orders.json').read_text())
for row in blob['census']:
    assert row['n_below_1_3'] == 0
    assert row['min_delta'][0] * 3 >= row['min_delta'][1]
print('interval_orders OK', [r['n'] for r in blob['census']])
"

echo "q1 ALL CHECKS PASSED"
