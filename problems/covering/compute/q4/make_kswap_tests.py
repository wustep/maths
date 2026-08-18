#!/usr/bin/env python3
"""Build planted positive controls for the kswap prover.

Reads the certified 50-column matrix, corrupts k columns (deterministic
choices), and writes 50-column configurations for which a k-swap back to
zero holes is known to exist (restore the corrupted columns).  The
kswap binary compiled with -DN_COLS=50 must report KSWAP-FOUND at
j <= k for each.  Also extracts 49-column configurations from search
checkpoints into plain .cols files for the real prover.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
COMPUTE = os.path.dirname(HERE)


def read_h50():
    rows = []
    with open(os.path.join(COMPUTE, "H_r10_n50.txt")) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            rows.append([int(t) for t in line.split()])
    assert len(rows) == 10 and all(len(r) == 50 for r in rows)
    cols = []
    for j in range(50):
        v = 0
        for i in range(10):
            v |= rows[i][j] << i
        cols.append(v)
    return cols


def main():
    cols = read_h50()
    used = set(cols)
    # deterministic junk values not colliding with the matrix
    junk = []
    v = 1
    while len(junk) < 4:
        if v not in used:
            junk.append(v)
            used.add(v)
        v += 1
    for k in (1, 2, 3, 4):
        corrupted = list(cols)
        # corrupt columns at deterministic positions 3, 17, 29, 41
        positions = [3, 17, 29, 41][:k]
        for t, p in enumerate(positions):
            corrupted[p] = junk[t]
        path = os.path.join(HERE, "test_corrupt%d.cols" % k)
        with open(path, "w") as f:
            f.write("# H50 with %d corrupted columns; a %d-swap to 0 holes "
                    "exists by construction\n" % (k, k))
            f.write(" ".join(str(c) for c in corrupted) + "\n")
        print("wrote", path)

    # extract checkpoint configurations into .cols files
    for name, tag in (("q4_search_checkpoint.json", "sa"),
                      ("q4_lifted_checkpoint.json", "lifted")):
        src = os.path.join(HERE, name)
        if not os.path.exists(src):
            continue
        with open(src) as f:
            data = json.load(f)
        cols49 = data.get("columns_decimal") or data.get("best_columns")
        if cols49 is None or len(cols49) != 49 or len(set(cols49)) != 49:
            print("skip", name, "(no clean 49-column list)")
            continue
        dst = os.path.join(HERE, "best_%s_config.cols" % tag)
        with open(dst, "w") as f:
            f.write("# 49-column configuration extracted from %s "
                    "(uncovered=%s)\n" % (name, data.get("best_uncovered")))
            f.write(" ".join(str(c) for c in cols49) + "\n")
        print("wrote", dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())
