#!/usr/bin/env bash
set -eu
cd "$(dirname "$0")"
python3 lt_constants.py
python3 -c "
import json
from lt_constants import verify
r = json.load(open('record.json'))
err = verify(r)
assert not err, err
print('record.json rechecked OK')
"
echo "simon-lieb-thirring compute: OK (replay of published constants, no new bound)"
