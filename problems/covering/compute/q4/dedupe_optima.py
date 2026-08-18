#!/usr/bin/env python3
"""Dedupe harvested 49-column local optima by GL(10,2) equivalence.

Reads every checkpoint under optima/, writes one .cols file per
equivalence class (class representatives), and prints the class map.
Uses the same color-guided backtracking as find_equivalence.py.
"""

import glob
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    reps = []  # (path, columns, holes)
    # seed with the two existing configs
    for pre in ("best_sa_config.cols", "best_lifted_config.cols"):
        p = os.path.join(HERE, pre)
        if os.path.exists(p):
            reps.append(p)
    new_id = 0
    for ck in sorted(glob.glob(os.path.join(HERE, "optima", "ckpt_*.json"))):
        with open(ck) as f:
            data = json.load(f)
        cols = data["columns_decimal"]
        holes = data["best_uncovered"]
        if len(cols) != 49 or len(set(cols)) != 49:
            continue
        tmp = os.path.join(HERE, "optima", "tmp_candidate.cols")
        with open(tmp, "w") as f:
            f.write("# from %s holes=%s\n" % (os.path.basename(ck), holes))
            f.write(" ".join(map(str, cols)) + "\n")
        matched = None
        for rp in reps:
            r = subprocess.run(
                [sys.executable, os.path.join(HERE, "find_equivalence.py"),
                 tmp, rp], capture_output=True, text=True, timeout=600)
            if r.returncode == 0 and "EQUIVALENT" in r.stdout:
                matched = rp
                break
        if matched:
            print("%s (holes=%s) ~ %s" % (os.path.basename(ck), holes,
                                          os.path.basename(matched)))
            os.remove(tmp)
        else:
            new_id += 1
            dst = os.path.join(HERE, "optima",
                               "class_%02d.cols" % new_id)
            os.rename(tmp, dst)
            reps.append(dst)
            print("%s (holes=%s) -> NEW CLASS %s" %
                  (os.path.basename(ck), holes, os.path.basename(dst)))
    print("total classes:", len(reps))
    return 0


if __name__ == "__main__":
    sys.exit(main())
