#!/usr/bin/env python3
"""Deep-nest-anchored search on the census's own triangulations.

Three modes, all seeded at published census witnesses (this is the
"steal the geometry that already produced a deep nest" attack, replacing
the failed random-triangulation simulated annealing):

  ball    exhaustive Hamming-ball enumeration around a seed sign vector
          (radius <= 5), exact local coverage, no stochastics;
  beam    best-first beam search moving along the pure deep-nest family
          <a u 1<2 u 1<c>>>: score rewards staying in the family and
          growing it toward a target (a*, c*);
  window  exhaustive 2^k enumeration of a k-bit sign window (all other
          bits pinned to the seed witness), window chosen by a bit-order
          file; gives an exact "no new scheme in this window" statement.

Every distinct scheme evaluated is diffed against the replayed census
(census_schemes.txt); anything not in it is logged with its full
witness for exact re-verification by tcurve.py (fastcx is only an
accelerator).  Output JSONL matches search_m8.py so verify_found.py
can aggregate.

Usage:
  python3 nest_search.py <tasks.json> <outfile.jsonl>

tasks.json: list of task objects
  {"mode":"ball","tri":..,"heights":..,"signs":{"i,j":+-1},"radius":r,
   "seed_name":..,"combo_lo":i0,"combo_hi":i1}       # slice of combos
  {"mode":"beam","tri":..,"heights":..,"signs":..,"seed_name":..,
   "target":[a,c],"width":W,"depth":D}
  {"mode":"window","tri":..,"heights":..,"signs":..,"seed_name":..,
   "bits":[[i,j],...],"lo":n0,"hi":n1}               # slice of 2^k
"""

import itertools
import json
import sys
import time

from fastcx import Complex
from notation import parse as parse_scheme

D8 = 8


def load_census():
    with open("census_schemes.txt") as f:
        return {line.strip() for line in f if line.strip()}


def profile(scheme):
    """(a, b, c, junk) for shape <a u 1<b u 1<c>>>; junk = ovals that
    do not fit the pure shape."""
    forest, _ = parse_scheme(scheme)

    def size(t):
        return sum(1 + size(x) for x in t)

    a = sum(1 for t in forest if t == ())
    nests = [t for t in forest if t != ()]
    if not nests:
        return a, 0, 0, 0
    big = max(nests, key=size)
    junk = sum(size(t) + 1 for t in nests if t is not big)
    b = sum(1 for x in big if x == ())
    inner = [x for x in big if x != ()]
    if not inner:
        return a, b, 0, junk
    ibig = max(inner, key=size)
    junk += sum(size(x) + 1 for x in inner if x is not ibig)
    c = sum(1 for y in ibig if y == ())
    junk += sum(size(y) + 1 for y in ibig if y != ())
    return a, b, c, junk


class Logger:
    def __init__(self, out, census, cx_pts):
        self.out = out
        self.census = census
        self.pts = cx_pts
        self.seen = set()
        self.new = 0
        self.frontier = {}   # (a,c) -> max a+c seen in pure family

    def log(self, scheme, signs, task, extra=None):
        if scheme is None or scheme in self.seen:
            return
        self.seen.add(scheme)
        rec = None
        if scheme not in self.census:
            self.new += 1
            rec = {"kind": "NEW", "scheme": scheme}
        else:
            a, b, c, junk = profile(scheme)
            if b == 2 and junk == 0 and a + c >= 16:
                rec = {"kind": "frontier", "scheme": scheme,
                       "abc": [a, b, c]}
        if rec is not None:
            rec["task"] = {k: task[k] for k in ("mode", "seed_name")
                           if k in task}
            if extra:
                rec.update(extra)
            rec["signs"] = {f"{p[0]},{p[1]}": s
                            for p, s in zip(self.pts, signs)}
            self.out.write(json.dumps(rec) + "\n")
            self.out.flush()


def build(task):
    tris = [tuple(tuple(v) for v in t) for t in task["triangles"]]
    cx = Complex(D8, tris)
    sm = {tuple(int(x) for x in k.split(",")): v
          for k, v in task["signs"].items()}
    seed = [sm[p] for p in cx.base_pts]
    return cx, seed


def run_ball(task, logger_out, census, stats):
    cx, seed = build(task)
    lg = Logger(logger_out, census, cx.base_pts)
    n = len(seed)
    r = task["radius"]
    lo, hi = task.get("combo_lo", 0), task.get("combo_hi", None)
    combos = itertools.chain.from_iterable(
        itertools.combinations(range(n), k) for k in range(r + 1))
    signs = list(seed)
    for idx, combo in enumerate(combos):
        if hi is not None and not (lo <= idx < hi):
            continue
        for k in combo:
            signs[k] = -signs[k]
        nc, s = cx.eval(signs)
        stats["evals"] += 1
        lg.log(s, signs, task, {"dist": len(combo)})
        for k in combo:
            signs[k] = -signs[k]
    stats["distinct"] += len(lg.seen)
    stats["new"] += lg.new


def beam_score(scheme, ncomp, target):
    """Higher is better.  Reward pure family shape and closeness of
    (a,c) to target; heavily reward total ovals."""
    if scheme is None:
        return -1000.0
    a, b, c, junk = profile(scheme)
    ta, tc = target
    s = 10.0 * ncomp
    s -= 6.0 * abs(b - 2)
    s -= 8.0 * junk
    s -= 3.0 * (abs(a - ta) + abs(c - tc))
    return s


def run_beam(task, logger_out, census, stats):
    cx, seed = build(task)
    lg = Logger(logger_out, census, cx.base_pts)
    width, depth = task["width"], task["depth"]
    target = tuple(task["target"])
    nc0, s0 = cx.eval(seed)
    lg.log(s0, seed, task, {"beam_depth": 0})
    frontier = [(beam_score(s0, nc0, target), tuple(seed))]
    seen_vec = {tuple(seed)}
    for dep in range(1, depth + 1):
        cand = []
        for sc, vec in frontier:
            signs = list(vec)
            for k in range(len(signs)):
                signs[k] = -signs[k]
                tv = tuple(signs)
                if tv not in seen_vec:
                    seen_vec.add(tv)
                    nc, s = cx.eval(signs)
                    stats["evals"] += 1
                    lg.log(s, signs, task, {"beam_depth": dep})
                    cand.append((beam_score(s, nc, target), tv))
                signs[k] = -signs[k]
        if not cand:
            break
        cand.sort(reverse=True)
        frontier = cand[:width]
    stats["distinct"] += len(lg.seen)
    stats["new"] += lg.new


def run_window(task, logger_out, census, stats):
    cx, seed = build(task)
    lg = Logger(logger_out, census, cx.base_pts)
    bits = [tuple(b) for b in task["bits"]]
    pidx = {p: k for k, p in enumerate(cx.base_pts)}
    bidx = [pidx[b] for b in bits]
    k = len(bits)
    lo, hi = task.get("lo", 0), task.get("hi", 1 << k)
    signs = list(seed)
    prev = 0
    for m in range(lo, hi):
        g = m ^ (m >> 1)            # Gray code: one bit flips per step
        diff = g ^ prev
        while diff:
            b = diff & -diff
            j = b.bit_length() - 1
            signs[bidx[j]] = -signs[bidx[j]]
            diff ^= b
        prev = g
        nc, s = cx.eval(signs)
        stats["evals"] += 1
        lg.log(s, signs, task, {"window_m": m})
    stats["distinct"] += len(lg.seen)
    stats["new"] += lg.new


def main():
    tasks = json.load(open(sys.argv[1]))
    out = open(sys.argv[2], "w")
    census = load_census()
    stats = {"evals": 0, "distinct": 0, "new": 0}
    t0 = time.time()
    for task in tasks:
        {"ball": run_ball, "beam": run_beam,
         "window": run_window}[task["mode"]](task, out, census, stats)
    stats["seconds"] = round(time.time() - t0, 1)
    out.write(json.dumps({"kind": "summary", **stats}) + "\n")
    out.close()
    print(f"{sys.argv[2]}: {stats}")


if __name__ == "__main__":
    main()
