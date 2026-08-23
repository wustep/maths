# Attack log — Sets with no unique sum mod p

## 2026-08-16

- Environment created. Overnight campaign: exact $m(p)$ for primes $p\le 200$, table + plots +
  extremal shape. No attack yet.

## 2026-08-16 — q1 residue (recovered)

- Table used wrong predicate r=1 not r∉{1,2} (memory: commit 77d43c5).
- Scripts recovered: `search_m_p.py`, `verify_m_p.py`, `plot_m_p.py`.

## 2026-08-16 — q2

- Recoded predicate. Recovered `green_m_p.csv` matches A398173 through p=47.
- Scripts: `search_green_m_p.py`, `verify_green_m_p.py`.

## 2026-08-23 — q3: p=53 replay, p=59 residue

- Fetched Bedert arXiv:2303.15134v2 and Cao–Yuan arXiv:2608.06728v1. Both use unordered-pair uniqueness, equivalently ordered multiplicities avoiding $\{1,2\}$ for odd $p$. Cao–Yuan's leading upper constant is $1/(2(\log_2 3)^2)$.
- Reopened OEIS A398173. It now has a 15th term, $m(53)=14$, so $p=59$ is the first unpublished boundary.
- Replayed the committed $p\le47$ cardinality-SAT table with CaDiCaL 1.9.5: 14/14 OEIS terms matched in 960.158 seconds.
- Added `compute/q3/verify_exact.rs`, an independent exact search. It starts from the affine-normalized $\{-1,0,1\}$, branches on all possible second representations of a currently unique sum, and memoizes intermediate sets up to every internal three-term-progression normalization.
- Replayed $m(53)=14$: the saved 14-set passes the definition directly, while the final Rust search returned `UNSAT` for every set of size at most 13 after 333,555,078 nodes in 1,428.475 seconds. The complete cold driver took 1,618.255 seconds. This matches the published term; it does not improve it.
- At $p=59$, CaDiCaL found the checked 15-set $\{0,1,25,28,32,36,43,46,47,49,52,53,55,57,58\}$ in 48.766 seconds. Therefore $m(59)\le15$ only.
- The independent size-at-most-14 run stopped `UNKNOWN` after exactly 100,000,000 nodes (72,327,605 memoized states) in 523.030 seconds. This incomplete run is not a lower bound. A CaDiCaL 1.9.5 exact-size-14 run was also manually stopped without a decision after 37:01 wall time (34:49 CPU).
- Kissat 4.0.4, CaDiCaL 3.0.0, and MapleChrono exact-size-14 runs were each stopped without a decision after about 30 minutes wall time. The solver timeouts are not certificates.
- Heuristic search reached a 14-set with one unique sum. Every normalized 14-set within four swaps of that near miss was checked (49,168,350 sets); none worked. This neighborhood search is also not a lower bound.
