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
echo 'Witnesses, small exhaustive controls, and partitions passed.'

# 128-bit port regression: the q6 AP5 ceiling at 61 must stay UNSAT.
"$PYTHON" "$HERE/run_cover.py" "$BUILD/cover" 61 14 --initial-ap 5 --forbid-ap 0 \
    --nodes 3000000 --seconds 300 --output "$BUILD/c-ap5-61.json"
"$PYTHON" "$HERE/run_exact.py" "$BUILD/exact" 61 14 --initial-ap 5 --forbid-ap 0 \
    --nodes 3000000 --seconds 300 --source "$HERE/verify_exact.rs" --output "$BUILD/rust-ap5-61.json"
"$PYTHON" - "$BUILD" <<'PY'
import json
from pathlib import Path
import sys
build = Path(sys.argv[1])
for name in ('c-ap5-61.json', 'rust-ap5-61.json'):
    result = json.loads((build/name).read_text())
    assert result['status'] == 'UNSAT', (name, result)
    assert result['p'] == 61 and result['bound'] == 14
print('128-bit engines replay m(61) AP5 ceiling: UNSAT.')
PY

set +e
"$PYTHON" "$HERE/verify_claim.py" > "$BUILD/claim-artifacts.json"
CLAIM_RC=$?
set -e
cat "$BUILD/claim-artifacts.json"
if [ "$CLAIM_RC" -ne 0 ]; then
    echo 'PARTIAL: stored dual ladder is incomplete. Matching OEIS is not a dent.'
    exit 3
fi

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
