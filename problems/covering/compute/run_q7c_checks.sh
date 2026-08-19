#!/bin/sh
set -eu

HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROBLEM=$(CDPATH= cd -- "$HERE/.." && pwd)
cd "$PROBLEM"

# Build and independently sweep the explicit r=18 and r=20 partitions.
compute/run_lift_partition_checks.sh

Q7C_CHECK_DIR=$(mktemp -d)
trap 'rm -rf -- "$Q7C_CHECK_DIR"' EXIT HUP INT TERM

# Rebuild only the two new Theorem 7.3 cases.  This deliberately avoids both
# the already-certified r=26 case and any flat 2^38 or 2^41 syndrome sweep.
python3 compute/build_qm35.py \
  --radius2 result/data/H_r18_n815.txt \
  --radius2 result/data/H_r20_n1631.txt \
  --output "$Q7C_CHECK_DIR/H_R3_r38_n13102.txt" \
  --output "$Q7C_CHECK_DIR/H_R3_r41_n26206.txt" \
  --manifest "$Q7C_CHECK_DIR/qm35_build_manifest.json"

cmp "$Q7C_CHECK_DIR/H_R3_r38_n13102.txt" \
  compute/H_R3_r38_n13102.txt
cmp "$Q7C_CHECK_DIR/H_R3_r41_n26206.txt" \
  compute/H_R3_r41_n26206.txt

python3 compute/verify_qm35_identity.py \
  --radius2 result/data/H_r18_n815.txt \
  --radius2-partition compute/partition_r18_n815_p17.txt \
  --partition-blocks 17 \
  --matrix compute/H_R3_r38_n13102.txt \
  --m 9 \
  --published 13118

python3 compute/verify_qm35_identity.py \
  --radius2 result/data/H_r20_n1631.txt \
  --radius2-partition compute/partition_r20_n1631_p14.txt \
  --partition-blocks 14 \
  --matrix compute/H_R3_r41_n26206.txt \
  --m 10 \
  --published 26238

echo "PASS q7c: explicit p(H) certificates and theorem-only r=38,41 lifts"
