#!/usr/bin/env python3
"""Even-split walk along the occupied (p,n)=(19,3) depth-3 row.

q2 stopped a pinned even BFS at 400,000 collections. q4 continued to
1,200,000 collections with 1,167,098 still in queue. This evaluates
that remainder: reconstruct the same prefix without re-scoring
schemes, then walk the leftover queue.

Paper Theorem 17: even Harnack splits do not change (p,n).  The census
already realises two rungs of the family <a u 1<2 u 1<c>>> with a+c=18,

    a=10  <10 u 1<2 u 1<8>>>     published T-curve
    a=17  <17 u 1<2 u 1<1>>>     published T-curve (bow-tie / nested box)

and the two algebraically open M-schemes sit on the same row at a=4
and a=14.  So the search is a move along an occupied congruence class:
start from the published (19,3) collections, add/drop/swap only even
splits, and score by |a-4| or |a-14| with b pinned at 2.

A hit in collection space is a PL curve.  Orevkov arXiv:2607.19457
shows a non-regular patchwork can be algebraically unrealisable, so a
target is claimed only after haas.regularize plus exact
tcurve.check_convexity.

Modes
  probe                              size the even-split neighbourhoods
  bfs     <out.jsonl> [limit] [skip] exhaustive even add/drop/swap BFS
  resume  <ckpt> <out.jsonl> [limit] continue from a dumped queue
  check-skip                         prefix-skip agrees with a full BFS
  beam    <seed> <minutes> <out>
  family  <seed> <minutes> <out>
"""
import json
import os
import pickle
import random
import sys
import time
from collections import deque
from fractions import Fraction

from common import HERE, boot, known_schemes, resolve_out

boot()

import deepnest as dn
import haas
from dn_charac import shape, nest_depth
from tcurve import check_convexity, validate_triangulation

TARGETS = [(4, 2, 14), (14, 2, 4)]
OPEN = {"<4 u 1<2 u 1<14>>>", "<14 u 1<2 u 1<4>>>"}
Q4_PREFIX = 1_200_000


def bowtie_ids(sp):
    """Prop 31 nested-box collection for d=8."""
    wanted = [
        ((0, 0), (1, 7)),
        ((2, 6), (1, 1), (8, 0)),
        ((3, 5), (2, 2), (7, 1)),
        ((4, 4), (3, 3), (6, 2)),
    ]
    key = {x.key: i for i, x in enumerate(sp)}
    ids = []
    for path in wanted:
        k = path if path[0] < path[-1] else path[::-1]
        if k not in key:
            k = k[::-1]
        if k not in key:
            raise SystemExit(f"bow-tie split missing: {path}")
        ids.append(key[k])
    return sorted(ids)


def seed_collections(sp):
    key = {x.key: i for i, x in enumerate(sp)}
    out = []
    for claimed, rec in sorted(json.load(
            open("certs/mcert_collections.json")).items()):
        if "p19-n03" not in rec.get("cert", ""):
            continue
        ids = []
        ok = True
        for p in rec["collection"]:
            t = tuple(tuple(v) for v in p)
            k = t if t[0] < t[-1] else t[::-1]
            if k not in key:
                ok = False
                break
            ids.append(key[k])
        if ok:
            out.append((claimed, sorted(ids)))
    out.append(("bowtie_B8", bowtie_ids(sp)))
    return out


def even_mask(sp):
    m = 0
    for i, s in enumerate(sp):
        if s.even:
            m |= 1 << i
    return m


def compat_mask(adj, ids):
    n = len(adj)
    m = (1 << n) - 1
    for i in ids:
        m &= adj[i] | (1 << i)
    return m


def ev(sp, ids):
    try:
        return dn.evaluate([sp[i] for i in ids])[:2]
    except ValueError:
        return 0, None


def score(nc, sch):
    if sch is None:
        return 1000.0
    a, b, c, junk = shape(sch)
    best = min(abs(a - ta) + abs(b - tb) + abs(c - tc)
               for ta, tb, tc in TARGETS)
    return 4.0 * abs(b - 2) + 3.0 * (22 - nc) + best + 2.0 * junk


def try_regularize(coll, tries=24):
    """Search for an exact convexity certificate of some refinement."""
    for seed in range(tries):
        rng = random.Random(1000 + seed)
        try:
            tris = dn.fast_refine(coll, rng)
        except ValueError:
            continue
        if len(tris) != 64:
            continue
        if validate_triangulation(8, tris):
            continue
        h = haas.regularize(tris, iters=80000, seed=seed)
        if h is None:
            continue
        frac = {p: Fraction(int(h[p])) for p in h}
        if not check_convexity(8, tris, frac):
            return tris, frac
    return None


class Log:
    def __init__(self, path, known):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        self.f = open(path, "w")
        self.known = known
        self.seen = {}
        self.new = 0
        self.hits = []
        self.best = (1e9, None, None)
        self.evals = 0

    def add(self, ids, nc, sch, mode, sp=None):
        self.evals += 1
        sc = score(nc, sch)
        if sc < self.best[0]:
            self.best = (sc, sch, list(ids))
            self.f.write(json.dumps(
                {"kind": "best", "score": sc, "scheme": sch, "ncomp": nc,
                 "collection": list(ids), "mode": mode}) + "\n")
            self.f.flush()
        if sch is None or sch in self.seen:
            return sc
        self.seen[sch] = list(ids)
        novel = sch not in self.known
        if novel:
            self.new += 1
        rec = {"kind": "NEW" if novel else "scheme", "scheme": sch,
               "ncomp": nc, "shape": list(shape(sch)),
               "depth": nest_depth(sch), "collection": list(ids),
               "mode": mode}
        if sch in OPEN:
            rec["kind"] = "HIT"
            rec["regular"] = False
            if sp is not None:
                coll = [sp[i] for i in ids]
                reg = try_regularize(coll)
                if reg is not None:
                    tris, frac = reg
                    rec["regular"] = True
                    rec["triangles"] = [[list(v) for v in t] for t in tris]
                    rec["heights"] = {f"{p[0]},{p[1]}": int(v)
                                      for p, v in frac.items()}
                    rec["signs"] = {f"{p[0]},{p[1]}": int(s)
                                    for p, s in haas.signs_of(coll).items()}
            self.hits.append(rec)
        self.f.write(json.dumps(rec) + "\n")
        self.f.flush()
        return sc

    def close(self, extra):
        self.f.write(json.dumps({"kind": "summary", "evals": self.evals,
                                 "distinct": len(self.seen),
                                 "new": self.new,
                                 "hits": len(self.hits),
                                 "best_score": self.best[0],
                                 "best_scheme": self.best[1],
                                 **extra}) + "\n")
        self.f.close()


def even_neighbours(ids, adj, emask, pin_odd=False):
    """One even-split add / drop / swap from ids.

    If pin_odd, odd splits in the seed are never dropped (Theorem 17:
    only even twists keep (p,n)).  The first BFS dropped odd splits
    and immediately left the (19,3) row.
    """
    n = len(adj)
    have = set(ids)
    mask = compat_mask(adj, ids)
    for k, i in enumerate(ids):
        if pin_odd and not (emask >> i) & 1:
            continue
        yield ids[:k] + ids[k + 1:]
    for j in range(n):
        if j in have or not (emask >> j) & 1 or not (mask >> j) & 1:
            continue
        yield sorted(ids + [j])
    for k, i in enumerate(ids):
        if pin_odd and not (emask >> i) & 1:
            continue
        sub = ids[:k] + ids[k + 1:]
        m2 = compat_mask(adj, sub)
        for j in range(n):
            if j in have or not (emask >> j) & 1 or not (m2 >> j) & 1:
                continue
            yield sorted(sub + [j])


def dump_ckpt(path, seen, q, walked, extra):
    if not path:
        return
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        pickle.dump({
            "seen": list(seen),
            "queue": list(q),
            "walked": walked,
            **extra,
        }, f, protocol=pickle.HIGHEST_PROTOCOL)
    os.replace(tmp, path)


def load_ckpt(path):
    with open(path, "rb") as f:
        return pickle.load(f)


def run_probe():
    sp = dn.splits()
    adj = dn.compat_matrix()
    emask = even_mask(sp)
    print(f"{len(sp)} splits, {bin(emask).count('1')} even")
    for name, ids in seed_collections(sp):
        nc, sch = ev(sp, ids)
        mask = compat_mask(adj, ids)
        even_ok = [j for j in range(len(sp))
                   if j not in ids and (emask >> j) & 1 and (mask >> j) & 1]
        print(f"  {name}: |S|={len(ids)} {nc} {sch}  "
              f"even-compatible-adds={len(even_ok)}")


def _seed_state(sp):
    q = deque()
    seen = set()
    seeds = []
    for name, ids in seed_collections(sp):
        t = tuple(ids)
        if t in seen:
            continue
        seen.add(t)
        q.append(ids)
        seeds.append((name, ids))
    return q, seen, seeds


def run_bfs(out, limit=200000, pin_odd=True, skip_eval_until=0,
            ckpt=None, quiet=False, log=None, state=None):
    """Pinned even-split BFS.

    skip_eval_until reconstructs that many newly seen collections
    without calling evaluate, then scores the remainder. q4 stored a
    1,200,000-collection prefix; the leftover queue is the rest.
    Complete only if the queue empties.
    """
    sp = dn.splits()
    adj = dn.compat_matrix()
    emask = even_mask(sp)
    lg = log if log is not None else Log(out, known_schemes())
    if state is None:
        q, seen, seeds = _seed_state(sp)
        walked = 0
        for name, ids in seeds:
            walked += 1
            if skip_eval_until <= 0 or walked > skip_eval_until:
                nc, sch = ev(sp, ids)
                lg.add(ids, nc, sch, f"seed/{name}", sp)
    else:
        q, seen, walked = state
        seeds = []

    t0 = time.time()
    last_dump = walked
    ckpt = ckpt or (os.path.splitext(out)[0] + ".ckpt" if out else None)

    def maybe_dump(force=False):
        nonlocal last_dump
        if not ckpt:
            return
        if force or walked - last_dump >= 100000:
            dump_ckpt(ckpt, seen, q, walked, {
                "pin_odd": pin_odd,
                "skip_eval_until": skip_eval_until,
                "remainder_evals": lg.evals,
            })
            last_dump = walked
            if not quiet:
                print(f"  wrote checkpoint walked={walked} queue={len(q)} "
                      f"evals={lg.evals}", flush=True)

    while q and lg.evals < limit:
        ids = q.popleft()
        for nw in even_neighbours(ids, adj, emask, pin_odd=pin_odd):
            t = tuple(nw)
            if t in seen:
                continue
            seen.add(t)
            walked += 1
            if walked <= skip_eval_until:
                q.append(nw)
            else:
                nc, sch = ev(sp, nw)
                lg.add(nw, nc, sch, "bfs", sp)
                q.append(nw)
                if lg.evals >= limit:
                    break
        if not quiet and (
                (lg.evals and lg.evals % 2000 == 0) or
                (skip_eval_until and walked <= skip_eval_until
                 and walked % 100000 == 0)):
            print(f"  bfs walked={walked} evals={lg.evals} queue={len(q)} "
                  f"seen_coll={len(seen)} schemes={len(lg.seen)} "
                  f"new={lg.new} best={lg.best[0]} {lg.best[1]} "
                  f"({time.time()-t0:.0f}s)", flush=True)
        maybe_dump()
    maybe_dump(force=True)
    extra = {"mode": "bfs", "pin_odd": pin_odd, "collections": len(seen),
             "queue_left": len(q), "limit": limit,
             "skip_eval_until": skip_eval_until, "walked": walked,
             "prefix_skipped": min(walked, skip_eval_until),
             "complete": len(q) == 0}
    if out:
        lg.close(extra)
    if not quiet:
        print(f"bfs pin_odd={pin_odd}: walked={walked} {lg.evals} evals, "
              f"{len(lg.seen)} schemes, {lg.new} new, {len(lg.hits)} hits, "
              f"queue={len(q)} best {lg.best[0]} {lg.best[1]}")
    return seen, q, lg, extra


def run_resume(ckpt_path, out, limit=200000):
    rec = load_ckpt(ckpt_path)
    seen = set(tuple(x) for x in rec["seen"])
    q = deque(list(x) for x in rec["queue"])
    walked = int(rec["walked"])
    skip = int(rec.get("skip_eval_until", 0))
    print(f"resume {ckpt_path}: walked={walked} queue={len(q)} "
          f"seen={len(seen)} skip={skip}", flush=True)
    return run_bfs(out, limit=limit, pin_odd=True, skip_eval_until=skip,
                   ckpt=ckpt_path, state=(q, seen, walked))


def run_check_skip(prefix=80, rest=40):
    """The skip-prefix walk must match a full BFS on the same window."""
    import io
    from contextlib import redirect_stdout

    def silent_bfs(limit, skip):
        lg = Log(os.path.join(HERE, "even_out", "_check.jsonl"),
                 known_schemes())
        buf = io.StringIO()
        with redirect_stdout(buf):
            seen, q, lg, extra = run_bfs(
                None, limit=limit, skip_eval_until=skip, quiet=True,
                log=lg, ckpt="")
        return seen, list(q), lg, extra

    seen_a, q_a, lg_a, ex_a = silent_bfs(prefix + rest, 0)
    seen_b, q_b, lg_b, ex_b = silent_bfs(rest, prefix)
    if seen_a != seen_b:
        raise SystemExit(f"check-skip: seen mismatch "
                         f"{len(seen_a)} vs {len(seen_b)}")
    if [tuple(x) for x in q_a] != [tuple(x) for x in q_b]:
        raise SystemExit(f"check-skip: queue mismatch "
                         f"{len(q_a)} vs {len(q_b)}")
    if ex_a["walked"] != ex_b["walked"]:
        raise SystemExit(f"check-skip: walked {ex_a['walked']} "
                         f"vs {ex_b['walked']}")
    print(f"check-skip ok: prefix={prefix} rest={rest} "
          f"walked={ex_a['walked']} queue={len(q_a)} "
          f"full_evals={lg_a.evals} remainder_evals={lg_b.evals}")


def run_beam(seedno, minutes, out, width=50, depth=16):
    sp = dn.splits()
    adj = dn.compat_matrix()
    emask = even_mask(sp)
    lg = Log(out, known_schemes())
    rng = random.Random(seedno)
    deadline = time.time() + minutes * 60
    frontier = []
    seen = set()
    for name, ids in seed_collections(sp):
        t = tuple(ids)
        seen.add(t)
        nc, sch = ev(sp, ids)
        frontier.append((lg.add(ids, nc, sch, f"beam0/{name}", sp), t))
    for d in range(depth):
        cand = []
        for sc, ids in frontier:
            ids = list(ids)
            moves = list(even_neighbours(ids, adj, emask, pin_odd=True))
            rng.shuffle(moves)
            for nw in moves[:80]:
                t = tuple(nw)
                if t in seen:
                    continue
                seen.add(t)
                nc, s = ev(sp, nw)
                cand.append((lg.add(nw, nc, s, f"beam{d}", sp), t))
                if time.time() > deadline:
                    break
            if time.time() > deadline:
                break
        if not cand:
            break
        cand.sort(key=lambda x: (x[0], len(x[1])))
        frontier = cand[:width]
        print(f"  beam depth {d}: evals={lg.evals} schemes={len(lg.seen)} "
              f"new={lg.new} best={lg.best[0]} {lg.best[1]}", flush=True)
        if time.time() > deadline:
            break
    lg.close({"mode": "beam", "seed": seedno, "collections": len(seen)})


def run_family(seedno, minutes, out):
    """Pin b=2 and drive a toward 4 or 14."""
    sp = dn.splits()
    adj = dn.compat_matrix()
    emask = even_mask(sp)
    lg = Log(out, known_schemes())
    rng = random.Random(seedno)
    deadline = time.time() + minutes * 60
    starts = [ids for _, ids in seed_collections(sp)]

    def energy(nc, sch):
        if sch is None:
            return 500.0
        a, b, c, junk = shape(sch)
        return (8.0 * abs(b - 2) + 6.0 * junk + 3.0 * (22 - nc)
                + min(abs(a - 4), abs(a - 14)))

    rounds = 0
    while time.time() < deadline:
        rounds += 1
        ids = list(starts[rng.randrange(len(starts))])
        nc, s = ev(sp, ids)
        lg.add(ids, nc, s, "family", sp)
        e = energy(nc, s)
        for step in range(4000):
            if step % 128 == 0 and time.time() > deadline:
                break
            T = 3.0 * (0.04 / 3.0) ** (step / 4000)
            moves = list(even_neighbours(ids, adj, emask, pin_odd=True))
            if not moves:
                break
            nw = rng.choice(moves)
            nc2, s2 = ev(sp, nw)
            lg.add(nw, nc2, s2, "family", sp)
            e2 = energy(nc2, s2)
            if e2 <= e or rng.random() < pow(2.718281828, (e - e2) / T):
                ids, e = nw, e2
        if rounds % 5 == 0:
            print(f"  family rounds={rounds} evals={lg.evals} "
                  f"best={lg.best[0]} {lg.best[1]}", flush=True)
    lg.close({"mode": "family", "seed": seedno, "rounds": rounds})
    print(f"family {seedno}: {lg.evals} evals, {len(lg.seen)} schemes, "
          f"{lg.new} new, best {lg.best[0]} {lg.best[1]}")


if __name__ == "__main__":
    m = sys.argv[1]
    if m == "probe":
        run_probe()
    elif m == "bfs":
        out = sys.argv[2]
        out = resolve_out(out)
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 200000
        skip = int(sys.argv[4]) if len(sys.argv) > 4 else Q4_PREFIX
        run_bfs(out, limit, pin_odd=True, skip_eval_until=skip)
    elif m == "resume":
        ckpt = resolve_out(sys.argv[2])
        out = resolve_out(sys.argv[3])
        limit = int(sys.argv[4]) if len(sys.argv) > 4 else 200000
        run_resume(ckpt, out, limit)
    elif m == "check-skip":
        p = int(sys.argv[2]) if len(sys.argv) > 2 else 80
        r = int(sys.argv[3]) if len(sys.argv) > 3 else 40
        run_check_skip(p, r)
    elif m == "beam":
        out = resolve_out(sys.argv[4])
        run_beam(int(sys.argv[2]), float(sys.argv[3]), out)
    elif m == "family":
        out = resolve_out(sys.argv[4])
        run_family(int(sys.argv[2]), float(sys.argv[3]), out)
    else:
        raise SystemExit(__doc__)
