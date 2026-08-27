#!/usr/bin/env bash
# Replay the q2 Carvalho Corso–Ried / Clausen envelope.
#   1. Float three-lines integral (not a bound)
#   2. Python Clausen series → compute/q2/certs/m3_ccr.json
#   3. rustc-only recomputation with a different n_terms and tail
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
build="$(mktemp -d)"
trap 'rm -rf "$build"' EXIT

python3 "$here/replay_m3.py"
python3 "$here/verify_m3.py" --cert "$here/certs/m3_ccr.json"

rustc -O -C opt-level=3 -o "$build/verify_m3" "$here/verify_m3.rs"
"$build/verify_m3" "$here/certs/m3_ccr.json"

echo "ok: q2 Clausen envelope replayed"
