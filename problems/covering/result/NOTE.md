# A binary $[50,40]_2$ code of covering radius 2, and what it does to the $R=2$ family

Every number below is emitted by code in [`verify/`](verify/) and re-checked on
every run of [`run_all.sh`](run_all.sh); none of it is typed from memory. The
script `verify/check_note.py` fails the pipeline if this file quotes a value the
pipeline did not produce.

---

## 1. Statement

$\ell_2(r,R)$ is the smallest length of a binary linear code of codimension $r$
and covering radius $R$. For an $r \times n$ parity-check matrix $H$ with column
set $S \subset \mathbb F_2^{\,r}$, covering radius $\le 2$ is equivalent to

$$\{0\} \cup S \cup (S+S) = \mathbb F_2^{\,r}.$$

**Result.** $\ell_2(10,2) \le 50$.

The witness is the $10 \times 50$ matrix
[`data/H_r10_n50.txt`](data/H_r10_n50.txt), a parity-check matrix of a
binary $[50,40]_2$ code of covering radius exactly 2. Its columns, as unsigned
integers with bit $i$ (LSB first) equal to row $i+1$:

```
   1    2    4   15   16   32   65   86  128  173
 183  202  212  247  256  297  320  329  341  366
 373  381  391  403  438  460  479  491  502  559
 576  608  653  734  742  754  771  777  789  821
 846  855  869  881  893  897  927  981 1003 1004
```

Verified exhaustively, from the matrix text, by two independent programs:

| | |
| --- | --- |
| shape | $10 \times 50$, $\mathbb F_2$-rank 10, 50 distinct nonzero columns |
| coverage | 1024/1024 syndromes |
| covering radius | exactly 2 (some syndrome is neither $0$ nor a column) |
| covering density $\mu = \bigl(1+n+\binom n2\bigr)/2^r$ | $319/256 = 1.24609375$ |
| minimum distance | $d = 3$ |

The previous entry is the Kaikkonen–Rosendahl $[51,41]_2 2$ code of 2003,
rebuilt here as [`data/kr_r10_n51.txt`](data/kr_r10_n51.txt) and independently
re-verified: 51 columns, coverage 1024/1024, density $1327/1024$. So this is
one column below a bound that has stood for 22 years.

## 2. Why it matters: the $r=10$ seed

Shaving one column off one table cell would be a footnote. That is not what
this is.

Davydov, Marcugini and Pambianco, *New upper bounds for binary linear covering
codes* ([arXiv:2511.02542](https://arxiv.org/abs/2511.02542), Nov 2025),
Theorem 5.7, give an infinite family of $[n, n-r, 3]_2 2$ codes for
$r = 10, 18, 20$ and even $r \ge 28$, with

$$n = \Phi(r) = 26 \cdot 2^{r/2-4} - 1 = 52 \cdot 2^{r/2-5} - 1,
\qquad \bar\mu(2) \approx 26^2/2^9 = 2704/2048 = 1.3203125 .$$

Read the closed form again: $\Phi(r) = 2^m(51+1) - 1$ with $m = r/2-5$. The
$52$ is the Kaikkonen–Rosendahl $51$, plus one. **The whole family is the $r=10$
entry pushed forward.** Their Theorem 5.7(i) says so in as many words — the
2-partitions of $H_{KR}$ "are very important for the next iterative process" —
and Table 5.1 row $r=10$ reads $n = 51$, reference Kaikkonen–Rosendahl, density
1.29590, *not bolded*: even this November 2025 paper did not improve it.

Replace the seed and the whole family moves. With $n_0 = 50$ the same recurrence
$n_{\text{new}} + 1 = 2^m (n_0+1)$, $r_{\text{new}} = r_0 + 2m$ gives

$$n = 51 \cdot 2^{r/2-5} - 1, \qquad
\bar\mu(2) \le 51^2/2^{11} = 2601/2048 = 1.27001953125 .$$

For that to be more than arithmetic, the new matrix has to admit a 2-partition
at least as small as the paper's. It does — smaller, in fact.

## 3. The 2-partition

Construction QM$_2^2$ needs a **$(2,0)$-partition** of the column set
(arXiv:2511.02542 Definition 3.2): a partition into nonempty blocks such that
every element of $\mathbb F_2^{\,r}$, including $0$, is a sum of at most two
columns drawn from *distinct* blocks. $p(H)$ denotes the number of blocks.

[`data/partition_p10.json`](data/partition_p10.json) gives one with
**p(H) = 10**, against the paper's computer-searched $p(H_{KR}) = 11$
(their Theorem 5.2). Block sizes 8, 1, 3, 2, 8, 8, 8, 2, 1, 9.

| block | columns |
| ---: | :--- |
| 0 | 2, 128, 202, 212, 771, 855, 897, 981 |
| 1 | 86 |
| 2 | 381, 893, 1003 |
| 3 | 183, 297 |
| 4 | 1, 65, 247, 256, 320, 438, 502, 734 |
| 5 | 15, 173, 329, 366, 460, 559, 653, 846 |
| 6 | 4, 16, 391, 491, 742, 754, 869, 881 |
| 7 | 479, 1004 |
| 8 | 403 |
| 9 | 32, 341, 373, 576, 608, 777, 789, 821, 927 |

The checker is separate from the covering check and sweeps all $2^{10}$
syndromes. Of them, 1 is zero and 50 are single columns — satisfied by
definition — leaving **973** that genuinely require a pair, and all 973 have a
cross-block pair.

How tight this is: the pair-only multiplicity histogram over those 973 is
`1:821, 2:123, 4:19, 5:8, 6:2`, so **821** syndromes have a *unique* pair
representation. Each of those 821 forces its two columns into different blocks.
The full multiplicity histogram over all 1024 syndromes, counting the empty sum,
the singletons and the $\binom{50}{2}$ pairs, is `1:859, 2:129, 4:24, 5:9, 6:3`
(total $1 + 50 + 1225 = 1276$, hence the density $319/256$).

## 4. Minimality

Delete any single column and the remaining 49 columns leave at least **9**
syndromes uncovered. The best deletions — columns 381, 479 and 927 — leave
exactly 9; every other deletion is worse. Checked by full recount over all
$2^{10}$ syndromes for each of the 50 deletions.

So the 50-set is a *minimal* 1-saturating set in $PG(9,2)$, equivalently a
locally optimal (LO) covering code in the sense of
Davydov–Giulietti–Marcugini–Pambianco. Nothing is padded; there is no slack to
give back. This is the first question a referee asks about a length record and
the answer is machine-checked.

## 5. The dependent triple

$d = 3$, and there are exactly **10** linearly dependent triples of columns.
Exactly one of them, $(491, 734, 821)$, has its three members in three distinct
blocks — blocks 6, 4 and 9.

This is the precise analogue of arXiv:2511.02542 Theorem 5.2(ii), where
$h_5 + h_{27} + h_{29} = 0$ with the three columns in distinct subsets of
$\mathscr P_{KR}$. The paper needs that property to run Construction QM$_5^2$
(their Theorem 5.4(ii)) and reach $r = 28$. The new seed has it, so the $r=28$
branch of the iteration has the ingredient it needs. **It is not carried out
here** — see §8.

## 6. Propagation

Construction QM$_2^2$ (arXiv:2511.02542 Theorem 4.1, equations (4.2) and (4.4)),
implemented in [`verify/build_propagation.py`](verify/build_propagation.py)
directly from the paper:

- $\mathscr B = \mathbb F_{2^m}$, $D = D_1(2)$, and the condition
  $n_0 \ge 2^m \ge p(H_0)$. With $n_0 = 50$ and $p(H_0) = 10$ this is asserted in
  code and permits exactly $m = 4, 5$ — $2^6 = 64 > 50$ closes it off above.
- Indicators: columns in distinct blocks get distinct $\beta_j$, and
  $\mathscr B$ is *all* of $\mathbb F_{2^m}$, so the per-block indicator sets are
  disjoint with $\sum_b |I_b| = 2^m$ and $|I_b| \le |B_b|$. A greedy allocator
  builds one and asserts feasibility rather than assuming it.
- Columns of $A(h_j,\beta_j)$ are $(h_j, \xi, \beta_j \xi)^{tr}$ over all
  $\xi \in \mathbb F_{2^m}$ including $\xi = 0$; $D = D_1(2)$ contributes the
  $2^m-1$ columns $(0_{r_0}, 0_m, w)^{tr}$.
- $GF(16)$ with $x^4+x+1$ (`0x13`), $GF(32)$ with $x^5+x^2+1$ (`0x25`), both
  self-tested for associativity, distributivity and inverses before use.

Both outputs then go through the **full exhaustive** check — the theorem tells
us where to look, the enumeration is what certifies the instance:

| | $r$ | $n$ | coverage | density | published |
| --- | ---: | ---: | ---: | ---: | ---: |
| seed | 10 | 50 | 1024/1024 | $319/256$ | 51 (KR 2003) |
| $m=4$ | 18 | 815 | 262144/262144 | $332521/262144 \approx 1.26847$ | 831 ($\Phi(18)$, new in the paper) |
| $m=5$ | 20 | 1631 | 1048576/1048576 | $1330897/1048576 \approx 1.26924$ | 1663 ($\Phi(20)$, new in the paper) |

Iterating: a state is $(r, p)$ with length $51 \cdot 2^{r/2-5} - 1$; a step with
parameter $m$ is legal iff $n \ge 2^m \ge p$ and lands on codimension $r+2m$ with
$p(H_C) \le 2^{m+1}+1$ by (4.4). Breadth-first from $(10, 10)$, the even $r$
reachable up to 64 are

> 10, 18, 20, 30, 32, 34, 36, 38, 40, 46, 48, 50, 52, 54, 56, 58, 60, 62, 64

and the even $r$ **not** reachable this way are

> 12, 14, 16, 22, 24, 26, 28, 42, 44.

The gaps are real and are shown as gaps. The paper fills its own $r = 22, 24, 26$
with Construction QM$_3^2$ and $r = 28$ with QM$_5^2$; $r = 42, 44$ then follow
from its $r=28$ code. Analogous steps ought to work from this seed — §5 supplies
the ingredient QM$_5^2$ needs — but they are not carried out here, so nothing is
claimed for those $r$.

The generated table with every row, density and published comparison is
[`data/family_table.md`](data/family_table.md). Closed form for the reachable
even $r$:

$$n = 51 \cdot 2^{r/2-5} - 1, \qquad
\mu = \frac{51^2}{2^{11}} - \frac{51}{2^{r/2+1}} + \frac{1}{2^{r}}
\ \longrightarrow\ \frac{51^2}{2^{11}} = \frac{2601}{2048} \approx 1.27002,$$

approached from below. Against the literature:

| | $\bar\mu(2)$ | source |
| --- | ---: | --- |
| pre-2025 | $729/512 \approx 1.42383$ | $\phi(r) = 27\cdot2^{r/2-4}-1$, standing since 1992 |
| arXiv:2511.02542 Thm 5.7 | $2704/2048 \approx 1.32031$ | seeded by KR $n_0=51$ |
| this seed | $2601/2048 \approx 1.27002$ | seeded by $n_0 = 50$ |

Green's Problem 40 asks for
$f(2) = \liminf_{r\to\infty}\bigl(1+\ell_2(r,2)+\binom{\ell_2(r,2)}{2}\bigr)/2^r$.
A liminf is bounded above by the limit along any subsequence, and the even-$r$
subsequence above attains $2601/2048$, so $f(2) \le 2601/2048$.

(For the record: `../PROBLEM.md` quotes the range $1 \le f(2) \le 1.4238$. That
was already stale when written — arXiv:2511.02542 had brought the upper bound to
$\approx 1.32031$ two months earlier. Both numbers are superseded here.)

## 7. Verification

```bash
cd problems/covering/result && ./run_all.sh
```

Needs `python3` and `rustc`. No network, no packages, no RNG, no timestamps —
the output is byte-identical across runs.

Two verifiers, two languages, and no shared code:

- [`verify/verify.py`](verify/verify.py) is **pair-driven**: walk all
  $\binom n2$ pairs, mark what they hit, then sweep $2^r$ for anything unmarked.
- [`verify/verify.rs`](verify/verify.rs) is **syndrome-driven**: for each of the
  $2^r$ syndromes, scan the columns and test membership of $s \oplus h$. It then
  runs its own independent pair loop and refuses to report anything unless the
  two verdicts agree with each other.

They also differ in parser, rank pivot rule (lowest set bit vs highest), exact
rational arithmetic (`fractions.Fraction` vs `u128` gcd and long division), and
in how the partition and minimality checks are formulated. `run_all.sh` diffs
their fact dumps and fails on any difference.

Both read the matrix from **text**. Neither reads a stored certificate, and
`data/partition_p10.json` is consulted only for the block *labels* — the columns
themselves are re-derived from the matrix and cross-checked against the JSON.

**Encoding.** Everything here is LSB-first: bit $i$ of a column integer is row
$i+1$. The hex listing of $M_{KR}$ in arXiv:2511.02542 Theorem 4.3 is the
opposite, MSB-first with row 1 as the most significant of the ten bits, so
reconstructing $H_{KR} = [I_{10} \mid M_{KR}]$ reverses the ten bits. A
from-scratch verifier that misses the reversal fails on KR *and only on KR*,
which is a useful signal: if KR alone fails, suspect bit order rather than
mathematics. The reversal is pinned by the paper's own Theorem 5.2(ii),
$h_5 + h_{27} + h_{29} = 0$, asserted in the builder as a canary.

**On "independent".** Both verifiers were written in one session by one author.
Two languages, two algorithms, two parsers, no shared code — but not two people.
The one assumption neither can falsify alone is the column encoding, and that is
what the KR canary is for. A reader using the opposite convention gets the
bit-reverse of every column, which is an $\mathbb F_2$-linear relabelling of
$\mathbb F_2^{10}$ and preserves every claim here.

## 8. What is **not** claimed

- **50 is not shown to be optimal.** The sphere-covering bound gives only
  $\ell_2(10,2) \ge 45$: a length-$n$ radius-2 binary code of codimension 10
  needs $1 + n + \binom n2 \ge 1024$, and $n = 44$ gives 991. Whether
  $\ell_2(10,2)$ is 45, 46, 47, 48, 49 or 50 is open. §4 shows only that *this*
  50-set has no redundant column, which says nothing about a different 49-set.
- **The $n = 49$ run leaving 7 uncovered syndromes is an incomplete search, not a
  lower bound.** It records where one annealing run stopped. It is not evidence
  that $\ell_2(10,2) > 49$.
- **The $(8,25)$ and $(9,38)$ gaps remain open.** The overnight attempts at
  $\ell_2(8,2) \le 25$ (best anneal missed 3 of 256 syndromes; CP-SAT and Z3
  returned no model) and $\ell_2(9,2) \le 38$ (CP-SAT UNKNOWN; deletions from a
  Gabidulin 39-set missed 8) both failed. Those failures are recorded in
  `../ATTACK.md` and are not superseded by anything here.
- **Only $m = 4$ and $m = 5$ are exhaustively verified.** Every claim at
  $r = 18$ and $r = 20$ rests on a complete enumeration of $2^{18}$ and $2^{20}$
  syndromes. Everything past that — the reachable-$r$ list, the closed form, the
  asymptotic density — rests on the paper's bound $p(H_C) \le 2^{m+1}+1$ from
  (4.4) rather than on partitions computed here. **This is the weakest link and
  a referee should push on it first.** The bound is the paper's own and the
  iteration is the paper's own; what is inherited is a bound, not a computation.
- **Nothing is claimed for $r \in \{12, 14, 16, 22, 24, 26, 28, 42, 44\}$.** The
  QM$_3^2$ and QM$_5^2$ analogues that would fill them are not implemented.
- **The $f(2)$ bound is an upper bound only.** Whether $f(2) = 1$ is untouched;
  the lower bound $f(2) \ge 1$ is unmoved.
- **Priority is unresolved.** Table 5.1 of arXiv:2511.02542 is explicitly "best
  as far as the authors know". A $\ell_2(10,2) \le 50$ may already exist in ACCT
  proceedings or elsewhere. See [`PRIORITY.md`](PRIORITY.md); this needs a human
  before anything is posted.

## 9. Provenance

The matrix was found by targeted fixed-cardinality simulated annealing, driven
by an LLM agent (Codex `gpt-5.6-sol`, overnight 2026-08-16), seeded from the
Kaikkonen–Rosendahl 51-column matrix; it hit zero uncovered syndromes at
proposal 3,600,281 of run 0 (xorshift64). The 2-partition, the minimality and
dependent-triple analysis, and the QM$_2^2$ propagation were derived afterwards.

That provenance does not need defending, because none of it is load-bearing. A
covering-radius claim is a finite, decidable statement about a committed matrix.
Every assertion in this note is re-derivable in under a second from
`data/*.txt` by two programs in two languages that share no code. How the matrix
was found is a matter of history; whether it works is a matter of enumeration.

A second pair of QM$_2^2$ matrices, from a different indicator allocation,
lives in [`data/alt/`](data/alt/). Both pass the exhaustive check. See
[`RESULT.md`](RESULT.md).
