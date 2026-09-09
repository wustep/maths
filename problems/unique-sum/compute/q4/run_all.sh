#!/usr/bin/env bash
set -euo pipefail

HERE=$(cd "$(dirname "$0")" && pwd)
PYTHON=${PYTHON:-python3}
"$PYTHON" -c 'import pysat' # install requirements.txt in a virtualenv first
BUILD=$(mktemp -d /tmp/unique-sum-q4-replay.XXXXXX)
trap 'rm -rf "$BUILD"' EXIT

rustc -D warnings -O "$HERE/verify_witness.rs" -o "$BUILD/witness"
rustc -D warnings -O "$HERE/verify_exact.rs" -o "$BUILD/exact"
gcc -O3 -march=native -std=c11 -Wall -Wextra -Werror "$HERE/cover_search.c" -o "$BUILD/cover"

"$PYTHON" "$HERE/verify_artifacts.py" "$BUILD/witness" > "$BUILD/witnesses.json"
"$PYTHON" "$HERE/audit_exact.py" "$BUILD/exact" > "$BUILD/rust-controls.json"
"$PYTHON" "$HERE/audit_cover.py" "$BUILD/cover" > "$BUILD/c-controls.json"
"$PYTHON" "$HERE/audit_partition.py" > "$BUILD/partition-controls.json"
"$PYTHON" "$HERE/audit_encoding.py" > "$BUILD/encoding-controls.json"
echo 'Witnesses, small exhaustive controls, and midpoint partitions passed.'

"$PYTHON" "$HERE/run_exact.py" "$BUILD/exact" 59 14 --initial-ap 5 \
    --nodes 3000000 --seconds 600 --source "$HERE/verify_exact.rs" --output "$BUILD/rust-ap5.json"
"$PYTHON" "$HERE/run_exact.py" "$BUILD/exact" 59 14 --initial-ap 6 \
    --nodes 3000000 --seconds 300 --source "$HERE/verify_exact.rs" --output "$BUILD/rust-ap6.json"
"$PYTHON" "$HERE/search_sat.py" 59 14 --initial-ap 5 --atmost --depth 12 \
    --conflicts 20000000 --solver cadical195 --output "$BUILD/sat-ap5.json"
"$PYTHON" - "$BUILD" <<'PY'
import json
from pathlib import Path
import sys
build = Path(sys.argv[1])
for name, length in (('rust-ap5.json', 5), ('rust-ap6.json', 6), ('sat-ap5.json', 5)):
    result = json.loads((build/name).read_text())
    assert result['status'] == 'UNSAT', (name, result)
    assert result['p'] == 59 and result['bound'] == 14 and result['initial_ap'] == length
    assert not result.get('forbid_ap', 0)
print('VALID_CLAIM: m(59)<=15; AP5 and AP6 families excluded through size 14.')
print('No unrestricted lower bound at 59 and no published record improvement.')
PY
