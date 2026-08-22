# Research log — Linear covering codes of radius two

## 2026-08-16

- [Ben Green, *100 Open Problems*, Problem 40](https://people.maths.ox.ac.uk/greenbj/papers/open-problems.pdf) — $1\le f(2)\le 1.4238$; unknown whether $f(2)=1$.
- [Davydov–Marcugini–Pambianco, arXiv:2511.02542v1, Table 5.1](https://arxiv.org/abs/2511.02542) — documented $\ell_2(10,2)\le 51$, density $1327/1024$; also $\ell_2(8,2)\le 26$, $\ell_2(9,2)\le 39$. Named in the recovered `witness_r10_n50.json`.
- Kaikkonen–Rosendahl 51-column seed used by q1 search (named in WALKTHROUGH.md and witness JSON). The explicit 51-column hex listing was not recovered as a separate file.

## 2026-08-18 (q4, n=49 push — residue only)

- Counting: $1+49+\binom{49}{2}=1226\ge 1024$, so 49 is not excluded by volume; a 49-covering would have density $1226/1024\approx 1.19727$, well below the paper's $\bar\mu$ values. Counting lower bound is only $n\ge 45$.
- Invariant-covering reduction: for $G\le GL(10,2)$, $G$-invariant coverings live in orbit-class space; conjugate subgroups give equivalent problems, and $\langle M\rangle=\langle M^k\rangle$ collapses cyclic classes to cyclotomic-coset data. Order-7 elements of $GL(10,2)$: elementary divisors from $x^3+x+1$, $x^3+x^2+1$, trivial part of dim 1, 4, or 7. Frobenius (order-10) and pure multiplicative order-3/5/11/31 symmetries are arithmetically impossible at n=49 (orbit sizes cannot sum to 49).
- Exhaustions (all zero witnesses): both order-7 dim-1-fixed classes; all 50 $C_7\times C_7$ classes; 12 order-15, 10 order-21, 7 order-105 classes. Open: order-7 with fixed dim 4/7 (timeouts), order-9/-35/-45 (not reached before stop).
- The 7-hole residue at n=49 reproduces across independent anneals; two inequivalent GL-classes of 7-hole optima found, both with hole sets of rank 5 containing exactly one zero-sum quadruple, both ≥5- resp. ≥4-swap-deep (exhaustive k-swap prover with exact defer/endgame logic).
- WLOG frame reduction for SAT: a rank-10 covering can be assumed to contain the ten unit vectors (GL acts transitively on ordered bases); cuts the cardinality-49 CNF search substantially. Instance built (1.14M clauses); no verdict before the stop order.

## 2026-08-20 (leftover paper constructions)

- $M_{OK}$ last hex word in arXiv:2511.02542 (6.10) is the invalid token `ICE`. Exhausting all 9-bit last columns against Theorem 7.1's $P_{OK}$ leaves exactly one survivor: `1CE`.
- QM$_2^1$ on the certified $p(H_{18})\le 17$ partition is the unused $p$-preserving lift: $n=2^m(n_0+2)-2$ is usually worse than QM$_2^2$, but here $m=4$ is legal and yields $\ell_2(26,2)\le 13070$, shorter than the already-certified QM$_3^2$ length 13309. An explicit 19-block 2-partition of that matrix unlocks QM$_2^2$ at $m=5$: theorem-only $\ell_2(36,2)\le 418271$.

## 2026-08-21 (q9, trajectory of the $r=10$ record)

Full text of arXiv:2511.02542v1 read from
[the arXiv HTML](https://arxiv.org/html/2511.02542v1) (the PDF is not added to
the repo; citation only). Bibliographic chain for $\ell_2(10,2)$:

- **1991** — Gabidulin, Davydov, Tombak, *Linear codes with covering radius 2
  and other new covering codes*,
  [IEEE Trans. Inform. Theory 37(1) 219–224](https://doi.org/10.1109/18.61146).
  Odd-$r$ family $f(2t-1)=5\cdot 2^{t-2}-1$; reprinted as (4.8) of
  arXiv:2511.02542. Gives $\ell_2(9,2)\le 39$, $\ell_2(11,2)\le 79$; **does not
  apply at $r=10$**.
- **1992/1994** — Davydov, Drozhzhina-Labinskaya, ACCT-3 p. 53 and
  [IEEE Trans. Inform. Theory 40(4) 1270–1279](https://doi.org/10.1109/18.335937),
  Example 3.1; also Cohen–Honkala–Litsyn–Lobstein, *Covering Codes* (1997),
  Thm 5.4.27(i). Even-$r$ family $\phi(2t)=27\cdot 2^{t-4}-1$, reprinted as (4.7)
  of arXiv:2511.02542. $\phi(8)=26$, $\phi(10)=53$, $\phi(12)=107$: the family
  doubles $n+1$ every two units of $r$, so its $r=10$ value is literally the
  $r=8$ value lifted, $2(26+1)-1=53$.
- **2003** — Kaikkonen, Rosendahl, *New covering codes from an ADS-like
  construction*,
  [IEEE Trans. Inform. Theory 49(7) 1809–1812](https://doi.org/10.1109/TIT.2003.813508),
  p. 1812: $\ell_2(10,2)\le 51$. Not a member of the $\phi$ family — a direct
  construction at $r=10$, a decrease of 2.
- **Nov 2025** — Davydov, Marcugini, Pambianco,
  [arXiv:2511.02542v1](https://arxiv.org/abs/2511.02542), Table 5.1 still carries
  51 at $r=10$ (marked $\bullet$ = "known result of [50] not in the book [17]"),
  and their Theorem 4.3 / display (4.9) **reprints the 41 hexadecimal columns of
  $M_{KR}$**, with $H_{KR}=[I_{10}\ M_{KR}]$. Their new $\Phi(r)$ family uses
  this 51-set as its seed, with the computer-searched $p(H_{KR})=11$ (Thm 5.2).
- **2026-08-16** — this repo, q1: 50.

The 41 hex words of (4.9) are now transcribed in
[`compute/q9/build_kr51.py`](compute/q9/build_kr51.py) and rebuilt into
[`compute/q9/H_r10_n51_KR.txt`](compute/q9/H_r10_n51_KR.txt): rank 10, 51
distinct nonzero columns, exhaustive pair-XOR 1024/1024. This closes the
2026-08-16 note above that "the explicit 51-column hex listing was not
recovered as a separate file".

Structural reading of the trajectory (computed, see
[`compute/q9/profiles.py`](compute/q9/profiles.py)): 53 *is* a lift of the $r=8$
record; 51 and 50 are not. Over all 174251 two-dimensional quotients
$q:\mathbb F_2^{10}\to\mathbb F_2^2$, neither the 51-set nor the 50-set has a
kernel block $S\cap\ker q$ that covers $\ker q$ — not one. Both are
quotient-flat: $|S\cap\ker q|$ stays in $3..27$ (51-set) and $3..26$ (50-set)
around a mean of $n/4$. Together with q4's 79 exhausted subgroup classes at
$n=49$, the object that would be a 49 is not a lift, not a symmetry orbit, and
(q4) not within 5 swaps of the known near-misses.
