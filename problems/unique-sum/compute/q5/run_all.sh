#!/usr/bin/env bash
set -euo pipefail

HERE=$(cd "$(dirname "$0")" && pwd)
PYTHON=${PYTHON:-python3}
BUILD=$(mktemp -d /tmp/unique-sum-q5-replay.XXXXXX)
trap 'rm -rf "$BUILD"' EXIT

rustc -D warnings -O "$HERE/verify_witness.rs" -o "$BUILD/witness"
rustc -D warnings -O "$HERE/verify_exact.rs" -o "$BUILD/exact"
gcc -O3 -march=native -std=c11 -Wall -Wextra -Werror "$HERE/cover_search.c" -o "$BUILD/cover"
gcc -O3 -march=native -std=c11 -Wall -Wextra -Werror "$HERE/seed_search.c" -o "$BUILD/seed"

"$PYTHON" "$HERE/verify_artifacts.py" "$BUILD/witness" > "$BUILD/witnesses.json"
"$PYTHON" "$HERE/audit_exact.py" "$BUILD/exact" > "$BUILD/rust-controls.json"
"$PYTHON" "$HERE/audit_cover.py" "$BUILD/cover" > "$BUILD/c-controls.json"
"$PYTHON" "$HERE/audit_partition.py" > "$BUILD/partition-controls.json"
"$PYTHON" "$HERE/verify_claim.py" > "$BUILD/claim-artifacts.json"
echo 'Witnesses, small exhaustive controls, partitions, and stored class decisions passed.'

"$PYTHON" "$HERE/run_exact.py" "$BUILD/exact" 59 14 --initial-ap 5 --forbid-ap 0 \
    --nodes 3000000 --seconds 300 --source "$HERE/verify_exact.rs" --output "$BUILD/rust-ap5.json"
"$PYTHON" "$HERE/run_cover.py" "$BUILD/cover" 59 14 --initial-ap 5 --forbid-ap 0 \
    --nodes 3000000 --seconds 300 --output "$BUILD/c-ap5.json"
"$PYTHON" "$HERE/run_cover.py" "$BUILD/cover" 59 14 --initial-ap 3 --forbid-ap 4 \
    --root 0x40000000000000b --nodes 2000000 --seconds 180 --output "$BUILD/c-ap4free-4pt.json"
"$PYTHON" "$HERE/run_exact.py" "$BUILD/exact" 59 14 --initial-ap 3 --forbid-ap 4 \
    --root 0x40000000000000b --nodes 3000000 --seconds 300 --source "$HERE/verify_exact.rs" \
    --output "$BUILD/rust-ap4free-4pt.json"

"$PYTHON" - "$BUILD" <<'PY'
import json
from pathlib import Path
import sys
build = Path(sys.argv[1])
for name in ('rust-ap5.json', 'c-ap5.json', 'c-ap4free-4pt.json', 'rust-ap4free-4pt.json'):
    result = json.loads((build/name).read_text())
    assert result['status'] == 'UNSAT', (name, result)
    assert result['p'] == 59 and result['bound'] == 14
print('VALID_CLAIM: m(59)=15 locally, matching OEIS A398173.')
print('No published record improvement.')
PY
