#!/usr/bin/env bash
# Replay the C_1 panel certificates.
#   1. Python writes compute/certs/c1_*.json and checks C_1_upper < 1.456·4/(9√3)
#   2. rustc-only verifier recomputes each certificate independently
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
certs="$(cd "$here/../certs" && pwd)"
build="$(mktemp -d)"
trap 'rm -rf "$build"' EXIT

python3 "$here/verify_c1.py" --certs-dir "$certs" --q1-dir "$here"

rustc -O -C opt-level=3 -o "$build/verify_c1" "$here/verify_c1.rs"

shopt -s nullglob
certs_found=("$certs"/c1_*.json)
if (( ${#certs_found[@]} == 0 )); then
  echo "error: no certificates in $certs" >&2
  exit 1
fi
for cert in "${certs_found[@]}"; do
  echo "rust: $cert"
  "$build/verify_c1" "$cert"
done

echo "ok: C_1 panel certificates replayed"
