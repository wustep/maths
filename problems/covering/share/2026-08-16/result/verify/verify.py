#!/usr/bin/env python3
"""Verifier #1 for the covering-code artifact.  Python 3, standard library only.

Certifies that the columns of a binary r x n parity-check matrix, read from a
plain text file, form a set S with {0} u S u (S+S) = F_2^r -- i.e. that the
code has covering radius at most 2 -- and reports the associated invariants.

COLUMN ENCODING.  Every .txt matrix in this artifact is LSB-first: a column is
the unsigned integer whose bit i (i = 0 is the least significant bit) is row
i+1 of H.  The first identity column is the integer 1; the tenth is 512.

This differs from the hexadecimal listing in arXiv:2511.02542 Theorem 4.3,
which is MSB-first with row 1 as the most significant of the r bits.  The
Kaikkonen-Rosendahl baseline is therefore built by reversing those r bits; see
build_propagation.py.  Getting this backwards makes the KR matrix and only the
KR matrix fail, which is a useful diagnostic: if just KR fails, suspect bit
order, not mathematics.

Nothing here consults a stored certificate.  Coverage is established by
enumerating all C(n,2) unordered pairs and all 2^r syndromes.  No sampling, no
early exit.

Verifier #2 (verify.rs) is an independent reimplementation that decides
coverage in the opposite direction -- syndrome-driven rather than pair-driven.
run_all.sh diffs the two fact dumps.
"""

import argparse
import json
import sys
from fractions import Fraction
from itertools import combinations


# --------------------------------------------------------------------------
# parsing
# --------------------------------------------------------------------------

def parse_matrix(path):
    """Read an r x n 0/1 matrix, return (r, n, columns) with LSB-first columns.

    Comment lines start with '#'.  Blank lines are ignored.  Every data row
    must have the same number of tokens and every token must be 0 or 1.
    """
    rows = []
    with open(path, "r", encoding="utf-8") as handle:
        for lineno, raw in enumerate(handle, 1):
            line = raw.split("#", 1)[0].strip()
            if not line:
                continue
            tokens = line.split()
            for tok in tokens:
                if tok not in ("0", "1"):
                    raise ValueError(
                        "%s:%d: token %r is not 0 or 1" % (path, lineno, tok))
            rows.append([int(tok) for tok in tokens])

    if not rows:
        raise ValueError("%s: no data rows" % path)
    width = len(rows[0])
    for idx, row in enumerate(rows):
        if len(row) != width:
            raise ValueError(
                "%s: row %d has %d entries, row 1 has %d"
                % (path, idx + 1, len(row), width))

    r = len(rows)
    n = width
    columns = [0] * n
    for i in range(r):
        row = rows[i]
        bit = 1 << i
        for j in range(n):
            if row[j]:
                columns[j] |= bit
    return r, n, columns


# --------------------------------------------------------------------------
# linear algebra over F_2
# --------------------------------------------------------------------------

def f2_rank(columns):
    """Rank over F_2 of the column set, reducing by LOWEST set bit.

    (Verifier #2 pivots on the highest set bit instead; same answer, different
    elimination order.)
    """
    pivots = {}
    rank = 0
    for col in columns:
        cur = col
        while cur:
            low = cur & -cur
            if low not in pivots:
                pivots[low] = cur
                rank += 1
                break
            cur ^= pivots[low]
    return rank


# --------------------------------------------------------------------------
# exact decimal for a dyadic rational
# --------------------------------------------------------------------------

def dyadic_decimal(num, den):
    """Exact finite decimal expansion of num/den where den is a power of two."""
    if den & (den - 1) != 0:
        raise ValueError("denominator %d is not a power of two" % den)
    k = den.bit_length() - 1
    if k == 0:
        return str(num)
    scaled = num * (5 ** k)
    text = str(scaled).rjust(k + 1, "0")
    integer_part, frac_part = text[:-k], text[-k:]
    frac_part = frac_part.rstrip("0")
    return integer_part + ("." + frac_part if frac_part else "")


def histogram_string(hist):
    return ",".join("%d:%d" % (k, hist[k]) for k in sorted(hist))


# --------------------------------------------------------------------------
# the checks
# --------------------------------------------------------------------------

def analyse(name, r, n, columns, do_minimality, do_triples):
    facts = {}
    total = 1 << r

    facts["name"] = name
    facts["r"] = r
    facts["n"] = n

    # -- well-formedness ---------------------------------------------------
    if any(c == 0 for c in columns):
        raise AssertionError("%s: a column is zero" % name)
    if any(c >= total for c in columns):
        raise AssertionError("%s: a column exceeds %d bits" % (name, r))
    if len(set(columns)) != n:
        raise AssertionError("%s: columns are not pairwise distinct" % name)
    facts["columns_nonzero"] = 1
    facts["columns_distinct"] = 1

    # -- rank --------------------------------------------------------------
    rank = f2_rank(columns)
    if rank != r:
        raise AssertionError("%s: F_2 rank is %d, expected %d" % (name, rank, r))
    facts["rank"] = rank

    # -- exhaustive coverage, pair-driven ----------------------------------
    # mult[s] counts the representations of s as a sum of AT MOST two columns:
    # the empty sum (s = 0 only), each single column, each unordered pair.
    mult = [0] * total
    mult[0] += 1
    for col in columns:
        mult[col] += 1
    for a, b in combinations(columns, 2):
        mult[a ^ b] += 1

    uncovered = 0
    for s in range(total):
        if mult[s] == 0:
            uncovered += 1
    covered = total - uncovered
    if uncovered:
        raise AssertionError(
            "%s: %d of %d syndromes uncovered" % (name, uncovered, total))
    facts["syndromes_total"] = total
    facts["syndromes_covered"] = covered

    # sanity: the total representation count must be 1 + n + C(n,2)
    expected_total_reps = 1 + n + n * (n - 1) // 2
    if sum(mult) != expected_total_reps:
        raise AssertionError("%s: representation bookkeeping is inconsistent" % name)

    # -- radius exactly two ------------------------------------------------
    column_set = set(columns)
    needs_pair = [s for s in range(total) if s != 0 and s not in column_set]
    if not needs_pair:
        raise AssertionError("%s: covering radius is at most 1, not 2" % name)
    facts["radius_exactly_2"] = 1
    facts["pair_needed"] = len(needs_pair)

    # -- multiplicity histograms ------------------------------------------
    hist = {}
    for s in range(total):
        hist[mult[s]] = hist.get(mult[s], 0) + 1
    facts["mult_hist"] = histogram_string(hist)

    pair_hist = {}
    forced_split = 0
    for s in needs_pair:
        # s is neither 0 nor a column, so every representation of it is a pair
        count = mult[s]
        pair_hist[count] = pair_hist.get(count, 0) + 1
        if count == 1:
            forced_split += 1
    facts["pair_hist"] = histogram_string(pair_hist)
    facts["forced_split"] = forced_split

    # -- density -----------------------------------------------------------
    density = Fraction(expected_total_reps, total)
    facts["density_num"] = density.numerator
    facts["density_den"] = density.denominator
    facts["density_decimal"] = dyadic_decimal(density.numerator, density.denominator)

    # -- minimum distance and dependent triples ----------------------------
    triples = []
    if do_triples:
        index_of = {c: i for i, c in enumerate(columns)}
        for i in range(n):
            for j in range(i + 1, n):
                s = columns[i] ^ columns[j]
                k = index_of.get(s)
                if k is not None and k > j:
                    # canonical form: ascending by column value, so that the
                    # listing does not depend on the order columns appear in
                    triples.append(tuple(sorted(
                        (columns[i], columns[j], columns[k]))))
        triples.sort()
        facts["min_distance"] = 3 if triples else 4
        facts["dependent_triples"] = len(triples)
        facts["triples_list"] = ";".join(
            "(%d,%d,%d)" % t for t in triples)

    # -- minimality (locally optimal / minimal saturating set) -------------
    if do_minimality:
        # Deleting column k removes exactly one representation from each of the
        # n syndromes {h_k} u {h_k ^ h_j : j != k}, and these n values are
        # pairwise distinct (columns are distinct and nonzero).  So the number
        # of syndromes left uncovered is the number of those with mult == 1.
        best = None
        best_cols = []
        for k in range(n):
            hk = columns[k]
            left = 1 if mult[hk] == 1 else 0
            for j in range(n):
                if j == k:
                    continue
                if mult[hk ^ columns[j]] == 1:
                    left += 1
            if best is None or left < best:
                best = left
                best_cols = [hk]
            elif left == best:
                best_cols.append(hk)
        facts["min_uncovered_on_deletion"] = best
        facts["argmin_deletion_columns"] = ",".join(str(c) for c in sorted(best_cols))

    return facts, mult, column_set, triples


# --------------------------------------------------------------------------
# partition checker
# --------------------------------------------------------------------------

def check_partition(name, r, n, columns, partition_path, facts, triples):
    """Confirm a (2,0)-partition in the sense of arXiv:2511.02542 Def. 3.2.

    Every column of F_2^r, including zero, must be a sum of at most 2 columns
    of H belonging to DISTINCT subsets.  Zero is the empty sum and a column of
    H is a sum of one column, so both are satisfied by definition; the content
    of the check is the remaining syndromes.
    """
    with open(partition_path, "r", encoding="utf-8") as handle:
        blob = json.load(handle)

    json_columns = blob["columns"]
    block_of = blob["block_of_column"]
    if len(json_columns) != n or len(block_of) != n:
        raise AssertionError("%s: partition JSON length does not match matrix" % name)
    # The block assignment is the only thing taken from JSON.  The columns
    # themselves are re-derived from the matrix text and cross-checked here.
    if list(json_columns) != list(columns):
        raise AssertionError(
            "%s: partition JSON columns disagree with the matrix text" % name)

    blocks = sorted(set(block_of))
    if blocks != list(range(len(blocks))):
        raise AssertionError("%s: block labels are not 0..p-1" % name)
    p = len(blocks)
    for b in blocks:
        if block_of.count(b) == 0:
            raise AssertionError("%s: block %d is empty" % (name, b))

    total = 1 << r
    column_set = set(columns)
    failures = []
    for s in range(total):
        if s == 0 or s in column_set:
            continue
        ok = False
        for i in range(n):
            j_val = s ^ columns[i]
            # find the partner; linear scan keeps this independent of any
            # precomputed structure
            for j in range(i + 1, n):
                if columns[j] == j_val and block_of[i] != block_of[j]:
                    ok = True
                    break
            if ok:
                break
        if not ok:
            failures.append(s)

    facts["partition_blocks"] = p
    facts["partition_sizes"] = ",".join(
        str(block_of.count(b)) for b in blocks)

    # Analogue of arXiv:2511.02542 Theorem 5.2(ii): the paper needs a linearly
    # dependent triple whose three columns lie in three DISTINCT subsets of the
    # partition, because that is what lets Construction QM_5^2 (Thm 5.4(ii))
    # run at the next step.  Report which triples have that property.
    if triples:
        index_of = {c: i for i, c in enumerate(columns)}
        spans = []
        three = 0
        for t in triples:
            bs = tuple(block_of[index_of[c]] for c in t)
            if len(set(bs)) == 3:
                three += 1
            spans.append("(%d,%d,%d):%d/%d/%d" % (t + bs))
        facts["triples_three_blocks"] = three
        facts["triples_block_map"] = ";".join(spans)
    facts["partition_valid"] = 1 if not failures else 0
    facts["partition_failures"] = len(failures)
    if failures:
        raise AssertionError(
            "%s: %d syndromes have no cross-block pair, first is %d"
            % (name, len(failures), failures[0]))
    return facts


# --------------------------------------------------------------------------
# driver
# --------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("matrix", help="path to the r x n 0/1 matrix text file")
    ap.add_argument("--name", default=None, help="label used in the fact dump")
    ap.add_argument("--expect-r", type=int, default=None)
    ap.add_argument("--expect-n", type=int, default=None)
    ap.add_argument("--partition", default=None,
                    help="path to a partition JSON to check against this matrix")
    ap.add_argument("--minimality", action="store_true",
                    help="run the single-column-deletion (LO code) check")
    ap.add_argument("--triples", action="store_true",
                    help="enumerate linearly dependent triples / minimum distance")
    ap.add_argument("--emit-flat", default=None,
                    help="write sorted key<TAB>value lines here")
    ap.add_argument("--emit-facts", default=None,
                    help="write the same facts as JSON here")
    args = ap.parse_args(argv)

    name = args.name or args.matrix.rsplit("/", 1)[-1].rsplit(".", 1)[0]
    r, n, columns = parse_matrix(args.matrix)

    if args.expect_r is not None and r != args.expect_r:
        raise AssertionError("%s: got r = %d, expected %d" % (name, r, args.expect_r))
    if args.expect_n is not None and n != args.expect_n:
        raise AssertionError("%s: got n = %d, expected %d" % (name, n, args.expect_n))

    facts, _mult, _cols, triples = analyse(
        name, r, n, columns, args.minimality, args.triples)

    if args.partition:
        check_partition(name, r, n, columns, args.partition, facts, triples)

    lines = ["%s\t%s" % (k, facts[k]) for k in sorted(facts)]
    for line in lines:
        sys.stdout.write(line + "\n")

    if args.emit_flat:
        with open(args.emit_flat, "w", encoding="utf-8") as handle:
            handle.write("\n".join(lines) + "\n")
    if args.emit_facts:
        with open(args.emit_facts, "w", encoding="utf-8") as handle:
            json.dump(facts, handle, indent=1, sort_keys=True)
            handle.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
