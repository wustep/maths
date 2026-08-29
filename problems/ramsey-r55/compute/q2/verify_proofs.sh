#!/bin/sh
# Regenerate every committed CNF and check its compressed DRAT proof.
set -eu
cd "$(dirname "$0")"

if [ ! -x work/drat-trim-bin ]; then
  ./build_tools.sh
fi
mkdir -p cnf proofs logs

for spec in 11_1 11_2 11_3 13_1 13_2 17_1 17_2 19_1 19_2 23_1; do
  p=${spec%_*}
  cycles=${spec#*_}
  name="orbit_n43_p${p}_c${cycles}"
  python3 orbit_sat.py --n 43 --p "$p" --cycles "$cycles" \
    --cnf "cnf/${name}.cnf"
  gzip -dc "certs/proofs/${name}.drat.gz" > "proofs/${name}.drat"
  work/drat-trim-bin "cnf/${name}.cnf" "proofs/${name}.drat" \
    > "logs/replay_drat_p${p}_c${cycles}.txt"
  grep -q 's VERIFIED' "logs/replay_drat_p${p}_c${cycles}.txt"
  echo "VERIFIED cycle type ${p}^${cycles} 1^$((43-p*cycles))"
done

python3 bounded_repair.py certs/local_best2.g6 6 --no-solve \
  --cnf cnf/repair_r6.cnf
gzip -dc certs/proofs/repair_r6.drat.gz > proofs/repair_r6.drat
work/drat-trim-bin cnf/repair_r6.cnf proofs/repair_r6.drat \
  > logs/replay_drat_repair_r6.txt
grep -q 's VERIFIED' logs/replay_drat_repair_r6.txt
echo 'VERIFIED radius-6 repair exclusion'
