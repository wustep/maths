#!/usr/bin/env bash
set -eu
cd "$(dirname "$0")"
python3 ionization_bounds.py
python3 -c "
import json
from ionization_bounds import verify
r = json.load(open('record.json'))
err = verify(r)
assert not err, err
print('record.json rechecked OK')
"
echo "simon-ionization-excess compute: OK (replay of published bounds, no new bound)"
