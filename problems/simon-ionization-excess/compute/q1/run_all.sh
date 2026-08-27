#!/usr/bin/env bash
# Replay entry point for q1. Exit 0 only if published-record checks succeed.
# Sibling workers may add replay_*.py / hylleraas.py / HF scripts; invoke
# those if present. Heuristic HF/ΔE steps are non-fatal.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p certs

run_if_present() {
  local f="$1"
  if [ -f "$f" ]; then
    echo "==> $f"
    python3 "$f"
  else
    echo "==> skip $f (not present)"
  fi
}

# Published-record replays and remainder arithmetic (fatal if present).
run_if_present replay_hps.py
run_if_present tighten_hps.py
run_if_present replay_nam_beta.py
run_if_present hylleraas.py

echo "==> verify_b3.c"
gcc -O2 -o verify_b3 verify_b3.c -lm
./verify_b3

echo "==> verify_b3.rs"
rustc -O -o verify_b3_rs verify_b3.rs
./verify_b3_rs

echo "==> compare_bounds.py"
python3 compare_bounds.py

# Heuristics: must not fail the published-record replay.
if [ -f rhf_atoms.py ]; then
  echo "==> rhf_atoms.py (heuristic, non-fatal)"
  python3 rhf_atoms.py || echo "WARN: rhf_atoms.py failed (heuristic)"
fi
if [ -f delta_e_table.py ]; then
  echo "==> delta_e_table.py (heuristic, non-fatal)"
  python3 delta_e_table.py || echo "WARN: delta_e_table.py failed (heuristic)"
fi

echo "q1 published-record replay PASS"
