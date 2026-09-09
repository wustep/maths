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

## 2026-09-09 — q4: AP ladder and named midpoint covers

- Reopened the source record: OEIS already reports m(59)=15 and values
  through 73. A lower replay at 59 would match that record. The checked
  15-set remains the only local bound at 59.
- The inherited Rust AP5 exclusion visited 1,559,513 nodes. Its pending
  CaDiCaL replay finished UNKNOWN at 5,000,000 conflicts; the saved SAT
  result does not independently confirm UNSAT.
- Started the AP4 case with the Rust repair-cover search, a 600-second
  wall limit and a 100-million-node limit. One heavy search runs at a time.
- Added a C completion checker using reflection intersections for ordered
  sum counts, a fixed 128 MiB cache, and a sumset-support cap. Its first
  controls agree with complete subset enumeration through 13, including
  named midpoint roots and progression avoidance. These controls test the
  implementation; they are not a lower bound at 59.

### Wrap at the user's request

- AP4 Rust timed out after 600 seconds and returned UNKNOWN through the
  harness. It emitted no node count. `p59_ap4_exact.json` records the cap,
  source hash, binary hash, and termination; this is not an exclusion.
- The later AP5 CaDiCaL artifact arrived during wrap. It reports UNSAT
  after 14,448,284 conflicts in 1,474.911 seconds. A fresh formula build
  matches its SHA-256, 44,028 variables, and 129,306 clauses. The earlier
  five-million-conflict UNKNOWN artifact is retained as well. The completed
  SAT and Rust runs now agree on the AP5 restriction; no DRAT proof is retained.
- The experimental C AP5 run was interrupted with exit 130 at the user's
  request. Its UNKNOWN record is `p59_ap5_cover_interrupted.json`; it adds
  no exclusion. No further heavy job was started.
- The midpoint partition audit checked 2,054 small sets and every affine
  identification at 59. It leaves 25 AP4-free classes, or 27 AP4-but-AP5-free
  classes for that part of the ladder. These classes were prepared, not
  searched. The C controls checked 104 decisions against enumeration of
  10,364 subsets through 13.
- The wrap retains only $m(59)\le15$ as an unrestricted local bound. OEIS
  already reports equality, so there is no dent. LEAVES records residue;
  unrestricted size at most 14 remains open here. The full replay driver
  includes the long AP5 SAT check, but only lightweight verification was
  rerun during wrap. The PR is to remain unmerged.
