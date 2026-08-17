#!/bin/sh
# Deterministic residue replay. Exit nonzero if a check fails.
set -eu
cd "$(dirname "$0")"
python3 verify_mckay.py
./extend_check refs/r55_42some.g6
./circulant_census 42 | tee logs/replay_c42.txt | tail -1
./circulant_census 43 | tee logs/replay_c43.txt | tail -1
python3 - <<'PY'
from pathlib import Path
for n,p in [(42,'logs/replay_c42.txt'),(43,'logs/replay_c43.txt')]:
    t=Path(p).read_text()
    assert f'n={n}' in t and 'hits=0' in t, t
print('circulant 42/43 still empty')
PY
python3 flip_types.py
python3 seidel_switch.py
echo OK
