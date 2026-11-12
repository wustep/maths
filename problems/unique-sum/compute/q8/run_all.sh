#!/usr/bin/env bash
set -euo pipefail

HERE=$(cd "$(dirname "$0")" && pwd)
PYTHON=${PYTHON:-python3}
BUILD=$(mktemp -d /tmp/unique-sum-q8-replay.XXXXXX)
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

# Live AP5 ceiling and the 4-point AP4-free class at 67, in both languages.
FOURPT=0x4000000000000000b
"$PYTHON" "$HERE/run_exact.py" "$BUILD/exact" 67 15 --initial-ap 5 --forbid-ap 0 \
    --nodes 20000000 --seconds 1800 --source "$HERE/verify_exact.rs" --output "$BUILD/rust-ap5.json"
"$PYTHON" "$HERE/run_cover.py" "$BUILD/cover" 67 15 --initial-ap 5 --forbid-ap 0 \
    --nodes 20000000 --seconds 1800 --output "$BUILD/c-ap5.json"
"$PYTHON" "$HERE/run_cover.py" "$BUILD/cover" 67 15 --initial-ap 3 --forbid-ap 4 \
    --root "$FOURPT" --nodes 10000000 --seconds 600 --output "$BUILD/c-ap4free-4pt.json"
"$PYTHON" "$HERE/run_exact.py" "$BUILD/exact" 67 15 --initial-ap 3 --forbid-ap 4 \
    --root "$FOURPT" --nodes 10000000 --seconds 600 --source "$HERE/verify_exact.rs" \
    --output "$BUILD/rust-ap4free-4pt.json"

"$PYTHON" - "$BUILD" <<'PY'
import json
from pathlib import Path
import sys
build = Path(sys.argv[1])
for name in ('rust-ap5.json', 'c-ap5.json', 'c-ap4free-4pt.json', 'rust-ap4free-4pt.json'):
    result = json.loads((build/name).read_text())
    assert result['status'] == 'UNSAT', (name, result)
    assert result['p'] == 67 and result['bound'] == 15
print('VALID_CLAIM: m(67)=m(71)=m(73)=16 locally, matching OEIS A398173.')
print('No published record improvement. q5 m(59)=15 and q6 m(61)=15 are retained.')
PY
