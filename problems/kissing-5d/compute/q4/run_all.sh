#!/bin/sh
# Replay the finished q4 checks.  Does not re-run the long SAT / BFS hunts.
set -eu
HERE=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
cd "$HERE"
ROOT=$(dirname "$HERE")
if [ ! -x "$ROOT/.venv/bin/python" ]; then
  python3 -m venv "$ROOT/.venv"
  "$ROOT/.venv/bin/pip" install sympy scipy matplotlib numpy
fi
PY="$ROOT/.venv/bin/python"
if ! "$PY" -c "import pysat" 2>/dev/null; then
  "$PY" -m pip install python-sat || true
fi

"$PY" analyze_stars.py
"$PY" n1_check.py
gcc -O3 -std=c11 n1_le32.c -o n1_le32 -lm
./n1_le32 8 8 > n1_le32.json
if command -v rustc >/dev/null 2>&1; then
  rustc -O -o verify_n1 verify_n1.rs
  ./verify_n1
fi
"$PY" replay_unions.py --maxk 8
gcc -O3 -std=c11 n1_dfs.c -o n1_dfs -lm
./n1_dfs 12 > n1_dfs_k12.json
"$PY" - <<'PY'
import json
from pathlib import Path
a = json.loads(Path("n1_complete_k12.json").read_text())
b = json.loads(Path("n1_dfs_k12.json").read_text())
assert a["n_unions_visited"] == b["n_unions_visited"]
assert a["found_41"] is False and b["found_41"] is False and b["complete"]
for k in range(4, 13):
    sa, sb = a["slices"][str(k)], b["slices"][str(k)]
    for key in ("n_unions", "n_promising", "tried", "max_seeds", "best_extras"):
        assert sa[key] == sb[key], (k, key, sa[key], sb[key])
print("n1_dfs k=12 matches n1_complete_k12")
PY
"$PY" -c "import bv; t=bv.self_tests(); assert all(v for _,v in t), t"
"$PY" verify.py
echo "Q4_ALL_OK"
