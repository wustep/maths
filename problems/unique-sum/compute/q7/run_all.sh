#!/usr/bin/env bash
set -euo pipefail

HERE=$(cd "$(dirname "$0")" && pwd)
PYTHON=${PYTHON:-python3}
BUILD=$(mktemp -d /tmp/unique-sum-q7-replay.XXXXXX)
trap 'rm -rf "$BUILD"' EXIT

rustc -D warnings -O "$HERE/verify_witness.rs" -o "$BUILD/witness"
rustc -D warnings -O "$HERE/verify_exact.rs" -o "$BUILD/exact"
gcc -O3 -march=native -std=c11 -Wall -Wextra -Werror "$HERE/cover_search.c" -o "$BUILD/cover"

"$PYTHON" "$HERE/verify_upper.py" "$BUILD/witness" > "$BUILD/upper.json"
"$PYTHON" "$HERE/audit_cover.py" "$BUILD/cover" > "$BUILD/c-controls.json"
"$PYTHON" "$HERE/audit_exact.py" "$BUILD/exact" > "$BUILD/rust-controls.json"
(cd "$HERE" && "$PYTHON" "$HERE/audit_partition.py") > "$BUILD/partition-controls.json"
"$PYTHON" "$HERE/verify_claim.py" > "$BUILD/claim-artifacts.json"
echo 'Witnesses, small exhaustive controls, partitions, and stored class decisions passed.'

# 128-bit port regression: the q6 AP5 ceiling at 61 must stay UNSAT.
"$PYTHON" "$HERE/run_cover.py" "$BUILD/cover" 61 14 --initial-ap 5 --forbid-ap 0 \
    --nodes 3000000 --seconds 300 --output "$BUILD/c-ap5-61.json"
"$PYTHON" "$HERE/run_exact.py" "$BUILD/exact" 61 14 --initial-ap 5 --forbid-ap 0 \
    --nodes 3000000 --seconds 300 --source "$HERE/verify_exact.rs" --output "$BUILD/rust-ap5-61.json"

# One 6-point named class at 67, both languages.
SIXPT=0x42000000000000017
"$PYTHON" "$HERE/run_cover.py" "$BUILD/cover" 67 15 --initial-ap 4 --forbid-ap 5 \
    --root "$SIXPT" --nodes 2000000 --seconds 600 --output "$BUILD/c-ap4-6pt.json"
"$PYTHON" "$HERE/run_exact.py" "$BUILD/exact" 67 15 --initial-ap 4 --forbid-ap 5 \
    --root "$SIXPT" --nodes 2000000 --seconds 600 --source "$HERE/verify_exact.rs" \
    --output "$BUILD/rust-ap4-6pt.json"

"$PYTHON" - "$BUILD" <<'PY'
import json
from pathlib import Path
import sys
build = Path(sys.argv[1])
for name in ('c-ap5-61.json', 'rust-ap5-61.json'):
    result = json.loads((build/name).read_text())
    assert result['status'] == 'UNSAT', (name, result)
    assert result['p'] == 61 and result['bound'] == 14
for name in ('c-ap4-6pt.json', 'rust-ap4-6pt.json'):
    result = json.loads((build/name).read_text())
    assert result['status'] == 'UNSAT', (name, result)
    assert result['p'] == 67 and result['bound'] == 15
print('VALID_CLAIM: m(67)=16 locally, matching OEIS A398173.')
print('No published record improvement. q5 m(59)=15 and q6 m(61)=15 are retained.')
print('Leftover: dual lower replay at 71 and 73, and the unpublished prime 79.')
PY
