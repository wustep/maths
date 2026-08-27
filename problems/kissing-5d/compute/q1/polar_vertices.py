#!/usr/bin/env python3
"""Exact vertices of the polar of each known 40-point kissing code.

For a code C ⊂ R^5 of squared-norm 2, a new equal-norm point x satisfies
<x, p> ≤ 1 for every p in C if and only if x lies in the polar

    P(C) = { x ∈ R^5 : <x, p> ≤ 1 for all p ∈ C }.

P(C) is a polytope containing the origin.  The maximum of |x|^2 on a
polytope is attained at a vertex.  A vertex is the unique solution of
five tight equalities <x, p_i> = 1 whose normals are linearly
independent, provided the remaining inequalities hold.

All four published codes have coordinates in Q, so every vertex is
rational and |x|^2 is an exact rational.  If that maximum is strictly
less than 2, C admits no 41st kissing point.

The recession cone is { r : <r, p> ≤ 0 for all p }.  Extreme rays are
kernels of four independent tight equalities through the origin.  No
nonzero feasible ray means P(C) is bounded.

Sanity check: for D5 the constraints are |x_i| + |x_j| ≤ 1, whose
maximum of |x|^2 is 5/4 at the signed equal-coordinate points.
"""

from __future__ import annotations

import json
import sys
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from configs import CONFIGS, _dot

SCALE = 10  # all published coords have denominator 1, 2, or 5


def as_int_rows(pts):
    rows = []
    for p in pts:
        row = []
        for c in p:
            v = c * SCALE
            if v.denominator != 1:
                raise ValueError(f"scale {SCALE} does not clear {c}")
            row.append(int(v))
        rows.append(tuple(row))
    return rows


def _det3(a, b, c, d, e, f, g, h, i):
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def _det4(M):
    a00, a01, a02, a03 = M[0]
    a10, a11, a12, a13 = M[1]
    a20, a21, a22, a23 = M[2]
    a30, a31, a32, a33 = M[3]
    return (
        a00 * _det3(a11, a12, a13, a21, a22, a23, a31, a32, a33)
        - a01 * _det3(a10, a12, a13, a20, a22, a23, a30, a32, a33)
        + a02 * _det3(a10, a11, a13, a20, a21, a23, a30, a31, a33)
        - a03 * _det3(a10, a11, a12, a20, a21, a22, a30, a31, a32)
    )


def det5(A):
    """Exact determinant of a 5×5 integer matrix by cofactor expansion."""
    total = 0
    sign = 1
    for j in range(5):
        minor = tuple(tuple(A[i][k] for k in range(5) if k != j) for i in range(1, 5))
        total += sign * A[0][j] * _det4(minor)
        sign = -sign
    return total


def cramer_column(A, col, rhs):
    B = [list(row) for row in A]
    for i in range(5):
        B[i][col] = rhs[i]
    return det5(B)


def kernel4(rows4):
    """Signed 4×4 minors of a 4×5 integer matrix (Plücker / 5D cross product)."""
    r = [0] * 5
    for j in range(5):
        minor = tuple(tuple(row[k] for k in range(5) if k != j) for row in rows4)
        sign = 1 if (j % 2 == 0) else -1
        r[j] = sign * _det4(minor)
    return tuple(r)


def enumerate_polar(name, pts):
    rows = as_int_rows(pts)
    n = len(rows)
    rhs = (SCALE,) * 5  # <x, p> = 1  ⇔  <x, SCALE p> wait: p_int = SCALE q, <x,q>=1 ⇔ <x,p_int>=SCALE
    # x = z / d with z_j = det(A with col j = rhs), d = det(A), A rows = p_int.
    n_combos = 0
    n_indep = 0
    n_vert = 0
    max_num = None  # |x|^2 = num/den in lowest terms, stored as (num, den)
    max_x = None
    max_support = None
    # Track a few vertices for the certificate.
    sample_vertices = []

    for idxs in combinations(range(n), 5):
        n_combos += 1
        A = [rows[i] for i in idxs]
        d = det5(A)
        if d == 0:
            continue
        n_indep += 1
        z = [cramer_column(A, j, rhs) for j in range(5)]
        # feasibility: <x, q> ≤ 1  ⇔  <z, p_int> ≤ d * SCALE   (d>0)
        # <x,q> = <z/d, p_int/SCALE> = <z,p_int>/(d SCALE)
        ok = True
        for p in rows:
            ip = z[0] * p[0] + z[1] * p[1] + z[2] * p[2] + z[3] * p[3] + z[4] * p[4]
            if d > 0:
                if ip > d * SCALE:
                    ok = False
                    break
            else:
                if ip < d * SCALE:
                    ok = False
                    break
        if not ok:
            continue
        n_vert += 1
        # |x|^2 = |z|^2 / d^2
        z2 = z[0] * z[0] + z[1] * z[1] + z[2] * z[2] + z[3] * z[3] + z[4] * z[4]
        den = d * d
        if max_num is None or z2 * max_num[1] > max_num[0] * den:
            max_num = (z2, den)
            max_x = (z, d)
            max_support = idxs
            sample_vertices.append({
                "support": list(idxs),
                "z": z,
                "d": d,
                "norm2_num": z2,
                "norm2_den": den,
            })

    # Recession cone extreme rays.
    unbounded = False
    ray = None
    for idxs in combinations(range(n), 4):
        r = kernel4([rows[i] for i in idxs])
        if all(t == 0 for t in r):
            continue
        for sign in (1, -1):
            rr = tuple(sign * t for t in r)
            good = True
            for p in rows:
                if (rr[0] * p[0] + rr[1] * p[1] + rr[2] * p[2]
                        + rr[3] * p[3] + rr[4] * p[4]) > 0:
                    good = False
                    break
            if good:
                unbounded = True
                ray = rr
                break
        if unbounded:
            break

    def lowest(num, den):
        a, b = abs(num), abs(den)
        while b:
            a, b = b, a % b
        g = a or 1
        sn = 1 if (num >= 0) == (den >= 0) else -1
        return sn * abs(num) // g, abs(den) // g

    if max_num is None:
        norm2 = None
        lt2 = False
    else:
        n2n, n2d = lowest(max_num[0], max_num[1])
        norm2 = f"{n2n}/{n2d}" if n2d != 1 else str(n2n)
        lt2 = n2n * 1 < 2 * n2d

    report = {
        "name": name,
        "n_points": n,
        "scale": SCALE,
        "n_5subsets": n_combos,
        "n_independent": n_indep,
        "n_vertices": n_vert,
        "bounded": not unbounded,
        "recession_ray": list(ray) if ray else None,
        "max_norm2": norm2,
        "max_norm2_lt_2": bool(lt2 and not unbounded),
        "maximal_as_spherical_code": bool(lt2 and not unbounded),
        "max_vertex": None if max_x is None else {
            "support": list(max_support),
            "z": list(max_x[0]),
            "d": max_x[1],
            "norm2": norm2,
        },
        "n_vertices_recorded": len(sample_vertices),
    }
    return report


def dump_points(pts, path: Path):
    rows = as_int_rows(pts)
    lines = [f"{SCALE} {len(rows)}"]
    for r in rows:
        lines.append(" ".join(str(x) for x in r))
    path.write_text("\n".join(lines) + "\n")


def compile_c(here: Path) -> Path | None:
    src = here / "polar.c"
    exe = here / "polar"
    if not src.exists():
        return None
    import os
    import subprocess
    need = (not exe.exists()) or (exe.stat().st_mtime < src.stat().st_mtime)
    if need:
        r = subprocess.run(
            ["gcc", "-O3", "-std=c11", str(src), "-o", str(exe)],
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            print("gcc polar.c failed:\n", r.stderr, flush=True)
            return None
    if os.access(exe, os.X_OK):
        return exe
    return None


def run_c(exe: Path, pts, name: str):
    import subprocess
    dump = exe.parent / f"points_{name}.txt"
    dump_points(pts, dump)
    r = subprocess.run([str(exe)], input=dump.read_text(), text=True,
                       capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"polar.exe failed: {r.stderr}")
    rec = json.loads(r.stdout)
    rec["name"] = name
    rec["engine"] = "polar.c"
    return rec


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    force_python = "--python" in sys.argv[1:]
    names = args or list(CONFIGS.keys())
    out_dir = Path(__file__).resolve().parent
    exe = None if force_python else compile_c(out_dir)
    reports = {}
    ok = True
    for name in names:
        print(f"enumerating polar vertices of {name} ...", flush=True)
        if exe is not None:
            rec = run_c(exe, CONFIGS[name](), name)
        else:
            rec = enumerate_polar(name, CONFIGS[name]())
            rec["engine"] = "python"
        reports[name] = rec
        print(
            f"  {name}: vertices={rec['n_vertices']} "
            f"independent={rec['n_independent']} "
            f"max|x|^2={rec['max_norm2']} "
            f"bounded={rec['bounded']} "
            f"maximal={rec['maximal_as_spherical_code']} "
            f"engine={rec.get('engine')}",
            flush=True,
        )
        if name == "D5":
            if rec["max_norm2"] != "5/4" or not rec["maximal_as_spherical_code"]:
                print("  FAIL: D5 sanity (expected max 5/4, maximal)")
                ok = False
        (out_dir / f"polar_{name}.json").write_text(json.dumps(rec, indent=2) + "\n")

    out = out_dir / "polar_vertices.json"
    out.write_text(json.dumps(reports, indent=2) + "\n")
    print("wrote", out)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
