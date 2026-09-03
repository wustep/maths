#!/usr/bin/env python3
"""Sample deep canonical prefixes with the Rust checker's random descent,
decide reachability of the core targets by the Rust brute-force expansion,
and compare with the C endgame (slp_search --endgame-test).

Usage: python3 compare_endgame.py DEPTH TRIALS SEED [targets file]
"""
import json, os, subprocess, sys
from sympy import factorint, isprime

def c_factorable(n):
    """slp_search factors targets by trial division below 2e6 plus a primality
    test on the cofactor, which must be below 2^64"""
    f = factorint(n, limit=2_000_000)
    rest = 1
    for p, e in f.items():
        if p >= 2_000_000:
            rest *= p ** e
    return rest == 1 or (rest < 2**64 and isprime(rest))

HERE = os.path.dirname(os.path.abspath(__file__))
depth, trials, seed = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
tfile = sys.argv[4] if len(sys.argv) > 4 else os.path.join(HERE, "targets_core.txt")
out = subprocess.run([os.environ.get("CHECK_BIN", os.path.join(HERE, "check")), "sample", str(depth), str(trials), str(seed), tfile], capture_output=True, text=True, check=True)
names = [l.split()[0] for l in open(tfile) if l.strip() and not l.startswith('#')]
total = 0; mism = []; hits = 0
for line in out.stdout.splitlines():
    rec = json.loads(line)
    pfile = os.path.join(HERE, f"_cmp_prefix_{seed}.txt"); tf2 = os.path.join(HERE, f"_cmp_targets_{seed}.txt")
    with open(pfile, "w") as f:
        for v in rec["prefix"][1:]:
            f.write(v + "\n")
    vals = [l.split()[1] for l in open(tfile) if l.strip() and not l.startswith('#')]
    expected = {v: r["steps"] for v, r in zip(vals, rec["results"])}
    for m in rec["members"]:
        v = int(m["value"])
        if v in (int(x) for x in vals) or v >= 2**128 or not c_factorable(v):
            continue
        expected[str(v)] = m["steps"]
    with open(tf2, "w") as f:
        for v in expected:
            f.write(f"{v}\n")
    c = subprocess.run([os.environ.get("SLP_BIN", os.path.join(HERE, "slp_search")), "--endgame-test", pfile, "--targets", tf2], capture_output=True, text=True)
    if c.returncode != 0:
        print("C failed:", c.stderr); sys.exit(1)
    cres = json.loads(c.stdout)
    assert cres["prefix_steps"] == depth
    cmap = {r["value"]: r["steps"] for r in cres["results"]}
    for val, exp in expected.items():
        got = cmap[val] - depth if cmap[val] >= 0 else -1
        total += 1
        if exp >= 0: hits += 1
        if exp != got:
            mism.append((rec["prefix"], val, exp, got))
    os.remove(pfile); os.remove(tf2)
print(json.dumps({"depth": depth, "trials": trials, "seed": seed, "pairs": total, "reachable_pairs": hits, "mismatches": len(mism)}))
for m in mism[:10]:
    print("MISMATCH", m)
sys.exit(1 if mism else 0)
