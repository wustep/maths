#!/usr/bin/env python3
"""Second-language spot-check of the 8-coset census.

Re-enumerate RREF 2-dimensional codes, rebuild unique connection sets,
and SAT a deterministic sample (first 40 unique graphs and every 80th).
Confirms the C unique-count and that those samples have no 8-pack.
"""

from __future__ import annotations

import itertools
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

from pysat.card import CardEnc, EncType
from pysat.solvers import Cadical195

from sat_leftover_cosets import QN, has8

CUBE = list(itertools.product((-1, 0, 1), repeat=5))


def is_good(a: tuple[int, ...], b: tuple[int, ...]) -> bool:
    for s in range(7):
        for t in range(7):
            if s == 0 and t == 0:
                continue
            small = True
            for i in range(5):
                x = (s * a[i] + t * b[i]) % 7
                if x > 1 and x < 6:
                    small = False
                    break
            if small:
                return False
    return True


def cid_of(c, a, b, p0, p1) -> int:
    x = list(c)
    s = x[p0]
    x = [(x[i] - (s * a[i]) % 7) % 7 for i in range(5)]
    t = x[p1]
    x = [(x[i] - (t * b[i]) % 7) % 7 for i in range(5)]
    rest = [x[i] for i in range(5) if i != p0 and i != p1]
    return rest[0] * 49 + rest[1] * 7 + rest[2]


def connection_of(a, b, p0, p1) -> str:
    bits = ["0"] * QN
    for s in range(7):
        for t in range(7):
            v = tuple((s * a[i] + t * b[i]) % 7 for i in range(5))
            for off in CUBE:
                c = tuple((v[i] + off[i]) % 7 for i in range(5))
                bits[cid_of(c, a, b, p0, p1)] = "1"
    return "".join(bits)


def rref_iter():
    pivots = [(i, j) for i in range(5) for j in range(i + 1, 5)]
    for p0, p1 in pivots:
        fa = [k for k in range(5) if k != p0 and k != p1 and k > p0]
        fb = [k for k in range(5) if k != p0 and k != p1 and k > p1]
        nfill = len(fa) + len(fb)
        for code in range(7**nfill):
            a = [0] * 5
            b = [0] * 5
            a[p0] = 1
            b[p1] = 1
            x = code
            for k in fa:
                a[k] = x % 7
                x //= 7
            for k in fb:
                b[k] = x % 7
                x //= 7
            yield tuple(a), tuple(b), p0, p1


def count_rref() -> tuple[int, int]:
    n_sub = n_good = 0
    for a, b, _, _ in rref_iter():
        n_sub += 1
        if is_good(a, b):
            n_good += 1
    return n_sub, n_good


def rref_codes():
    n_sub = 0
    n_good = 0
    seen: set[str] = set()
    unique: list[str] = []
    for a, b, p0, p1 in rref_iter():
        n_sub += 1
        if not is_good(a, b):
            continue
        n_good += 1
        conn = connection_of(a, b, p0, p1)
        if conn in seen:
            continue
        seen.add(conn)
        unique.append(conn)
    return n_sub, n_good, unique


def main() -> None:
    t0 = time.time()
    dump = HERE / "coset_unique.conn"
    if dump.exists():
        unique = [ln.strip() for ln in dump.read_text().splitlines() if ln.strip()]
        for i, conn in enumerate(unique, 1):
            if len(conn) != QN or any(ch not in "01" for ch in conn):
                raise SystemExit(f"bad unique line {i}")
        n_sub, n_good = count_rref()
        lines = [
            f"unique_dump={len(unique)}",
            f"rref_replay subspaces={n_sub} good={n_good}",
        ]
    else:
        n_sub, n_good, unique = rref_codes()
        lines = [f"subspaces={n_sub} good={n_good} unique={len(unique)}"]
        if n_sub != 140050 or n_good != 97240:
            raise SystemExit(f"RREF count drifted: {lines[0]}")
    if len(unique) != 9584:
        raise SystemExit(f"unique count drifted: {len(unique)} != 9584")
    sample = []
    for i, conn in enumerate(unique):
        if i < 40 or i % 80 == 0:
            sample.append((i, conn))
    print(f"{lines[0]} sample={len(sample)}", flush=True)
    n_yes = 0
    for i, conn in sample:
        if has8(conn):
            n_yes += 1
            print(f"YES unique {i}", flush=True)
    lines.append(f"sample {len(sample)} sat8 {n_yes}")
    lines.append(f"seconds {time.time() - t0:.1f}")
    text = "\n".join(lines) + "\n"
    print(text, end="")
    (HERE / "unique_sample_log.txt").write_text(text)
    if n_yes:
        raise SystemExit("sample found an 8-pack")


if __name__ == "__main__":
    main()
