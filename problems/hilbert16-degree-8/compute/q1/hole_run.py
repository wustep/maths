#!/usr/bin/env python3
"""Run parent hole_balls.py into q1/hole_out (radius 6 around our 17)."""
import os
import subprocess
import sys

from common import boot, resolve_out

boot()
outdir = resolve_out(sys.argv[1] if len(sys.argv) > 1 else "hole_out")
radius = int(sys.argv[2]) if len(sys.argv) > 2 else 6
w = int(sys.argv[3]) if len(sys.argv) > 3 else 0
nw = int(sys.argv[4]) if len(sys.argv) > 4 else 1
os.makedirs(outdir, exist_ok=True)
os.environ["HB_TAG"] = "q"
subprocess.check_call(
    [sys.executable, "hole_balls.py", str(radius), outdir, str(w), str(nw)]
)
