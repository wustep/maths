#!/usr/bin/env bash
# Replay driver for q1.  Exit 0 means every control and certificate checked.
#   ./run_all.sh          controls + decisions at 11 and 12 steps (about 30 min on 8 threads)
#   ./run_all.sh --full   also the 13-step decision (several hours on 8 threads)
#   ./run_all.sh --quick  controls only (a few minutes)
set -euo pipefail
cd "$(dirname "$0")"
PY=${PY:-python3}
THREADS=${THREADS:-$(nproc)}
mode=${1:-}

gcc -O3 -march=native -fopenmp -o slp_search slp_search.c
rustc -O -o check check.rs

echo "== control 1: reached-set counts and tau(n), n <= 5000 (9 steps)"
./slp_search --count 9 --table 5000 --threads 1 > count9.json
$PY - <<'PYEOF'
import json
d = json.load(open("count9.json"))
assert d["reached_cumulative"] == [1, 2, 4, 9, 26, 102, 562, 4363, 46154, 652227], d["reached_cumulative"]   # Markstrom Fig. 1
tau = d["tau"]
b = {}
for line in open("b173419.txt"):
    p = line.split()
    if len(p) == 2: b[int(p[0])] = int(p[1])
assert len(b) == 1800 and all(tau[n - 1] == b[n] for n in b), "OEIS A173419 b-file mismatch"
assert [n for n in range(1, 5001) if tau[n - 1] < 0] == []
def isprime(n):
    return n > 1 and all(n % i for i in range(2, int(n ** 0.5) + 1))
cex = [p for p in range(3, 5000) if isprime(p) and tau[p - 1] < tau[p - 2]]
assert cex == [3359, 3623, 4909, 4943], cex   # OEIS A173419 comment, Patane 2026
print("count control ok:", d["reached_cumulative"])
PYEOF

echo "== control 2: Rust enumeration agrees on node counts and reached sets (8 steps)"
./check count 8 > check_count8.json
$PY - <<'PYEOF'
import json
c = json.load(open("check_count8.json"))
assert c["nodes_per_depth"] == [1, 2, 8, 59, 663, 10609, 225219, 6057298], c
assert c["reached_cumulative"] == [1, 2, 4, 9, 26, 102, 562, 4363, 46154], c
print("rust count control ok")
PYEOF

echo "== control 3: endgame versus brute force"
$PY brute_check.py 1 6 | tail -1
$PY compare_endgame.py 10 40 5 | tail -1
$PY compare_endgame.py 7 40 6 | tail -1

if [ "$mode" = "--quick" ]; then echo "quick controls passed"; exit 0; fi

echo "== decisions at 11 and 12 steps (replay of the 2013 record)"
./slp_search --steps 11 --targets targets_core.txt --threads "$THREADS" > decide11_core.json
./slp_search --steps 12 --targets targets_core.txt --threads "$THREADS" > decide12.json
$PY verify_slp.py decide11_core.json decide12.json | tail -1
$PY - <<'PYEOF'
import json
d11 = {t["name"]: t["found_steps"] for t in json.load(open("decide11_core.json"))["targets"]}
d12 = {t["name"]: t["found_steps"] for t in json.load(open("decide12.json"))["targets"]}
assert d11["13!"] == 11 and d11["14!"] == 11 and all(d11[k] is None for k in d11 if k not in ("13!", "14!")), d11
assert all(d12[k] == 12 for k in ("15!", "16!", "17!")) and all(d12[k] is None for k in ("18!", "19!", "20!", "21!", "22!")), d12
print("12-step replay ok:", d12)
PYEOF

if [ "$mode" = "--full" ]; then
  echo "== decision at 13 steps (crash-safe; resumes from ck13.txt if present)"
  ulimit -s unlimited 2>/dev/null || true; export OMP_STACKSIZE=512M
  ./slp_search --steps 13 --targets targets13.txt --threads "$THREADS" --split 6 --checkpoint ck13.txt > decide13.json
  $PY decide_from_checkpoint.py ck13.txt 10609 13 \
      "20!=2432902008176640000" "21!=51090942171709440000" \
      "22!=1124000727777607680000" "37#=7420738134810" > decide13_from_ckpt.json
  $PY verify_slp.py decide13.json | tail -1
fi

$PY make_certificate.py
echo "all checks passed"
