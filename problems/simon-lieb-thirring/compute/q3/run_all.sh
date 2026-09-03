#!/usr/bin/env bash
# Replay the q3 alternative-method hunt versus CCR 1.44655.
#   1. Weidl interpolation with the HLT endpoint
#   2. Seiringer–Solovej Airy R_1 after Hoffmann–Ostenhof absorption
#   3. Neumann covering local ratios
#   4. 1D trial-potential lower-bound search
#   5. Eden–Foias empirical kappa (not a bound)
#   6. rustc-only Weidl / Airy recomputation
#   7. q2 Clausen envelope (the published-record replay)
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
build="$(mktemp -d)"
trap 'rm -rf "$build"' EXIT
cd "$here"

python3 weidl_interp.py
python3 ss_airy.py
python3 covering_local.py
python3 trial_potential.py
python3 ef_ratio.py

rustc -O -C opt-level=3 -o "$build/verify_alt" verify_alt.rs
"$build/verify_alt"

python3 ../q2/verify_m3.py --cert "$here/../q2/certs/m3_ccr.json"

echo "ok: q3 alternative-method hunt replayed"
