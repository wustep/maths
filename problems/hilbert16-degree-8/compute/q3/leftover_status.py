#!/usr/bin/env python3
"""Print leftover ranks 22–26 thicken status. Residue, not a bound."""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from leftover_watch import (complete_certs, leftover_tasks, ps_args,
                            q2_reserved, running_q3_only, running_thicken_count)
from write_thick_cert import expected_evals


def main():
    leftover = leftover_tasks()
    leftover.sort(key=lambda d: (d["rank"], d["cert"]))
    done = complete_certs()
    lines = ps_args()
    inflight, _ = running_q3_only(lines)
    reserved = q2_reserved(lines, done)
    print(f"leftover {len(done)}/{len(leftover)} complete; "
          f"thicken processes {running_thicken_count(lines)}")
    for t in leftover:
        cert = t["cert"]
        exp = expected_evals(t["rank"])
        if cert in done:
            state = "done"
        elif cert in inflight:
            state = "running-q3"
        elif cert in reserved:
            state = "running-q2"
        else:
            state = "open"
        print(f"  r{t['rank']:2d} {state:10s} {exp:12d}  {cert}")
    if Path("q3/certs/new_schemes.json").exists():
        print("WARNING: q3/certs/new_schemes.json exists")
    else:
        print("no q3/certs/new_schemes.json")


if __name__ == "__main__":
    main()
