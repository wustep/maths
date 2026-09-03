#!/usr/bin/env bash
# Single-thread Gray-code enum of the stored n=37 matrix.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p work certs
gcc -O3 -march=native -o verify_gray verify_gray.c -lm
export GRAY_BACKUP="${GRAY_BACKUP:-/tmp/ion-q13-faces.txt}"
# Resume from an off-tree backup if the worktree dump was wiped.
if [ ! -f certs/beta3_mid_faces_R10_n37_t0p9119.txt ] && [ -f "$GRAY_BACKUP" ]; then
  cp "$GRAY_BACKUP" certs/beta3_mid_faces_R10_n37_t0p9119.txt
fi
exec ./verify_gray \
  certs/beta3_mid_R10_n37_t0p9119.txt \
  certs/beta3_mid_faces_R10_n37_t0p9119.txt
