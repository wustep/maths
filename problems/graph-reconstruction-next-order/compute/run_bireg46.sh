#!/bin/sh
# Generate n=14 graphs of degree sequence 4^{14-s} 6^{s} (s>=3) and
# certify unique full/reduced decks.
set -eu
cd "$(dirname "$0")"
smin=${1:-3}
smax=${2:-$smin}
tag=s${smin}
if [ "$smax" != "$smin" ]; then tag=s${smin}-${smax}; fi
mkdir -p certs logs
echo "generate 4-regular + 2-factor support [$smin,$smax]"
bin/geng -q -d4 -D4 14 \
  | bin/add_twofactor --smin "$smin" --smax "$smax" 2>logs/tf_${tag}.err \
  | bin/shortg -q >"certs/bireg46_${tag}.g6"
echo "unlabeled $(wc -l < certs/bireg46_${tag}.g6)"
bin/deckrecon hash --sample 400 "certs/sample_bireg46_${tag}.txt" \
  <"certs/bireg46_${tag}.g6" >"/tmp/bireg46_${tag}.hash"
./check_unique.sh "/tmp/bireg46_${tag}.hash" | tee "certs/bireg46_${tag}_unique.txt"
python3 verify_labelg.py "certs/sample_bireg46_${tag}.txt" | tee -a "certs/bireg46_${tag}_unique.txt"
