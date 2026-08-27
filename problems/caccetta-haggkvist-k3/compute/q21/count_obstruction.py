#!/usr/bin/env python3
"""Counting and forcing checks on leftover Caccetta–Häggkvist cubes.

A leftover cube fixes N⁺(0)=A={1..d}, N⁻(0)=B={d+1..d+k}, U the rest,
forbids every A→B arc, and asks for a C₃-free oriented d-outregular graph.
Pigeonhole uses k≥d; the N⁺ counting cut empties k>n-2-d.

High-k cubes have slack σ=n-2-d-k small. Each a∈A must take d outs from
the d+σ vertices (A\\{a})∪U, so it omits exactly σ of them. Avoiding
2-cycles in A needs at least C(d,2) A-omissions, hence dσ ≥ C(d,2), i.e.
σ ≥ (d-1)/2. Equality forces A to be a tournament, and the only C₃-free
tournaments are transitive, whose out-degrees {0,1,...,d-1} cannot all
meet s_a ≥ d-u = d-σ-1.

That covering count leaves the k≈d cubes (σ large). This file also runs
combinatorial unit propagation (forced / forbidden arcs + exact degree)
and failed-literal probing on the arc variables, without Sinz auxiliaries
or lex SB. A UP/FL contradiction is a forcing proof; it is not by itself
a kissat DRAT. Certificates still come from encode.py + kissat + drat-trim.

Do not treat 0.3388 as published. This script does not claim a published
threshold movement.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from holes import ceil_div, cube_range, remaining_after_q3


def slack(n: int, d: int, k: int) -> int:
    """σ = |(A\\{a}) ∪ U| − d = u − 1 = n − 2 − d − k."""
    return n - 2 - d - k


def survive_k_range(n: int, d: int) -> list[int]:
    """Needed cubes k≥d that the covering count does not empty.

    Survive when σ ≥ floor((d−1)/2)+1, i.e. k ≤ n−3−d−floor((d−1)/2).
    Equality σ=(d−1)/2 (d odd) is the transitive-tournament kill, not a
    survivor.
    """
    sigma_min = (d - 1) // 2 + 1
    k_max = n - 2 - d - sigma_min
    k_min = d
    if k_min > k_max:
        return []
    return list(range(k_min, k_max + 1))


def covering_obstruction(n: int, d: int, k: int) -> dict:
    """2-cycle covering on A, plus the transitive-tournament equality case.

    Returns a record. ``kills`` is True when this count already empties the
    cube. Not a lower bound on anything; a verified empty cube is a dent
    only after a DRAT or a written proof.
    """
    u = n - 1 - d - k
    sigma = slack(n, d, k)
    need_omit = d * (d - 1) // 2
    have_omit = d * sigma
    min_s = d - u  # each a needs at least this many outs in A
    rec = {
        "n": n,
        "d": d,
        "k": k,
        "u": u,
        "sigma": sigma,
        "binom_d_2": need_omit,
        "max_A_omissions": have_omit,
        "min_s_A": min_s,
        "kills": False,
        "reason": None,
    }
    if k < d:
        rec["reason"] = "below-pigeonhole"
        return rec
    if k > n - 2 - d:
        rec["kills"] = True
        rec["reason"] = "Nplus-count"  # fewer than d legal targets
        return rec
    if sigma < 0:
        rec["kills"] = True
        rec["reason"] = "negative-slack"
        return rec
    if have_omit < need_omit:
        rec["kills"] = True
        rec["reason"] = "2cycle-covering"
        rec["deficit"] = need_omit - have_omit
        return rec
    if have_omit == need_omit:
        # Every omission sits in A, A is a tournament, C₃-free ⇒ transitive,
        # so the out-degrees in A are {0,1,...,d-1}. Need every s_a ≥ min_s.
        # The sink side of a transitive tournament fails this unless min_s ≤ 0
        # and we only need the source, or d=1.
        tt_low = 0
        if tt_low < min_s or d > 1 and min_s > 0:
            rec["kills"] = True
            rec["reason"] = "covering-eq-transitive-tournament"
            rec["tt_degrees"] = "0..d-1"
            rec["need_s_A"] = min_s
            return rec
    rec["reason"] = "survives-covering"
    rec["surplus_omissions"] = have_omit - need_omit
    return rec


class ArcProp:
    """Exact-degree + oriented + triangle unit propagation on arc variables."""

    def __init__(self, n: int, d: int, k: int):
        self.n = n
        self.d = d
        self.k = k
        self.out = [0] * n
        self.inn = [0] * n
        self.forb = [0] * n
        self.need = [d] * n
        self.conflict = None
        self.n_force = 0
        self.n_forbid = 0
        self.queue_arc: list[tuple[int, int]] = []
        self.queue_deg: list[int] = []
        all_mask = (1 << n) - 1
        self.all = all_mask
        for i in range(n):
            self.forb[i] |= 1 << i
        # Vertex 0: N⁺ = A = {1..d}
        A = range(1, d + 1)
        B = range(d + 1, d + k + 1)
        U = range(d + k + 1, n)
        for a in A:
            self._force(0, a)
            self._forbid(a, 0)
        for j in range(d + 1, n):
            self._forbid(0, j)
        for b in B:
            self._force(b, 0)
        for u in U:
            self._forbid(u, 0)
        for a in A:
            for b in B:
                self._forbid(a, b)
        self.need[0] = d

    def _force(self, i: int, j: int) -> None:
        if self.conflict:
            return
        bit = 1 << j
        if self.forb[i] & bit:
            self.conflict = f"force-forbidden {i}->{j}"
            return
        if self.out[i] & bit:
            return
        self.out[i] |= bit
        self.inn[j] |= 1 << i
        self.n_force += 1
        self.queue_arc.append((i, j))
        self.queue_deg.append(i)
        self._forbid(j, i)

    def _forbid(self, i: int, j: int) -> None:
        if self.conflict:
            return
        bit = 1 << j
        if self.out[i] & bit:
            self.conflict = f"forbid-forced {i}->{j}"
            return
        if self.forb[i] & bit:
            return
        self.forb[i] |= bit
        self.n_forbid += 1
        self.queue_deg.append(i)

    def _process_arc(self, i: int, j: int) -> None:
        # i→j: for k in N⁺(j), forbid k→i; for k in N⁻(i), forbid j→k.
        outs_j = self.out[j]
        m = outs_j
        while m:
            lsb = m & -m
            kk = lsb.bit_length() - 1
            m ^= lsb
            self._forbid(kk, i)
        inns_i = self.inn[i]
        m = inns_i
        while m:
            lsb = m & -m
            kk = lsb.bit_length() - 1
            m ^= lsb
            self._forbid(j, kk)

    def _tighten(self, v: int) -> None:
        if self.conflict:
            return
        possible = self.all & ~self.forb[v]
        n_out = self.out[v].bit_count()
        n_pos = possible.bit_count()
        need = self.need[v]
        if n_out > need:
            self.conflict = f"deg-over v={v} out={n_out}>{need}"
            return
        if n_pos < need:
            self.conflict = f"deg-under v={v} possible={n_pos}<{need}"
            return
        if n_out == need:
            extra = possible ^ self.out[v]
            m = extra
            while m:
                lsb = m & -m
                j = lsb.bit_length() - 1
                m ^= lsb
                self._forbid(v, j)
        if n_pos == need:
            missing = possible ^ self.out[v]
            m = missing
            while m:
                lsb = m & -m
                j = lsb.bit_length() - 1
                m ^= lsb
                self._force(v, j)

    def propagate(self) -> bool:
        """Run to a fixpoint. True means conflict (cube empty)."""
        while self.queue_arc or self.queue_deg:
            if self.conflict:
                return True
            while self.queue_arc:
                i, j = self.queue_arc.pop()
                self._process_arc(i, j)
                if self.conflict:
                    return True
            while self.queue_deg:
                v = self.queue_deg.pop()
                self._tighten(v)
                if self.conflict:
                    return True
        return bool(self.conflict)

    def undecided(self) -> list[tuple[int, int]]:
        pairs = []
        for i in range(self.n):
            unk = self.all & ~self.forb[i] & ~self.out[i]
            m = unk
            while m:
                lsb = m & -m
                j = lsb.bit_length() - 1
                m ^= lsb
                # oriented: only list i<j to probe each pair once as (i→j)
                pairs.append((i, j))
        return pairs

    def snapshot(self) -> dict:
        return {
            "out": self.out[:],
            "inn": self.inn[:],
            "forb": self.forb[:],
            "n_force": self.n_force,
            "n_forbid": self.n_forbid,
            "conflict": self.conflict,
        }

    def restore(self, snap: dict) -> None:
        self.out = snap["out"][:]
        self.inn = snap["inn"][:]
        self.forb = snap["forb"][:]
        self.n_force = snap["n_force"]
        self.n_forbid = snap["n_forbid"]
        self.conflict = snap["conflict"]
        self.queue_arc.clear()
        self.queue_deg.clear()

    def clone(self) -> "ArcProp":
        other = ArcProp.__new__(ArcProp)
        other.n = self.n
        other.d = self.d
        other.k = self.k
        other.out = self.out[:]
        other.inn = self.inn[:]
        other.forb = self.forb[:]
        other.need = self.need[:]
        other.conflict = self.conflict
        other.n_force = self.n_force
        other.n_forbid = self.n_forbid
        other.queue_arc = []
        other.queue_deg = []
        other.all = self.all
        return other


def run_up(n: int, d: int, k: int) -> dict:
    p = ArcProp(n, d, k)
    empty = p.propagate()
    unk = 0 if empty else sum(
        (p.all & ~p.forb[i] & ~p.out[i]).bit_count() for i in range(n)
    )
    return {
        "n": n,
        "d": d,
        "k": k,
        "up_unsat": empty,
        "conflict": p.conflict,
        "forced_arcs": p.n_force,
        "forbids": p.n_forbid,
        "undecided_arcs": unk,
    }


def run_up_failed_literals(n: int, d: int, k: int, max_rounds: int = 8) -> dict:
    """UP, then failed-literal probing on undecided arcs.

    If forcing i→j UP-conflicts, forbid it; if forbidding UP-conflicts, force
    it; if both conflict, the cube is empty. Repeats to a fixpoint or
    ``max_rounds``.
    """
    p = ArcProp(n, d, k)
    if p.propagate():
        return {
            "n": n,
            "d": d,
            "k": k,
            "up_unsat": True,
            "fl_unsat": True,
            "fl_rounds": 0,
            "fl_learned": 0,
            "conflict": p.conflict,
            "forced_arcs": p.n_force,
            "undecided_arcs": 0,
        }
    learned = 0
    rounds = 0
    for rounds in range(1, max_rounds + 1):
        progressed = False
        pairs = p.undecided()
        # Probe each undecided directed arc once.
        i = 0
        while i < len(pairs):
            a, b = pairs[i]
            i += 1
            if p.conflict:
                break
            if (p.out[a] & (1 << b)) or (p.forb[a] & (1 << b)):
                continue
            snap = p.snapshot()
            p._force(a, b)
            force_bad = p.propagate()
            p.restore(snap)
            p._forbid(a, b)
            forb_bad = p.propagate()
            p.restore(snap)
            if force_bad and forb_bad:
                return {
                    "n": n,
                    "d": d,
                    "k": k,
                    "up_unsat": False,
                    "fl_unsat": True,
                    "fl_rounds": rounds,
                    "fl_learned": learned,
                    "conflict": f"failed-literal both {a}->{b}",
                    "forced_arcs": p.n_force,
                    "undecided_arcs": sum(
                        (p.all & ~p.forb[x] & ~p.out[x]).bit_count()
                        for x in range(n)
                    ),
                }
            if force_bad:
                p._forbid(a, b)
                p.propagate()
                learned += 1
                progressed = True
            elif forb_bad:
                p._force(a, b)
                p.propagate()
                learned += 1
                progressed = True
            if p.conflict:
                return {
                    "n": n,
                    "d": d,
                    "k": k,
                    "up_unsat": False,
                    "fl_unsat": True,
                    "fl_rounds": rounds,
                    "fl_learned": learned,
                    "conflict": p.conflict,
                    "forced_arcs": p.n_force,
                    "undecided_arcs": 0,
                }
        if not progressed:
            break
        if p.propagate():
            return {
                "n": n,
                "d": d,
                "k": k,
                "up_unsat": False,
                "fl_unsat": True,
                "fl_rounds": rounds,
                "fl_learned": learned,
                "conflict": p.conflict,
                "forced_arcs": p.n_force,
                "undecided_arcs": 0,
            }
    unk = sum(
        (p.all & ~p.forb[i] & ~p.out[i]).bit_count() for i in range(n)
    )
    return {
        "n": n,
        "d": d,
        "k": k,
        "up_unsat": False,
        "fl_unsat": False,
        "fl_rounds": rounds,
        "fl_learned": learned,
        "conflict": None,
        "forced_arcs": p.n_force,
        "undecided_arcs": unk,
    }


def scan_covering(n_min: int = 73, n_max: int = 120) -> dict:
    rows = []
    leftover = remaining_after_q3(n_max=n_max)
    leftover_ns = {r["n"] for r in leftover if r["n"] >= n_min}
    for n in range(n_min, n_max + 1):
        d = ceil_div(n, 3)
        info = cube_range(n, d)
        ks = info["needed_cubes"]
        killed = []
        survive = []
        for k in ks:
            rec = covering_obstruction(n, d, k)
            if rec["kills"]:
                killed.append(k)
            else:
                survive.append(k)
        assert survive == survive_k_range(n, d)
        rows.append(
            {
                "n": n,
                "d": d,
                "needed": ks,
                "killed_by_covering": killed,
                "survives_covering": survive,
                "n_survive": len(survive),
                "leftover_vs_f4": n in leftover_ns,
            }
        )
    return {
        "n_min": n_min,
        "n_max": n_max,
        "rows": rows,
        "n_with_survivors": [r["n"] for r in rows if r["survives_covering"]],
        "all_killed": all(not r["survives_covering"] for r in rows),
        "n_cubes_killed": sum(len(r["killed_by_covering"]) for r in rows),
        "n_cubes_survive": sum(len(r["survives_covering"]) for r in rows),
        "note": (
            "covering = 2-cycle omissions on A plus transitive-tournament "
            "equality. Survivors still need SAT, UP, or a stronger count. "
            "Not a published-threshold claim."
        ),
    }


def self_test() -> None:
    """Replay the n=21 / n=73 covering table and the σ=0 UP kill."""
    r = covering_obstruction(21, 7, 7)
    assert r["reason"] == "survives-covering" and not r["kills"]
    r = covering_obstruction(21, 7, 9)
    assert r["kills"] and r["reason"] == "covering-eq-transitive-tournament"
    r = covering_obstruction(21, 7, 10)
    assert r["kills"] and r["reason"] == "2cycle-covering"
    r = covering_obstruction(21, 7, 13)
    assert r["kills"] and r["reason"] == "Nplus-count"
    up = run_up(21, 7, 12)
    assert up["up_unsat"], up
    up = run_up(21, 7, 7)
    assert not up["up_unsat"], up
    surv = survive_k_range(73, 25)
    assert surv == list(range(25, 34)), surv
    scan = scan_covering(73, 80)
    for row in scan["rows"]:
        assert row["survives_covering"] == survive_k_range(row["n"], row["d"])
    print("self-test ok")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-min", type=int, default=73)
    ap.add_argument("--n-max", type=int, default=120)
    ap.add_argument("--up", action="store_true", help="run combinatorial UP on listed cubes")
    ap.add_argument("--fl", action="store_true", help="also failed-literal probing")
    ap.add_argument("--cubes", nargs="*", default=None, help="n:d:k triples")
    ap.add_argument("--json-out", type=Path, default=None)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        self_test()
        return 0

    covering = scan_covering(args.n_min, args.n_max)
    rec = {"covering": covering, "forcing": []}

    cubes = []
    if args.cubes:
        for tok in args.cubes:
            n, d, k = (int(x) for x in tok.split(":"))
            cubes.append((n, d, k))
    elif args.up or args.fl:
        # Default: every leftover k=d cube in range, plus the covering
        # boundary and the tight cube at n_min.
        for n in range(args.n_min, args.n_max + 1):
            d = ceil_div(n, 3)
            info = cube_range(n, d)
            cubes.append((n, d, info["k_min_pigeonhole"]))
        n0 = args.n_min
        d0 = ceil_div(n0, 3)
        info0 = cube_range(n0, d0)
        cubes.append((n0, d0, info0["k_max_count"]))
        # covering boundary if it exists
        for k in info0["needed_cubes"]:
            if covering_obstruction(n0, d0, k)["reason"] == "survives-covering":
                continue
            cubes.append((n0, d0, k))
            break

    seen = set()
    for n, d, k in cubes:
        if (n, d, k) in seen:
            continue
        seen.add((n, d, k))
        cov = covering_obstruction(n, d, k)
        row = {"covering": cov}
        if args.up or args.fl:
            row["up"] = run_up(n, d, k)
        if args.fl:
            row["fl"] = run_up_failed_literals(n, d, k)
        rec["forcing"].append(row)
        cov_s = cov["reason"]
        up_s = row.get("up", {}).get("up_unsat")
        fl_s = row.get("fl", {}).get("fl_unsat")
        print(
            f"n={n} d={d} k={k} covering={cov_s} up_unsat={up_s} fl_unsat={fl_s}",
            flush=True,
        )

    print(
        f"covering n={args.n_min}..{args.n_max}: "
        f"all_killed={covering['all_killed']} "
        f"n_with_survivors={covering['n_with_survivors'][:12]}"
        + ("..." if len(covering["n_with_survivors"]) > 12 else ""),
        flush=True,
    )
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(rec, indent=2))
        print("wrote", args.json_out)

    # Exit 0 even when survivors exist: this is an analysis tool, not a bound.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
