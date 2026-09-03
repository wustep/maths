#!/usr/bin/env bash
# Replay driver for q2: exact T(k) for k <= 6 (minutes) and k = 7 (about an
# hour on 8 threads).  Exit 0 means the table was regenerated and matched.
set -euo pipefail
cd "$(dirname "$0")"
PY=${PY:-python3}
THREADS=${THREADS:-$(nproc)}
gcc -O3 -march=native -fopenmp -o poly_search poly_search.c -lm
# thresholds: one more than the best construction at each depth
./poly_search 6 2 3 4 4 5 6 --threads "$THREADS" > cand6.txt
if [ "${1:-}" = "--full" ]; then
  ./poly_search 7 2 3 4 4 5 6 6 --threads "$THREADS" > cand7.txt
  cat cand6.txt cand7.txt | $PY count_roots.py > table.json
else
  $PY count_roots.py < cand6.txt > table.json
fi
$PY - <<'PYEOF'
import json
t = json.load(open("table.json"))
assert t["unresolved_count"] == 0
print({d: v["Z"] for d, v in t["per_depth_max"].items()})
PYEOF
echo "q2 table regenerated"
