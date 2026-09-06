#!/usr/bin/env python3
"""Cross-check the C endgame against a brute-force 3-step expansion.

Random normalised prefixes are generated; the set of values reachable in at
most three further steps is computed exactly in Python (with the minimal
number of steps); the C binary is run in --endgame-test mode on the same
prefix with a list of member and non-member targets; the answers must agree.
"""
import json, random, subprocess, sys, os, itertools
from sympy import factorint

HERE = os.path.dirname(os.path.abspath(__file__))
BIN = os.environ.get("SLP_BIN", os.path.join(HERE, "slp_search"))

def ops(a, b):
    yield a + b
    yield a * b
    if a != b:
        yield abs(a - b)

def one_step(S):
    out = set()
    for a in S:
        for b in S:
            for r in ops(a, b):
                if r > 0 and r not in S:
                    out.add(r)
    return out

def random_prefix(depth, rng):
    S = [1]
    while len(S) - 1 < depth:
        cand = sorted(one_step(set(S)))
        # bias towards moderately sized values but allow big ones
        v = rng.choice(cand)
        S.append(v)
    return S

def reach3(S):
    """min steps (0..3) for every value reachable in <= 3 steps from set S"""
    best = {v: 0 for v in S}
    S0 = set(S)
    L1 = one_step(S0)
    for y1 in L1:
        best.setdefault(y1, 1)
    for y1 in L1:
        S1 = S0 | {y1}
        L2 = one_step(S1)
        for y2 in L2:
            if best.get(y2, 9) > 2:
                best[y2] = 2
            S2 = S1 | {y2}
            # third step: only values that use y2 (else covered at level <= 2)
            for a in S2:
                for r in ops(a, y2):
                    if r > 0 and best.get(r, 9) > 3:
                        best[r] = 3
    return best

def c_factorable(n):
    """the C binary factors targets by trial division below 2e6 plus a
    Miller-Rabin test on the cofactor (which must be < 2^64)"""
    f = factorint(n)
    big = [p for p in f if p >= 2_000_000]
    if len(big) > 1 or any(f[p] > 1 for p in big):
        return False
    if big and big[0] >= 2**64:
        return False
    return True

def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    trials = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    rng = random.Random(seed)
    total = 0; mism = []
    for trial in range(trials):
        depth = rng.randint(3, 6)
        S = random_prefix(depth, rng)
        best = reach3(S)
        members = [v for v in best if 0 < best[v] <= 3 and v < 2**128 and c_factorable(v)]
        rng.shuffle(members)
        members = members[:150]
        # non-members: neighbours of members and random products
        non = set()
        for v in members[:60]:
            for w in (v + 1, v - 1, v + 2, 2 * v + 1):
                if w > 0 and w not in best and w < 2**128 and c_factorable(w):
                    non.add(w)
        non = sorted(non)[:100]
        targets = members + non
        pfile = os.path.join(HERE, f"_bc_prefix_{seed}.txt"); tfile = os.path.join(HERE, f"_bc_targets_{seed}.txt")
        with open(pfile, "w") as f:
            for v in S[1:]:
                f.write(f"{v}\n")
        with open(tfile, "w") as f:
            for v in targets:
                f.write(f"{v}\n")
        out = subprocess.run([BIN, "--endgame-test", pfile, "--targets", tfile], capture_output=True, text=True)
        if out.returncode != 0:
            print("C binary failed:", out.stderr); sys.exit(1)
        res = json.loads(out.stdout)
        assert res["prefix_steps"] == depth
        for r in res["results"]:
            v = int(r["value"]); got = r["steps"] - depth if r["steps"] >= 0 else -1
            exp = best.get(v, -1)
            if exp > 3: exp = -1
            total += 1
            if got != exp:
                mism.append((S, v, exp, got))
        os.remove(pfile); os.remove(tfile)
        print(f"trial {trial}: depth {depth} prefix {S} members {len(members)} non {len(non)} mismatches so far {len(mism)}", flush=True)
    print(f"checked {total} (prefix, target) pairs; mismatches: {len(mism)}")
    for m in mism[:20]:
        print("  MISMATCH", m)
    sys.exit(1 if mism else 0)

if __name__ == "__main__":
    main()
