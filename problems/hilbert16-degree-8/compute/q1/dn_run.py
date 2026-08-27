#!/usr/bin/env python3
"""Run parent collection-space sweeps into q1/dn_out.

Modes (same as compute/dn_sweep.py):
  nbhd     one-split add/drop/swap around every published M-collection
  ladder   two-split moves around the depth-3 seeds  [minutes]
  family   anneal toward the open-nest shape         [seed minutes]

usage: python3 q1/dn_run.py <mode> [args...]
"""
import os
import subprocess
import sys

from common import boot, resolve_out

boot()

mode = sys.argv[1] if len(sys.argv) > 1 else "nbhd"
if mode == "nbhd":
    out = resolve_out(sys.argv[2] if len(sys.argv) > 2 else "dn_out/nbhd.jsonl")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    subprocess.check_call([sys.executable, "dn_sweep.py", "nbhd", out])
elif mode == "ladder":
    minutes = sys.argv[2] if len(sys.argv) > 2 else "90"
    out = resolve_out(sys.argv[3] if len(sys.argv) > 3 else "dn_out/ladder.jsonl")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    subprocess.check_call([sys.executable, "dn_sweep.py", "ladder", out, minutes])
elif mode == "family":
    seed = sys.argv[2] if len(sys.argv) > 2 else "0"
    minutes = sys.argv[3] if len(sys.argv) > 3 else "60"
    out = resolve_out(sys.argv[4] if len(sys.argv) > 4 else "dn_out/family.jsonl")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    subprocess.check_call(
        [sys.executable, "dn_sweep.py", "family", seed, minutes, out])
else:
    raise SystemExit(__doc__)
