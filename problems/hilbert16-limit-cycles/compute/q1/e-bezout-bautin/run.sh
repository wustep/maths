#!/usr/bin/env bash
# Replay line E: Bézout ceiling and Bautin L1 (plus L2 as V2).
set -euo pipefail
cd "$(dirname "$0")"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

python3 bezout_preimages.py --json bezout_samples.json --dump "$tmp/py_bezout.txt"
python3 pullback_degree.py --json pullback_degree.json --dump "$tmp/py_pull.txt"
python3 l1_focal.py --json l1_polynomial.json --tests center_family_tests.json --dump "$tmp/py_l1.txt"
python3 emit_common.py --dump "$tmp/python_common.txt"

rustc --edition 2021 -D warnings -C opt-level=2 replay.rs -o "$tmp/replay"
(cd "$(pwd)" && "$tmp/replay" --dump "$tmp/rust_common.txt")
diff -u "$tmp/python_common.txt" "$tmp/rust_common.txt"
echo "Python and Rust common dumps agree"

if command -v lean >/dev/null 2>&1; then
  lean AdjBezout.lean
  echo "Lean AdjBezout.lean OK"
else
  echo "lean not on PATH; skipped AdjBezout.lean"
fi

echo "OK"
