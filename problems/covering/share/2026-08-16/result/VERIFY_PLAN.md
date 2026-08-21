# Verification plan

Written **before** any verifier code, per the working protocol for this
artifact. Everything below is a commitment about what the two verifiers must
do; if the implementation later disagrees with this plan, the plan is wrong and
gets amended in place with a note, not silently.

## What is being certified

A binary \(r\times n\) matrix \(H\) over \(\mathbb F_2\) is the parity-check
matrix of an \([n,n-r]_2\) code of covering radius \(\le 2\) iff its column
multiset \(S\subset\mathbb F_2^{\,r}\) satisfies

\[
\{0\}\cup S\cup(S+S)=\mathbb F_2^{\,r}.
\]

Covering radius is *exactly* 2 iff additionally some syndrome is neither \(0\)
nor a single column. The four matrices to certify:

| file | \(r\) | \(n\) | provenance |
| --- | --- | --- | --- |
| `data/H_r10_n50.txt` | 10 | 50 | the result; copied verbatim from `../compute/` |
| `data/kr_r10_n51.txt` | 10 | 51 | Kaikkonen–Rosendahl 2003 baseline, rebuilt from the hex in arXiv:2511.02542 Thm 4.3 |
| `data/H_r18_n815.txt` | 18 | 815 | QM\(_2^2\) at \(m=4\), built by `verify/build_propagation.py` |
| `data/H_r20_n1631.txt` | 20 | 1631 | QM\(_2^2\) at \(m=5\), built by `verify/build_propagation.py` |

Exhaustive means exhaustive: \(2^{20}=1{,}048{,}576\) syndromes at the top end,
enumerated, no sampling, no early exit, no consulting a stored certificate.

## Encoding convention (the one thing most likely to go wrong)

Two conventions collide here and they are reverses of each other.

- **Repo convention (LSB-first).** A column is an unsigned integer; bit \(i\)
  (counting from the least significant bit, \(i=0\)) is row \(i+1\) of \(H\).
  So the first identity column \((1,0,\dots,0)^{tr}\) is the integer `1` and the
  tenth is `512`. Used by `compute/H_r10_n50.txt`, by
  `compute/witness_r10_n50.json`, and by every `.txt` matrix in `data/`.
- **Paper convention (MSB-first).** In arXiv:2511.02542 Thm 4.3, the hex string
  for a \(10\)-row column has row 1 as the **most** significant of the ten bits:
  `1B6` \(=\) `01 1011 0110` read top-to-bottom as rows 1..10.

The reconstruction of \(H_{KR}\) must therefore **reverse the ten bits**. A
verifier that skips the reversal will report a spurious failure on the KR
baseline only — the other three matrices never touch the paper's hex — which is
a diagnostic worth stating out loud, because "only KR fails" means encoding, not
mathematics.

Independent self-test of the reversal, taken from Thm 5.2(ii): the paper asserts
\(h_5+h_{27}+h_{29}=0\) with \(h_5=(00\,0010\,0000)^{tr}\),
\(h_{27}=\)`274`, \(h_{29}=\)`254`. Under the correct reversal this must come out
as \(16 \oplus \texttt{rev}(\texttt{0x274}) \oplus \texttt{rev}(\texttt{0x254}) = 0\).
The builder asserts this. It is a bit-order canary that costs nothing.

## Verifier #1 — `verify/verify.py` (Python 3, stdlib only)

Reads a matrix `.txt`. Never reads a JSON certificate for the covering claim.

1. **Parse.** Strip `#` comments and blank lines. Require every remaining line
   to have the same number of whitespace-separated tokens, each in `{0,1}`.
   \(r\) = number of lines, \(n\) = tokens per line. Assemble column \(j\) as
   \(\sum_i \text{row}_i[j]\,2^{i}\) (LSB-first).
2. **Well-formedness.** All \(n\) columns nonzero; all \(n\) pairwise distinct;
   every column \(< 2^r\). Shape matches the expected \((r,n)\) passed on the
   command line.
3. **Rank.** \(\mathbb F_2\) Gaussian elimination on the integer columns
   (pivot = lowest set bit, XOR-reduce). Assert rank \(= r\); this is what makes
   the redundancy genuinely \(r\).
4. **Exhaustive coverage.** Allocate an integer array `mult` of length \(2^r\)
   initialised to 0. Increment `mult[0]` once for the empty sum. Increment
   `mult[h]` for each column \(h\). Increment `mult[h_i ^ h_j]` for every
   unordered pair \(i<j\) — all \(\binom n2\) of them, no shortcuts. Then assert
   `min(mult) >= 1` over the whole range. This is a full enumeration of
   \(\{0\}\cup S\cup(S+S)\) by construction, and it yields the multiplicity data
   for free.
5. **Radius exactly 2.** Assert some \(s\) has \(s\ne0\), \(s\notin S\). Since
   coverage already holds, the radius is not \(\le 1\), hence exactly 2.
6. **Reporting.** Multiplicity histogram over all \(2^r\) syndromes (counting
   the empty sum, singletons and unordered pairs as above); the *pair-only*
   histogram restricted to the syndromes that are neither \(0\) nor a column
   (these are the ones that genuinely need a pair); the count of such syndromes;
   the count with a **unique** pair representation (call these the *forced-split*
   pairs — the two columns involved must land in distinct blocks of any
   2-partition, so this number lower-bounds how constrained \(p(H)\) is); the
   covering density \(\bigl(1+n+\binom n2\bigr)/2^r\) as an exact
   `fractions.Fraction`, printed reduced, alongside its decimal expansion.
7. **Minimum distance and dependent triples.** \(d\ge3\) already follows from
   distinct-and-nonzero. Enumerate all \(\binom n3\) triples — or equivalently
   all pairs \(i<j\) with \(h_i\oplus h_j\in S\) at index \(k>j\), which is the
   same set and cheaper — and report the count. \(d=3\) iff that count is
   positive. Report the triples explicitly.
8. **Minimality (LO check).** For each of the \(n\) columns, delete it and
   recount uncovered syndromes over the full \(2^r\) range. Report the minimum
   over all deletions. If that minimum is \(\ge1\), no single column is
   redundant and the set is a *minimal* 1-saturating set in \(PG(r-1,2)\),
   equivalently a locally optimal covering code. Implemented by decrementing
   the shared `mult` array rather than recomputing from scratch, then restoring
   it — and the restore is checked by re-asserting the total.
9. **Partition checker** (separate entry point, `--partition`). Loads
   `data/partition_p10.json` for the *block assignment only*, and re-derives the
   columns from the `.txt`. Cross-checks that the JSON `columns` list equals the
   columns parsed from the matrix text as a set and in order. Then for every
   syndrome \(s\in\mathbb F_2^{\,r}\): if \(s=0\) or \(s\in S\), pass by
   definition (Def. 3.2 allows sums of 0 or 1 columns); otherwise require some
   pair \(h_i\oplus h_j=s\) with `block[i] != block[j]`. Report the number of
   blocks \(p(H)\) and which syndromes, if any, fail.

Output is a stable, sorted, machine-readable dump (`--emit-facts <path>` writes
JSON) so the shell driver can assert on it and so the prose in `NOTE.md` can be
checked against it mechanically rather than by eye.

## Verifier #2 — `verify/verify.rs` (Rust, no crates, `rustc` only)

Written after #1 exists but **deliberately not a port of it**. Sharing an
encoding convention is unavoidable — that is the specification, not an
implementation choice — but sharing an *algorithm* would make the pair
redundant. So #2 differs where it can:

- **Different coverage algorithm, opposite direction.** #1 is pair-driven: walk
  the \(\binom n2\) pairs and mark what they hit. #2 is syndrome-driven: for
  each \(s\in\{0,\dots,2^r-1\}\), decide membership by scanning columns and
  testing whether \(s\oplus h\) is in a `Vec<bool>` membership table of size
  \(2^r\). These two agree only if the mathematics is right; a transcription
  error in one does not reproduce in the other. #2 *additionally* computes the
  multiplicity histogram by its own independent pair loop, and asserts its
  syndrome-driven verdict matches its own pair-driven multiplicities before it
  ever reports a number — an internal consistency check that #1 does not have.
- **Different rank routine.** #1 reduces by lowest set bit; #2 does textbook
  column-echelon by highest set bit. Same answer, different pivot order.
- **Different parser.** #1 works row-wise then transposes; #2 accumulates
  directly into the column integers as it streams tokens.
- **Different arithmetic for the density.** #1 uses `fractions.Fraction`; #2
  reduces \(\bigl(1+n+\binom n2\bigr)/2^r\) by an explicit `u128` `gcd` and
  prints numerator/denominator, then separately prints the decimal to 12 places
  by long division rather than by float.
- Same partition check, but expressed as: build for each syndrome the set of
  block-pairs realising it, and require a non-diagonal one. #2 parses the
  partition JSON with a hand-rolled integer scanner (no serde), which is ugly
  but keeps the dependency surface at zero and means a malformed JSON is a hard
  error rather than a silent default.

**Honest limitation, stated up front.** Both verifiers were written in the same
session by the same author. "Independent" here means: two languages, two
algorithms, two parsers, two arithmetic paths, and no shared code or shared
intermediate files. It does *not* mean two people. The one shared assumption
that cannot be factored out is the LSB-first column encoding — and that
assumption is itself pinned by the \(h_5+h_{27}+h_{29}=0\) canary against the
published paper. A third party re-deriving the columns under the opposite
convention would get the bit-reverse of every column, which is an
\(\mathbb F_2\)-linear relabelling of \(\mathbb F_2^{10}\) and therefore
preserves every claim made here.

## Builder — `verify/build_propagation.py`

Implements Construction QM\(_2^2\) (arXiv:2511.02542, Thm 4.1, eq. (4.2) and
(4.4)) literally, from the paper, not from any prior script.

- Field arithmetic: \(GF(2^m)\) by carry-less multiply and reduce, modulus
  \(x^4+x+1\) (`0x13`) for \(m=4\) and \(x^5+x^2+1\) (`0x25`) for \(m=5\).
  Self-test before use: closure, commutativity, associativity of multiplication
  on all \(2^{3m}\) triples, distributivity, and existence and uniqueness of an
  inverse for every nonzero element. Cheap at \(m\le5\) and it catches a wrong
  modulus instantly.
- Condition from (4.2): assert \(n_0\ge 2^m\ge p(H_0)\) explicitly, as an
  `assert`, for each \(m\) tried; enumerate all \(m\) satisfying it rather than
  assuming \(\{4,5\}\).
- Indicators: \(\mathscr B=\mathbb F_{2^m}\) exactly. Columns in distinct blocks
  must get distinct indicators, so the indicator sets \(I_b\) are pairwise
  disjoint, and \(\mathscr B=\mathbb F_{2^m}\) forces
  \(\sum_b |I_b| = 2^m\) with \(1\le |I_b|\le |B_b|\). Feasible iff
  \(p(H_0)\le 2^m\le n_0\), which is exactly (4.2) again. Greedy allocator:
  one indicator per block first, then top up in block order to capacity.
  Deterministic; assert the resulting allocation is a partition of
  \(\mathbb F_{2^m}\).
- Columns: \(A(h_j,\beta_j)=(h_j,\xi,\beta_j\xi)^{tr}\) for all
  \(\xi\in\mathbb F_{2^m}\) **including** \(\xi=0\), giving \(2^m\) columns per
  starting column. Plus \(D=D_1(2)\): the \(2^m-1\) columns
  \((0_{r_0},0_m,w)^{tr}\), \(w\) over the nonzero \(m\)-bit vectors — i.e. the
  Hamming parity-check matrix \(W_m\) in the bottom \(m\) rows.
- Layout of the new \(r=r_0+2m\) rows, LSB-first: rows \(1..r_0\) carry \(h_j\),
  rows \(r_0+1..r_0+m\) carry \(\xi\), rows \(r_0+m+1..r_0+2m\) carry
  \(\beta_j\xi\). Assert \(n = 2^m(n_0+1)-1\) from (4.4).
- No RNG anywhere. Column order is fixed: \(D\) first, then
  \(A(h_1,\beta_1),\dots,A(h_{n_0},\beta_{n_0})\), matching (3.2).
- The resulting matrices then go through the **full** verifier, both of them.
  Nothing about QM\(_2^2\) is taken on trust from the theorem statement; the
  theorem tells us where to look and the exhaustive check is the proof of the
  instance.

## Family table

Generated, not typed. From (4.2)/(4.4): a state is \((t,p)\) with \(r=2t\) and
\(p\) an upper bound on \(p(H)\); the length is \(n(t)=51\cdot2^{t-5}-1\). A step
with parameter \(m\) is legal iff \(n(t)\ge 2^m\ge p\), and produces
\((t+m,\ 2^{m+1}+1)\) with \(n(t+m)=2^m(n(t)+1)-1\). Breadth-first from the seed
\((t,p)=(5,10)\), keeping for each reachable \(t\) the smallest \(p\) found,
gives the reachable even \(r\) honestly — including the gaps, which are real and
must be shown as gaps. Closed form \(n=51\cdot2^{r/2-5}-1\) and asymptotic
density \(51^2/2^{11}\) both fall out and are asserted against the table.

## Driver — `run_all.sh`

`set -euo pipefail`, deterministic, byte-identical across runs (no timestamps,
no paths outside the repo, sorted output, `LC_ALL=C`). Rebuilds the propagated
matrices from scratch into a temp dir and `cmp`s them against the committed
copies, so a stale committed matrix is a hard failure. Runs both verifiers on
all four matrices, diffs their fact dumps, and asserts each hard-coded expected
value individually with a named failure message. Exit 0 only if everything
passes.
