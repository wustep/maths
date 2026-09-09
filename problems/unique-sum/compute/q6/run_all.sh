#!/usr/bin/env bash
set -euo pipefail

HERE=$(cd "$(dirname "$0")" && pwd)
Q5=$(cd "$HERE/../q5" && pwd)
PYTHON=${PYTHON:-python3}
BUILD=$(mktemp -d /tmp/unique-sum-q6-replay.XXXXXX)
trap 'rm -rf "$BUILD"' EXIT

rustc -D warnings -O "$Q5/verify_witness.rs" -o "$BUILD/witness"
rustc -D warnings -O "$Q5/verify_exact.rs" -o "$BUILD/exact"
gcc -O3 -march=native -std=c11 -Wall -Wextra -Werror "$Q5/cover_search.c" -o "$BUILD/cover"

"$PYTHON" "$HERE/verify_upper.py" "$BUILD/witness" > "$BUILD/upper.json"
(cd "$Q5" && "$PYTHON" "$Q5/audit_cover.py" "$BUILD/cover") > "$BUILD/c-controls.json"
(cd "$Q5" && "$PYTHON" "$Q5/audit_exact.py" "$BUILD/exact") > "$BUILD/rust-controls.json"
"$PYTHON" "$HERE/verify_claim.py" > "$BUILD/claim-artifacts.json"
echo 'Witness, q5 engine controls, and stored class decisions passed.'

"$PYTHON" "$Q5/run_exact.py" "$BUILD/exact" 61 14 --initial-ap 5 --forbid-ap 0 \
    --nodes 3000000 --seconds 300 --source "$Q5/verify_exact.rs" --output "$BUILD/rust-ap5.json"
"$PYTHON" "$Q5/run_cover.py" "$BUILD/cover" 61 14 --initial-ap 5 --forbid-ap 0 \
    --nodes 3000000 --seconds 300 --output "$BUILD/c-ap5.json"
"$PYTHON" "$Q5/run_cover.py" "$BUILD/cover" 61 14 --initial-ap 3 --forbid-ap 4 \
    --root 0x100000000000000b --nodes 2000000 --seconds 180 --output "$BUILD/c-ap4free-4pt.json"
"$PYTHON" "$Q5/run_exact.py" "$BUILD/exact" 61 14 --initial-ap 3 --forbid-ap 4 \
    --root 0x100000000000000b --nodes 3000000 --seconds 300 --source "$Q5/verify_exact.rs" \
    --output "$BUILD/rust-ap4free-4pt.json"

"$PYTHON" - "$BUILD" <<'PY'
import json
from pathlib import Path
import sys
build = Path(sys.argv[1])
for name in ('rust-ap5.json', 'c-ap5.json', 'c-ap4free-4pt.json', 'rust-ap4free-4pt.json'):
    result = json.loads((build/name).read_text())
    assert result['status'] == 'UNSAT', (name, result)
    assert result['p'] == 61 and result['bound'] == 14
print('VALID_CLAIM: m(61)=15 locally, matching OEIS A398173.')
print('No published record improvement. q5 m(59)=15 is retained.')
PY
