#!/bin/sh
# Run one (n,d) CH-triangle SAT instance with kissat and verify.
set -e
n=$1
d=$2
secs=${3:-300}
here=$(dirname "$0")
cnf="$here/certs/ch-${n}-${d}.cnf"
out="$here/certs/ch-${n}-${d}.out"
proof="$here/certs/ch-${n}-${d}.drat"
python3 "$here/encode_ch.py" --n "$n" --d "$d" > "$cnf"
echo "encoded $cnf $(head -1 "$cnf")"
# kissat: --proof writes DRAT on UNSAT
# kissat 4: optional second file is a DRAT proof
"$here/kissat" --time="$secs" "$cnf" "$proof" > "$out" || true
python3 "$here/verify_model.py" "$n" "$d" < "$out"
tail -20 "$out" | head -20
ls -l "$cnf" "$out" "$proof" 2>/dev/null || true
