#!/usr/bin/env python3
"""Construct the propagated matrices from the r = 10, n = 50 seed.

Implements Construction QM_2^2 of

    A. A. Davydov, S. Marcugini, F. Pambianco,
    "New upper bounds for binary linear covering codes", arXiv:2511.02542,
    Theorem 4.1, equations (4.2) and (4.4),

directly from the paper's statement.  Also reconstructs the Kaikkonen-Rosendahl
[51,41]_2 2 baseline from the hexadecimal listing in Theorem 4.3, and emits the
reachable-codimension family table.

No RNG anywhere.  Every choice (indicator allocation, column order) is made by
a deterministic rule, so repeated runs are byte-identical.

----------------------------------------------------------------------------
Construction QM_2^2, verbatim from the paper
----------------------------------------------------------------------------

Basic Construction QM (Section 3.2).  Start from an [n_0, n_0 - r_0]_2 R code
with parity check matrix H_0 = [h_1 ... h_n0], h_j in F_2^{r_0}, admitting an
(R, l_0)-partition P_0 into p(H_0, l_0) subsets.  Associate with every column
h_j an indicator beta_j in F_{2^m} u {*} so that beta_i != beta_j whenever h_i
and h_j lie in DISTINCT subsets of P_0; within a subset the choice is free.
The indicator set is B = {beta_1, ..., beta_n0} and #B >= p(H_0, l_0) is
necessary.  Then (3.2)

    H_C = [ D  A(h_1, beta_1)  A(h_2, beta_2) ... A(h_n0, beta_n0) ],

and for R = 2 the (r_0 + 2m) x 2^m block A(h_j, beta_j) has columns

    ( h_j , xi , beta_j * xi )^tr      for all xi in F_{2^m}, including xi = 0.

Specialisation (4.2):   QM_2^2:  B = F_{2^m},  n_0 >= 2^m >= p(H_0),
                                 D = D_1(2) = [ 0_{r_0 + m} ; W_m ],
where W_m is the m x (2^m - 1) parity check matrix of the Hamming code, i.e.
the columns of D are ( 0_{r_0}, 0_m, w )^tr for w over the nonzero m-bit
vectors.

Result (4.4):           R = 2,  n = 2^m (n_0 + 1) - 1,  r = r_0 + 2m,
                        p(H_C) <= 2^{m+1} + 1.

Note that B = F_{2^m} is an equality: every element of the field must actually
be used as somebody's indicator.  Combined with "distinct subsets get distinct
indicators", the sets I_b of indicators used inside block b are pairwise
disjoint and their union is all of F_{2^m}, so

    sum_b |I_b| = 2^m   with   1 <= |I_b| <= |B_b|,

which is feasible exactly when p(H_0) <= 2^m <= n_0 -- condition (4.2) again.
The allocator below asserts this rather than assuming it.

----------------------------------------------------------------------------
Column encoding
----------------------------------------------------------------------------

LSB-first throughout: bit k of the integer is row k+1 of the matrix.  For the
propagated matrix of r = r_0 + 2m rows, rows 1..r_0 carry h_j, rows
r_0+1..r_0+m carry xi, and rows r_0+m+1..r_0+2m carry beta_j * xi.

The KR hex in Theorem 4.3 is the other way round -- row 1 is the MOST
significant of the ten bits -- so reconstructing H_KR reverses the ten bits.
The reversal is checked against the paper's own Theorem 5.2(ii), which asserts
h_5 + h_27 + h_29 = 0.
"""

import argparse
import json
import os
import sys
from fractions import Fraction


# --------------------------------------------------------------------------
# GF(2^m)
# --------------------------------------------------------------------------

MODULUS = {
    4: 0x13,   # x^4 + x + 1
    5: 0x25,   # x^5 + x^2 + 1
}


def gf_mul(a, b, m):
    """Carry-less multiply of a and b in GF(2^m), reduced by MODULUS[m]."""
    mod = MODULUS[m]
    top = 1 << m
    product = 0
    while b:
        if b & 1:
            product ^= a
        b >>= 1
        a <<= 1
        if a & top:
            a ^= mod
    return product


def gf_selftest(m):
    """Closure, commutativity, associativity, distributivity, inverses."""
    size = 1 << m
    for a in range(size):
        for b in range(size):
            ab = gf_mul(a, b, m)
            assert 0 <= ab < size, "GF(2^%d): product left the field" % m
            assert ab == gf_mul(b, a, m), "GF(2^%d): not commutative" % m
            assert gf_mul(a, 1, m) == a, "GF(2^%d): 1 is not the identity" % m
            assert gf_mul(a, 0, m) == 0, "GF(2^%d): 0 does not annihilate" % m
    for a in range(size):
        for b in range(size):
            for c in range(size):
                left = gf_mul(gf_mul(a, b, m), c, m)
                right = gf_mul(a, gf_mul(b, c, m), m)
                assert left == right, "GF(2^%d): not associative" % m
                dist = gf_mul(a, b ^ c, m)
                assert dist == gf_mul(a, b, m) ^ gf_mul(a, c, m), \
                    "GF(2^%d): not distributive" % m
    for a in range(1, size):
        inverses = [b for b in range(1, size) if gf_mul(a, b, m) == 1]
        assert len(inverses) == 1, \
            "GF(2^%d): element %d has %d inverses" % (m, a, len(inverses))
    return True


# --------------------------------------------------------------------------
# matrix i/o
# --------------------------------------------------------------------------

def read_matrix(path):
    rows = []
    with open(path, "r", encoding="utf-8") as handle:
        for raw in handle:
            line = raw.split("#", 1)[0].strip()
            if line:
                rows.append(line.split())
    r = len(rows)
    n = len(rows[0])
    for row in rows:
        assert len(row) == n, "%s: ragged matrix" % path
    cols = [0] * n
    for i in range(r):
        for j in range(n):
            if rows[i][j] == "1":
                cols[j] |= 1 << i
    return r, n, cols


def write_matrix(path, r, columns, header_lines):
    n = len(columns)
    out = []
    for line in header_lines:
        out.append("# " + line if line else "#")
    for i in range(r):
        bit = 1 << i
        out.append(" ".join("1" if (c & bit) else "0" for c in columns))
        # rebuild per row without mutating columns
        out[-1] = " ".join("1" if (c >> i) & 1 else "0" for c in columns)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(out) + "\n")


# --------------------------------------------------------------------------
# Kaikkonen-Rosendahl baseline (arXiv:2511.02542 Theorem 4.3)
# --------------------------------------------------------------------------

KR_HEX = (
    "1B6 193 1CC 187 1F6 F7 16E 140 3C 296 22F 303 381 365 "
    "11D 1A3 274 2F2 254 56 F 41 357 208 34 329 28D 31D 3D5 129 3D7 "
    "B7 3EC 2E2 23C AD 34E 155 2E6 371 D4"
).split()


def bit_reverse(value, width):
    out = 0
    for i in range(width):
        if (value >> i) & 1:
            out |= 1 << (width - 1 - i)
    return out


def build_kr():
    """H_KR = [I_10 | M_KR], returned in the repo's LSB-first encoding."""
    assert len(KR_HEX) == 41, "Theorem 4.3 lists 41 columns of M_KR"
    identity = [1 << i for i in range(10)]
    msb_first = [int(h, 16) for h in KR_HEX]
    for value in msb_first:
        assert 0 < value < 1024, "KR hex column %X is not a 10-bit value" % value
    tail = [bit_reverse(v, 10) for v in msb_first]
    columns = identity + tail
    assert len(columns) == 51

    # Bit-order canary, from Theorem 5.2(ii): h_5 + h_27 + h_29 = 0_10.
    # In the paper's numbering h_1..h_10 are the identity columns and h_11 is
    # the first column of M_KR, so h_27 and h_29 are M_KR columns 17 and 19.
    h5, h27, h29 = columns[4], columns[26], columns[28]
    assert h5 ^ h27 ^ h29 == 0, (
        "KR bit-order canary failed: h5 ^ h27 ^ h29 = %d, expected 0. "
        "The hex in Theorem 4.3 is MSB-first (row 1 = most significant); "
        "this artifact is LSB-first, so the ten bits must be reversed."
        % (h5 ^ h27 ^ h29))
    assert h5 == 16, "h_5 should be (00 0010 0000)^tr = 16 in LSB-first form"
    assert len(set(columns)) == 51, "KR columns are not distinct"
    return columns


# --------------------------------------------------------------------------
# indicator allocation for QM_2^2
# --------------------------------------------------------------------------

def allocate_indicators(block_of_column, m):
    """Assign beta_j in F_{2^m} to every column, per Construction QM.

    Returns (betas, indicator_sets).  Guarantees:
      * columns in distinct blocks get distinct indicators;
      * the set of indicators actually used is exactly F_{2^m} (B = F_{2^m});
      * deterministic -- blocks in index order, field elements in integer order.
    """
    size = 1 << m
    blocks = sorted(set(block_of_column))
    assert blocks == list(range(len(blocks))), "block labels must be 0..p-1"
    p = len(blocks)
    members = {b: [j for j, bb in enumerate(block_of_column) if bb == b]
               for b in blocks}
    capacities = [len(members[b]) for b in blocks]

    assert p <= size, (
        "infeasible: p(H_0) = %d > 2^m = %d, violates (4.2)" % (p, size))
    assert size <= sum(capacities), (
        "infeasible: 2^m = %d > n_0 = %d, violates (4.2)"
        % (size, sum(capacities)))

    # one indicator per block, then top up greedily in block order
    counts = [1] * p
    remaining = size - p
    for b in range(p):
        if remaining <= 0:
            break
        extra = min(capacities[b] - 1, remaining)
        counts[b] += extra
        remaining -= extra
    assert remaining == 0, "greedy allocator failed to place %d indicators" % remaining
    assert sum(counts) == size
    for b in range(p):
        assert 1 <= counts[b] <= capacities[b]

    # hand out consecutive field elements
    indicator_sets = {}
    nxt = 0
    for b in range(p):
        indicator_sets[b] = list(range(nxt, nxt + counts[b]))
        nxt += counts[b]
    assert nxt == size
    seen = set()
    for b in range(p):
        assert not (seen & set(indicator_sets[b])), "indicator sets overlap"
        seen |= set(indicator_sets[b])
    assert seen == set(range(size)), "indicators do not exhaust F_{2^m}"

    betas = [None] * len(block_of_column)
    for b in range(p):
        pool = indicator_sets[b]
        for pos, j in enumerate(members[b]):
            betas[j] = pool[pos % len(pool)]
    assert all(x is not None for x in betas)
    assert set(betas) == set(range(size)), "B is not all of F_{2^m}"
    # distinct blocks => distinct indicators
    for j, bj in enumerate(block_of_column):
        for k, bk in enumerate(block_of_column):
            if bj != bk:
                assert betas[j] != betas[k], \
                    "columns %d and %d share an indicator across blocks" % (j, k)
    return betas, indicator_sets


# --------------------------------------------------------------------------
# Construction QM_2^2
# --------------------------------------------------------------------------

def qm2_squared(r0, columns0, block_of_column, m, p_h0):
    """Apply QM_2^2 and return (r, columns) for the new code."""
    n0 = len(columns0)
    size = 1 << m

    # Condition (4.2), asserted explicitly rather than assumed.
    assert n0 >= size, "(4.2) violated: n_0 = %d < 2^m = %d" % (n0, size)
    assert size >= p_h0, "(4.2) violated: 2^m = %d < p(H_0) = %d" % (size, p_h0)

    gf_selftest(m)
    betas, _sets = allocate_indicators(block_of_column, m)

    r = r0 + 2 * m
    shift_xi = r0
    shift_bx = r0 + m

    columns = []
    # D = D_1(2): the 2^m - 1 columns (0_{r0}, 0_m, w), w over nonzero m-bit
    # vectors -- the Hamming parity check matrix W_m in the bottom m rows.
    for w in range(1, size):
        columns.append(w << shift_bx)
    # A(h_j, beta_j), j = 1..n0, in the order of (3.2)
    for j in range(n0):
        hj = columns0[j]
        bj = betas[j]
        for xi in range(size):
            columns.append(hj | (xi << shift_xi) | (gf_mul(bj, xi, m) << shift_bx))

    n = size * (n0 + 1) - 1
    assert len(columns) == n, \
        "(4.4) violated: built %d columns, expected %d" % (len(columns), n)
    assert len(set(columns)) == n, "propagated columns are not distinct"
    assert all(0 < c < (1 << r) for c in columns), "propagated column out of range"
    return r, columns, betas


# --------------------------------------------------------------------------
# family table
# --------------------------------------------------------------------------

def seed_length(t):
    """n = 51 * 2^(t-5) - 1 for r = 2t, the closed form of the new family."""
    return 51 * (1 << (t - 5)) - 1


def published_even(r):
    """Best published upper bound on l_2(r,2) for even r, from arXiv:2511.02542.

    Tables 5.1 and 5.2.  phi(r) = 27*2^(r/2-4) - 1 is (4.5); Phi(r) =
    26*2^(r/2-4) - 1 is (5.4); Phihat(r) = 26.5*2^(r/2-4) - 3 = 53*2^(r/2-5) - 3
    is (5.5).  r = 8 is 26 = phi(8) and r = 10 is 51 (Kaikkonen-Rosendahl).
    """
    t = r // 2
    if r == 8:
        return 26, "phi(8)"
    if r == 10:
        return 51, "KR 2003"
    if r in (12, 14, 16):
        return 27 * (1 << (t - 4)) - 1, "phi(%d)" % r
    if r in (22, 24, 26):
        return 53 * (1 << (t - 5)) - 3, "Phihat(%d)" % r
    return 26 * (1 << (t - 4)) - 1, "Phi(%d)" % r


def density(n, r):
    return Fraction(1 + n + n * (n - 1) // 2, 1 << r)


def reachable_family(t_max):
    """Breadth-first over QM_2^2 steps from the seed (t, p) = (5, 10).

    A state is (t, p): r = 2t, length n(t) = 51*2^(t-5) - 1, and p an upper
    bound on the size of a 2-partition of that code's parity check matrix.
    A step with parameter m is legal iff n(t) >= 2^m >= p, per (4.2), and lands
    on (t + m, 2^(m+1) + 1) by (4.4).  For each reachable t we keep the
    smallest p obtainable, since a smaller p only widens the next step.
    """
    best = {5: 10}
    frontier = [5]
    provenance = {5: ("seed", None, None)}
    while frontier:
        new_frontier = []
        for t in sorted(frontier):
            p = best[t]
            n0 = seed_length(t)
            m = 1
            while (1 << m) <= n0:
                if (1 << m) >= p and t + m <= t_max:
                    t2 = t + m
                    p2 = (1 << (m + 1)) + 1
                    if t2 not in best or p2 < best[t2]:
                        best[t2] = p2
                        provenance[t2] = ("QM_2^2", t, m)
                        if t2 not in new_frontier:
                            new_frontier.append(t2)
                m += 1
        frontier = new_frontier
    return best, provenance


def family_rows(t_max):
    best, provenance = reachable_family(t_max)
    rows = []
    for t in range(5, t_max + 1):
        r = 2 * t
        pub, pub_label = published_even(r)
        if t in best:
            n = seed_length(t)
            d = density(n, r)
            kind, t0, m = provenance[t]
            rows.append({
                "r": r,
                "reachable": 1,
                "n": n,
                "p_bound": best[t],
                "density_num": d.numerator,
                "density_den": d.denominator,
                "density": float(d),
                "published": pub,
                "published_label": pub_label,
                "improvement": pub - n,
                "from_r": (2 * t0) if t0 is not None else None,
                "m": m,
                "step": kind,
            })
        else:
            rows.append({
                "r": r,
                "reachable": 0,
                "n": None,
                "p_bound": None,
                "density_num": None,
                "density_den": None,
                "density": None,
                "published": pub,
                "published_label": pub_label,
                "improvement": None,
                "from_r": None,
                "m": None,
                "step": None,
            })
    return rows


def family_markdown(rows):
    out = []
    out.append("| r | n (this family) | p(H) bound | density | published n | published form | improvement |")
    out.append("| ---: | ---: | ---: | ---: | ---: | :--- | ---: |")
    for row in rows:
        if not row["reachable"]:
            out.append("| %d | — | — | — | %d | %s | not reachable by QM_2^2 |"
                       % (row["r"], row["published"], row["published_label"]))
            continue
        mark = "**-%d**" % row["improvement"] if row["improvement"] > 0 else "0"
        out.append("| %d | %d | %d | %.5f | %d | %s | %s |"
                   % (row["r"], row["n"], row["p_bound"], row["density"],
                      row["published"], row["published_label"], mark))
    return "\n".join(out)


# --------------------------------------------------------------------------
# driver
# --------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--seed", required=True, help="path to the r=10 seed matrix")
    ap.add_argument("--partition", required=True, help="path to partition_p10.json")
    ap.add_argument("--outdir", required=True, help="directory to write matrices into")
    ap.add_argument("--t-max", type=int, default=32,
                    help="largest t = r/2 in the family table (default 32, i.e. r<=64)")
    ap.add_argument("--emit-family", default=None,
                    help="write the family table as JSON here")
    ap.add_argument("--emit-family-md", default=None,
                    help="write the family table as markdown here")
    ap.add_argument("--emit-flat", default=None,
                    help="write sorted key<TAB>value build facts here")
    ap.add_argument("--emit-appendix", default=None,
                    help="write the LaTeX appendix listing of the seed matrix here")
    args = ap.parse_args(argv)

    facts = {}

    r0, n0, columns0 = read_matrix(args.seed)
    assert (r0, n0) == (10, 50), "seed is %d x %d, expected 10 x 50" % (r0, n0)

    with open(args.partition, "r", encoding="utf-8") as handle:
        blob = json.load(handle)
    assert list(blob["columns"]) == list(columns0), \
        "partition JSON columns disagree with the seed matrix text"
    block_of_column = list(blob["block_of_column"])
    p_h0 = len(set(block_of_column))
    assert p_h0 == blob["p_H"]
    facts["seed_r"] = r0
    facts["seed_n"] = n0
    facts["seed_p"] = p_h0

    # --- Kaikkonen-Rosendahl baseline ------------------------------------
    kr = build_kr()
    write_matrix(
        os.path.join(args.outdir, "kr_r10_n51.txt"), 10, kr,
        ["Kaikkonen-Rosendahl [51,41]_2 2 baseline (2003).",
         "Reconstructed from the hexadecimal listing of M_KR in",
         "arXiv:2511.02542 Theorem 4.3, equation (4.9), as H_KR = [I_10 | M_KR].",
         "",
         "The paper's hex is MSB-first (row 1 = most significant of the ten",
         "bits); this file, like every matrix here, is LSB-first (bit k of the",
         "integer encoding = row k+1), so the ten bits are reversed on import.",
         "The reversal is pinned by the paper's own Theorem 5.2(ii):",
         "h_5 + h_27 + h_29 = 0.",
         "",
         "10 rows, 51 columns; space separated.",
         "Generated by verify/build_propagation.py -- do not edit by hand."])
    facts["kr_n"] = len(kr)
    facts["kr_canary_h5_h27_h29"] = kr[4] ^ kr[26] ^ kr[28]

    # --- QM_2^2 at every legal m ------------------------------------------
    legal_m = [m for m in range(1, 12) if n0 >= (1 << m) >= p_h0]
    facts["legal_m"] = ",".join(str(m) for m in legal_m)
    assert legal_m == [4, 5], (
        "expected (4.2) to permit exactly m = 4, 5 for n_0 = %d, p(H_0) = %d; got %s"
        % (n0, p_h0, legal_m))

    for m in legal_m:
        r, columns, betas = qm2_squared(r0, columns0, block_of_column, m, p_h0)
        n = len(columns)
        path = os.path.join(args.outdir, "H_r%d_n%d.txt" % (r, n))
        write_matrix(
            path, r, columns,
            ["Construction QM_2^2 (arXiv:2511.02542 Theorem 4.1, eq. (4.2),",
             "(4.4)) applied to the [50,40]_2 2 seed with m = %d." % m,
             "",
             "  H_C = [ D  A(h_1,b_1) ... A(h_50,b_50) ],",
             "  A(h_j,b_j) columns = (h_j, xi, b_j*xi)^tr, xi over F_{2^%d}," % m,
             "  D = D_1(2): columns (0_10, 0_%d, w)^tr, w over nonzero %d-bit"
             % (m, m),
             "  vectors (the Hamming parity check matrix W_%d)." % m,
             "",
             "GF(2^%d) modulus 0x%X.  r = 10 + 2*%d = %d, n = 2^%d * 51 - 1 = %d."
             % (m, MODULUS[m], m, r, m, n),
             "LSB-first: bit k of the integer encoding is row k+1.",
             "Rows 1..10 carry h_j, rows 11..%d carry xi, rows %d..%d carry b_j*xi."
             % (10 + m, 11 + m, r),
             "",
             "%d rows, %d columns; space separated." % (r, n),
             "Generated by verify/build_propagation.py -- do not edit by hand."])
        facts["qm2_m%d_r" % m] = r
        facts["qm2_m%d_n" % m] = n
        facts["qm2_m%d_p_bound" % m] = (1 << (m + 1)) + 1
        facts["qm2_m%d_distinct_betas" % m] = len(set(betas))
        d = density(n, r)
        facts["qm2_m%d_density_num" % m] = d.numerator
        facts["qm2_m%d_density_den" % m] = d.denominator

    # --- family ------------------------------------------------------------
    rows = family_rows(args.t_max)
    reachable = [row for row in rows if row["reachable"]]
    facts["family_reachable_r"] = ",".join(str(row["r"]) for row in reachable)
    facts["family_unreachable_r"] = ",".join(
        str(row["r"]) for row in rows if not row["reachable"])
    facts["family_improvements"] = ",".join(
        str(row["r"]) for row in reachable if row["improvement"] > 0)
    facts["family_closed_form"] = "51*2^(r/2-5)-1"
    # verify the closed form against the recurrence at every reachable r
    for row in reachable:
        t = row["r"] // 2
        assert row["n"] == 51 * (1 << (t - 5)) - 1
    facts["asymptotic_density_num"] = 51 * 51
    facts["asymptotic_density_den"] = 1 << 11
    facts["asymptotic_density_decimal"] = "%.6f" % (51 * 51 / 2048.0)
    facts["paper_asymptotic_density_num"] = 52 * 52
    facts["paper_asymptotic_density_den"] = 1 << 11
    # sanity: the published family really is the n_0 = 51 version of ours
    for row in rows:
        if row["r"] >= 28 or row["r"] in (18, 20):
            assert row["published"] == 52 * (1 << (row["r"] // 2 - 5)) - 1 \
                or row["r"] in (22, 24, 26), \
                "published Phi(%d) does not match 52*2^(r/2-5)-1" % row["r"]

    if args.emit_appendix:
        # The appendix of note.tex is generated from the matrix, never typed,
        # so the paper listing cannot drift away from the verified object.
        body = []
        body.append("\\begin{verbatim}")
        for i in range(r0):
            body.append("".join("1" if (c >> i) & 1 else "0" for c in columns0))
        body.append("\\end{verbatim}")
        body.append("")
        body.append("\\noindent The same columns as unsigned integers, with bit $i$ (least")
        body.append("significant first) equal to row $i+1$:")
        body.append("")
        body.append("\\begin{verbatim}")
        line = []
        width = 0
        for value in columns0:
            token = str(value)
            if width and width + 1 + len(token) > 66:
                body.append(" ".join(line))
                line, width = [], 0
            line.append(token)
            width += (1 if width else 0) + len(token)
        if line:
            body.append(" ".join(line))
        body.append("\\end{verbatim}")
        with open(args.emit_appendix, "w", encoding="utf-8") as handle:
            handle.write("\n".join(body) + "\n")

    if args.emit_family:
        with open(args.emit_family, "w", encoding="utf-8") as handle:
            json.dump(rows, handle, indent=1, sort_keys=True)
            handle.write("\n")
    if args.emit_family_md:
        with open(args.emit_family_md, "w", encoding="utf-8") as handle:
            handle.write(family_markdown(rows) + "\n")

    lines = ["%s\t%s" % (k, facts[k]) for k in sorted(facts)]
    for line in lines:
        sys.stdout.write(line + "\n")
    if args.emit_flat:
        with open(args.emit_flat, "w", encoding="utf-8") as handle:
            handle.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
