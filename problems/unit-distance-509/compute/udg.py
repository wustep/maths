#!/usr/bin/env python3
"""Exact unit-distance graphs in Q(sqrt(3), sqrt(5), sqrt(11)).

Coordinates of the published Parts 509-graph and Heule 510-graph live in this
degree-8 field.  A number is stored as

    (c0 + c1√3 + c2√5 + c3√15 + c4√11 + c5√33 + c6√55 + c7√165) / den

with integer coefficients.  Bit k of the index is the factor √p_k for
p = (3, 5, 11).  All unit-distance tests are exact: an edge exists iff the
squared Euclidean distance equals 1 in this ring.

The four nested radicals in the Parts file denest:

    √((5/2)(7 + √33)) = (√15 + √55)/2
    √((5/2)(7 − √33)) = (√55 − √15)/2
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

PRIMES = (3, 5, 11)
BASIS_NAMES = (
    "1",
    "√3",
    "√5",
    "√15",
    "√11",
    "√33",
    "√55",
    "√165",
)
# index -> integer whose square-free kernel is that basis element
BASIS_INT = (1, 3, 5, 15, 11, 33, 55, 165)


def _gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return abs(a)


def _gcd_list(vals: list[int]) -> int:
    g = 0
    for v in vals:
        g = _gcd(g, v)
        if g == 1:
            return 1
    return g if g else 1


def _mul_basis(i: int, j: int) -> tuple[int, int]:
    """Return (k, m) such that e_i * e_j = m * e_k."""
    k = i ^ j
    m = 1
    shared = i & j
    bit = 0
    while shared:
        if shared & 1:
            m *= PRIMES[bit]
        shared >>= 1
        bit += 1
    return k, m


# 8x8 tables: product of basis i and j is MUL_M[i][j] * e_{MUL_K[i][j]}
MUL_K = [[0] * 8 for _ in range(8)]
MUL_M = [[0] * 8 for _ in range(8)]
for _i in range(8):
    for _j in range(8):
        k, m = _mul_basis(_i, _j)
        MUL_K[_i][_j] = k
        MUL_M[_i][_j] = m


def _factor_squarefree(n: int) -> tuple[int, int]:
    """n = square * squarefree, squarefree > 0, n may be negative? require n>0."""
    if n <= 0:
        raise ValueError(f"need positive integer, got {n}")
    square = 1
    squarefree = 1
    x = n
    p = 2
    while p * p <= x:
        if x % p == 0:
            exp = 0
            while x % p == 0:
                x //= p
                exp += 1
            if exp % 2:
                squarefree *= p
            square *= p ** (exp // 2)
        p = 3 if p == 2 else p + 2
    if x > 1:
        squarefree *= x
    return square, squarefree


@dataclass(frozen=True, slots=True)
class F:
    """Element of Q(√3, √5, √11)."""

    c: tuple[int, int, int, int, int, int, int, int]
    den: int

    def __post_init__(self) -> None:
        if self.den <= 0:
            raise ValueError("denominator must be positive")

    @staticmethod
    def from_int(n: int) -> F:
        return F((n, 0, 0, 0, 0, 0, 0, 0), 1).normal()

    @staticmethod
    def from_fraction(fr: Fraction) -> F:
        return F((fr.numerator, 0, 0, 0, 0, 0, 0, 0), fr.denominator).normal()

    @staticmethod
    def basis(idx: int, coeff: int = 1, den: int = 1) -> F:
        c = [0] * 8
        c[idx] = coeff
        return F(tuple(c), den).normal()

    def normal(self) -> F:
        den = self.den
        c = list(self.c)
        if den < 0:
            den = -den
            c = [-x for x in c]
        g = _gcd_list(c + [den])
        if g > 1:
            c = [x // g for x in c]
            den //= g
        return F(tuple(c), den)

    def is_zero(self) -> bool:
        return all(x == 0 for x in self.c)

    def __bool__(self) -> bool:
        return not self.is_zero()

    def __neg__(self) -> F:
        return F(tuple(-x for x in self.c), self.den)

    def __add__(self, other: F | int) -> F:
        if not isinstance(other, F):
            other = F.from_int(int(other))
        d1, d2 = self.den, other.den
        g = _gcd(d1, d2)
        m1, m2 = d2 // g, d1 // g
        c = tuple(self.c[i] * m1 + other.c[i] * m2 for i in range(8))
        return F(c, (d1 // g) * d2).normal()

    def __radd__(self, other: int) -> F:
        return self + other

    def __sub__(self, other: F | int) -> F:
        if not isinstance(other, F):
            other = F.from_int(int(other))
        return self + (-other)

    def __rsub__(self, other: int) -> F:
        return F.from_int(int(other)) - self

    def __mul__(self, other: F | int) -> F:
        if not isinstance(other, F):
            other = F.from_int(int(other))
        out = [0] * 8
        a, b = self.c, other.c
        for i, ai in enumerate(a):
            if ai == 0:
                continue
            for j, bj in enumerate(b):
                if bj == 0:
                    continue
                out[MUL_K[i][j]] += ai * bj * MUL_M[i][j]
        return F(tuple(out), self.den * other.den).normal()

    def __rmul__(self, other: int) -> F:
        return self * other

    def __truediv__(self, other: F | int) -> F:
        if not isinstance(other, F):
            other = F.from_int(int(other))
        return self * other.inv()

    def __rtruediv__(self, other: int) -> F:
        return F.from_int(int(other)) * self.inv()

    def conj_sign(self, bits: int) -> F:
        """Flip signs of √3, √5, √11 according to bits 0,1,2."""
        c = list(self.c)
        for i in range(8):
            sign = 1
            if (bits & 1) and (i & 1):
                sign = -sign
            if (bits & 2) and (i & 2):
                sign = -sign
            if (bits & 4) and (i & 4):
                sign = -sign
            c[i] *= sign
        return F(tuple(c), self.den)

    def norm_to_q(self) -> F:
        """Product of all 8 Galois conjugates; lands in Q."""
        acc = self
        for bits in range(1, 8):
            acc = acc * self.conj_sign(bits)
        return acc

    def inv(self) -> F:
        if self.is_zero():
            raise ZeroDivisionError("inverse of 0")
        # For a number in a Galois extension, 1/x = (prod_{σ≠id} σx) / N(x)
        rest = F.from_int(1)
        for bits in range(1, 8):
            rest = rest * self.conj_sign(bits)
        nrm = self * rest
        if any(nrm.c[i] != 0 for i in range(1, 8)):
            raise RuntimeError(f"norm not rational: {nrm}")
        if nrm.c[0] == 0:
            raise ZeroDivisionError("zero norm")
        # rest / (nrm.c[0]/nrm.den) = rest * nrm.den / nrm.c[0]
        num = nrm.c[0]
        den = nrm.den
        out = [rest.c[i] * den for i in range(8)]
        # divide by num; may be negative
        if num < 0:
            out = [-x for x in out]
            num = -num
        return F(tuple(out), rest.den * num).normal()

    def to_float(self) -> float:
        s3 = math.sqrt(3.0)
        s5 = math.sqrt(5.0)
        s11 = math.sqrt(11.0)
        vals = (
            1.0,
            s3,
            s5,
            s3 * s5,
            s11,
            s3 * s11,
            s5 * s11,
            s3 * s5 * s11,
        )
        return sum(self.c[i] * vals[i] for i in range(8)) / self.den

    def is_one(self) -> bool:
        return self.den == 1 and self.c == (1, 0, 0, 0, 0, 0, 0, 0)

    def support(self) -> tuple[int, ...]:
        return tuple(i for i, v in enumerate(self.c) if v)

    def in_q_sqrt33(self) -> bool:
        return all(self.c[i] == 0 for i in (1, 2, 3, 4, 6, 7))

    def has_sqrt5(self) -> bool:
        return any(self.c[i] for i in (2, 3, 6, 7))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, int):
            other = F.from_int(other)
        if not isinstance(other, F):
            return NotImplemented
        a, b = self.normal(), other.normal()
        return a.c == b.c and a.den == b.den

    def __hash__(self) -> int:
        n = self.normal()
        return hash((n.c, n.den))

    def __repr__(self) -> str:
        n = self.normal()
        parts = []
        for i, coeff in enumerate(n.c):
            if coeff == 0:
                continue
            name = BASIS_NAMES[i]
            if i == 0:
                parts.append(str(coeff))
            elif coeff == 1:
                parts.append(name)
            elif coeff == -1:
                parts.append("-" + name)
            else:
                parts.append(f"{coeff}{name}")
        if not parts:
            body = "0"
        else:
            body = parts[0]
            for p in parts[1:]:
                body += p if p.startswith("-") else "+" + p
        if n.den == 1:
            return body
        return f"({body})/{n.den}"


def sqrt_of(x: F) -> F:
    """Principal square root, when it lies in the field."""
    if x.is_zero():
        return F.from_int(0)
    if any(v < 0 for v in (x.to_float(),)) and x.support() == (0,):
        raise ValueError(f"sqrt of negative rational {x}")

    # Rational case (possibly after writing n/d = (n d)/d^2).
    if x.support() == (0,):
        num, den = x.c[0], x.den
        if num < 0:
            raise ValueError(f"sqrt of negative {x}")
        # √(num/den) = √(num den) / den
        sq, sf = _factor_squarefree(num * den)
        try:
            idx = BASIS_INT.index(sf)
        except ValueError as exc:
            raise ValueError(f"sqrt({x}) leaves square-free {sf} outside the field") from exc
        return F.basis(idx, sq, den)

    # Element of Q(√33): denest a + b√33.
    if x.in_q_sqrt33():
        a = Fraction(x.c[0], x.den)
        b = Fraction(x.c[5], x.den)
        d = 33
        disc = a * a - b * b * d
        if disc < 0:
            raise ValueError(f"cannot denest {x}: negative discriminant {disc}")
        # disc must be a square in Q
        dn, dd = disc.numerator, disc.denominator
        sqn, sfn = _factor_squarefree(abs(dn))
        sqd, sfd = _factor_squarefree(dd)
        if sfn != 1 or sfd != 1:
            raise ValueError(f"cannot denest {x}: disc {disc} not a square")
        root = Fraction(sqn, sqd)
        if dn < 0:
            raise ValueError(f"cannot denest {x}: disc {disc} not a square")
        # √(a + b√d) = √((a+root)/2) + sign(b) √((a-root)/2)
        plus = sqrt_of(F.from_fraction((a + root) / 2))
        minus = sqrt_of(F.from_fraction((a - root) / 2))
        if b >= 0:
            val = plus + minus
        else:
            val = plus - minus
        if val.to_float() < 0:
            val = -val
        return val

    raise ValueError(f"sqrt({x}) not implemented for this support {x.support()}")


# ---------------------------------------------------------------------------
# Mathematica-style parser for the published .vtx files
# ---------------------------------------------------------------------------

_NUM = re.compile(r"\d+")


class _Parser:
    def __init__(self, s: str):
        self.s = s.replace(" ", "")
        self.i = 0

    def peek(self) -> str:
        return self.s[self.i] if self.i < len(self.s) else ""

    def eof(self) -> bool:
        return self.i >= len(self.s)

    def expr(self) -> F:
        val = self.term()
        # Do not use `peek() in "+-"`: the empty string is a substring of every
        # string, so end-of-input would look like an operator.
        while self.peek() == "+" or self.peek() == "-":
            op = self.peek()
            self.i += 1
            rhs = self.term()
            val = val + rhs if op == "+" else val - rhs
        return val

    def term(self) -> F:
        val = self.unary()
        while self.peek() == "*" or self.peek() == "/":
            op = self.peek()
            self.i += 1
            rhs = self.unary()
            val = val * rhs if op == "*" else val / rhs
        return val

    def unary(self) -> F:
        if self.peek() == "+":
            self.i += 1
            return self.unary()
        if self.peek() == "-":
            self.i += 1
            return -self.unary()
        return self.primary()

    def primary(self) -> F:
        if self.s.startswith("Sqrt[", self.i):
            self.i += 5
            inner = self.expr()
            if self.peek() != "]":
                raise ValueError(f"expected ] at {self.i} in {self.s}")
            self.i += 1
            return sqrt_of(inner)
        if self.peek() == "(":
            self.i += 1
            val = self.expr()
            if self.peek() != ")":
                raise ValueError(f"expected ) at {self.i} in {self.s}")
            self.i += 1
            return val
        m = _NUM.match(self.s, self.i)
        if not m:
            raise ValueError(f"expected number at {self.i} in {self.s}")
        self.i = m.end()
        return F.from_int(int(m.group()))


def parse_mma_expr(s: str) -> F:
    p = _Parser(s)
    val = p.expr()
    if not p.eof():
        raise ValueError(f"trailing junk {p.s[p.i:]!r} in {s!r}")
    return val


def split_top_comma(s: str) -> tuple[str, str]:
    depth = 0
    for i, ch in enumerate(s):
        if ch in "[(":
            depth += 1
        elif ch in "])":
            depth -= 1
        elif ch == "," and depth == 0:
            return s[:i], s[i + 1 :]
    raise ValueError(f"no top-level comma in {s!r}")


def parse_vtx_line(line: str) -> tuple[F, F]:
    s = line.strip()
    if not (s.startswith("{") and s.endswith("}")):
        raise ValueError(f"not a {{x, y}} line: {line!r}")
    left, right = split_top_comma(s[1:-1])
    return parse_mma_expr(left), parse_mma_expr(right)


def load_vtx(path: Path | str) -> list[tuple[F, F]]:
    path = Path(path)
    pts: list[tuple[F, F]] = []
    seen: set[tuple[F, F]] = set()
    for lineno, raw in enumerate(path.read_text().splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        pt = parse_vtx_line(line)
        if pt in seen:
            raise ValueError(f"duplicate vertex at line {lineno}: {line}")
        seen.add(pt)
        pts.append(pt)
    return pts


def sqdist(p: tuple[F, F], q: tuple[F, F]) -> F:
    dx = p[0] - q[0]
    dy = p[1] - q[1]
    return dx * dx + dy * dy


def unit_edges(pts: list[tuple[F, F]]) -> list[tuple[int, int]]:
    one = F.from_int(1)
    edges: list[tuple[int, int]] = []
    n = len(pts)
    for i in range(n):
        pi = pts[i]
        for j in range(i + 1, n):
            if sqdist(pi, pts[j]) == one:
                edges.append((i, j))
    return edges


def degrees(n: int, edges: list[tuple[int, int]]) -> list[int]:
    deg = [0] * n
    for a, b in edges:
        deg[a] += 1
        deg[b] += 1
    return deg


def classify_parts(pts: list[tuple[F, F]]) -> dict[str, list[int]]:
    """Split into no-√5 (large / unrotated) and has-√5 (rotated small)."""
    large = []
    small = []
    for i, (x, y) in enumerate(pts):
        if x.has_sqrt5() or y.has_sqrt5():
            small.append(i)
        else:
            large.append(i)
    return {"large": large, "small_rotated": small}


# ---------------------------------------------------------------------------
# 4-color SAT
# ---------------------------------------------------------------------------

NCOLORS = 4


def color_var(v: int, c: int, ncolors: int = NCOLORS) -> int:
    """1-based DIMACS variable: vertex v, color c in 0..ncolors-1."""
    return v * ncolors + c + 1


def coloring_cnf(
    n: int,
    edges: list[tuple[int, int]],
    ncolors: int = NCOLORS,
    skip: set[int] | None = None,
    triangle: tuple[int, int, int] | None = None,
    vertex_selectors: bool = False,
) -> tuple[int, list[list[int]], dict[str, int]]:
    """Build a k-coloring CNF.

    If vertex_selectors is True, each vertex v gets a selector s_v (true means
    the vertex is present).  Vertex clauses become (~s_v OR colors).  Edge
    clauses stay hard.  The selector variables are n*ncolors + 1 .. n*ncolors+n.

    Returns (nvars, clauses, meta).
    """
    skip = skip or set()
    clauses: list[list[int]] = []
    # vertex: at least one color
    for v in range(n):
        if v in skip:
            continue
        clauses.append([color_var(v, c, ncolors) for c in range(ncolors)])
    # edges: different colors
    for a, b in edges:
        if a in skip or b in skip:
            continue
        for c in range(ncolors):
            clauses.append([-color_var(a, c, ncolors), -color_var(b, c, ncolors)])
    nvars = n * ncolors
    sel_base = 0
    if vertex_selectors:
        sel_base = nvars
        # rewrite vertex clauses: (~s_v OR colors)
        # We rebuild more cleanly:
        clauses = []
        for v in range(n):
            if v in skip:
                continue
            sel = sel_base + v + 1
            clauses.append([-sel] + [color_var(v, c, ncolors) for c in range(ncolors)])
        for a, b in edges:
            if a in skip or b in skip:
                continue
            for c in range(ncolors):
                clauses.append([-color_var(a, c, ncolors), -color_var(b, c, ncolors)])
        nvars = sel_base + n
    if triangle is not None:
        i, j, k = triangle
        if i not in skip and j not in skip and k not in skip:
            # fix colors 0,1,2 on the triangle
            clauses.append([color_var(i, 0, ncolors)])
            clauses.append([color_var(j, 1, ncolors)])
            clauses.append([color_var(k, 2, ncolors)])
    meta = {"n": n, "ncolors": ncolors, "sel_base": sel_base, "nvars": nvars}
    return nvars, clauses, meta


def find_triangle(n: int, edges: list[tuple[int, int]]) -> tuple[int, int, int] | None:
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    # Prefer a triangle containing vertex 0 (the origin in both published files).
    order = list(range(n))
    if 0 in range(n):
        order = [0] + list(range(1, n))
    for i in order:
        nbrs = sorted(adj[i])
        for ia, a in enumerate(nbrs):
            for b in nbrs[ia + 1 :]:
                if b in adj[a]:
                    return (i, a, b)
    return None


def write_dimacs(path: Path | str, nvars: int, clauses: list[list[int]], comments: list[str] | None = None) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="ascii") as fh:
        if comments:
            for c in comments:
                fh.write(f"c {c}\n")
        fh.write(f"p cnf {nvars} {len(clauses)}\n")
        for cl in clauses:
            fh.write(" ".join(str(x) for x in cl) + " 0\n")


def f_to_mma(x: F) -> str:
    """Write a field element as a Mathematica expression the parser accepts."""
    n = x.normal()
    names = (
        None,
        "Sqrt[3]",
        "Sqrt[5]",
        "Sqrt[15]",
        "Sqrt[11]",
        "Sqrt[33]",
        "Sqrt[55]",
        "Sqrt[165]",
    )
    terms: list[str] = []
    for i, coeff in enumerate(n.c):
        if coeff == 0:
            continue
        if i == 0:
            terms.append(str(coeff))
            continue
        name = names[i]
        if coeff == 1:
            piece = name
        elif coeff == -1:
            piece = "-" + name
        else:
            piece = f"{coeff}*{name}"
        terms.append(piece)
    if not terms:
        body = "0"
    else:
        body = terms[0]
        for t in terms[1:]:
            body += t if t.startswith("-") else "+" + t
    if n.den == 1:
        return body
    if len(terms) <= 1 and not body.startswith("-"):
        return f"{body}/{n.den}"
    return f"({body})/{n.den}"


def write_vtx(path: Path | str, pts: list[tuple[F, F]]) -> None:
    path = Path(path)
    lines = [f"{{{f_to_mma(x)}, {f_to_mma(y)}}}" for x, y in pts]
    path.write_text("\n".join(lines) + "\n")


def write_edge_list(path: Path | str, n: int, edges: list[tuple[int, int]]) -> None:
    path = Path(path)
    with path.open("w", encoding="ascii") as fh:
        fh.write(f"p edge {n} {len(edges)}\n")
        for a, b in edges:
            fh.write(f"e {a + 1} {b + 1}\n")
