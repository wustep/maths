# Attack log — smale-tau

Chronological attempts, newest last. A failed attack belongs here too.

## 2026-09-02 — mint, literature, choice of the finite handle

- Read Smale 1998 (Problem 4), Shub–Smale 1995, Bürgisser 2006/2009,
  Koiran 2004, Markström 2014, OEIS A173419 and A217032, and the 2013
  contest pages (RESEARCH.md).
- The polynomial statement has no finite record to move: no table of the
  largest \(Z(f)\) for \(\tau(f)\le k\) exists in the literature, so a
  table would be new data, not a dent. Smale's own text puts the integer
  question \(\tau(k!)\le(\log k)^c\) inside Problem 4, and there the
  record is finite and explicit: \(\tau(n!)\) is known for \(n\le 19\),
  and \(20!,21!,22!\) sit at \(13\le\tau\le 14\).
- q1: complete 13-step search with exact arithmetic, deciding
  \(\tau(20!),\tau(21!),\tau(22!)\), plus \(29\#\) and \(31\#\) where
  Markström's bounds leave a gap of three. Details in
  `compute/q1/README.md`.

## 2026-09-02 — q1 controls

- Count mode replays Markström's Figure 1 exactly for \(k\le 9\)
  (2, 4, 9, 26, 102, 562, 4363, 46154, 652227) and OEIS A173419 for
  \(n\le 1800\) with no mismatch; the four Patanè primes below 5000
  (3359, 3623, 4909, 4943) come out with the stated values.
- The three-step endgame agrees with a brute-force Python expansion on
  7485 random (prefix, target) pairs at prefix depths 3–6, and with an
  independent Rust brute-force expansion (`compute/q1/check.rs`) on
  11991 pairs at prefix depths 7, 9 and 10, of which 11991 include 7991
  genuinely reachable targets. The Rust enumerator, written separately
  with different data structures, reproduces the node counts per depth
  through depth 9 (1, 2, 8, 59, 663, 10609, 225219, 6057298, 199290037)
  and the same reached-set sizes.
- Decisions at 11 and 12 steps replay the 2013 record: 13! and 14! in 11
  steps, none of 15!–22! in 11; the 12-step run is the second control
  (see below).
- Endgame comparison totals: four Rust batches at prefix depths 7, 9, 10,
  10 with 25183 (prefix, target) pairs, 16785 of them reachable, zero
  mismatches (`compute/q1/compare_*.txt`).
- Table extension: count mode to 9 steps reaches every \(n\le 10266\)
  (Markström's "initial interval"; OEIS A141414 has 10267 as the least
  \(n\) with \(\tau(n)=10\)). The C and Rust tables agree for all
  \(n\le 10266\), match the OEIS b-file for \(n\le 1800\), and are
  written to `compute/q1/tau_table_10266.txt`. The least \(n\) with
  \(\tau(n)=9\) is 1821, as in A141414. Histogram of \(\tau(n)\) for
  \(n\le 10266\): 1, 1, 2, 5, 17, 75, 405, 2130, 5845, 1785 for
  \(\tau=0,\dots,9\).
- Speed work: the first endgame did about a thousand hash lookups per
  target per leaf. A size bound (a target that is neither a square nor a
  cube needs \(\max S^5\ge N\) to be reachable in three steps), range
  checks before every lookup, divisor sets instead of 128-bit divisions,
  and a bit-length scan instead of a limb division cut the 11-step run
  from 187 s to 50 s on 8 threads.

## 2026-09-02 — q2, the polynomial side (largest \(Z\) at cost \(k\))

- Question: \(T(k)=\max\{Z(f):\tau(f)\le k\}\) over \(\mathbb Z[x]\),
  programs from \(\{1,x\}\). Hand constructions: \(x\) (\(k=0\)),
  \(x(x-1)\) (2), \(x^3-x\) (3), \((x^2-2x)(x^2-1)\) (5, roots
  \(-1,0,1,2\)), \(x(x^2-1)(x^2-4)\) (7 by hand).
- Canonical enumeration over \(\mathbb Z[x]\) (`compute/q2/poly_search.c`),
  exact 128-bit coefficients with a carried size bound, and three rigorous
  filters on \(Z\) (Descartes; roots modulo small primes with multiplicity
  and a collision allowance from the Cauchy bound; distinct roots modulo a
  prime larger than twice the Cauchy bound). Survivors are counted exactly
  in Python by the rational root theorem.
- Node counts per depth: 7, 67, 880, 16141, 396475, 12465248 for
  \(k=1,\dots,6\); distinct polynomials reached within \(k\) steps:
  2, 9, 36, 186, 1270, 11404, 133743.
- Result through \(k=6\): no candidate with \(Z\ge T_{\text{lower}}(k)+1\)
  at \(k\le 5\), so \(T(0..5)=1,1,2,3,3,4\); at \(k=6\) exactly four
  polynomials (\(\pm x(x^4-5x^2+4)\), \(\pm x^2(x^4-5x^2+4)\)) reach
  \(Z=5\) and none reaches 6, so \(T(6)=5\). The route is
  \(x^2-2\), its square \(x^4-4x^2+4\), minus \(x^2\), times \(x\): one
  step better than the hand construction. Root set \(\{-2,\dots,2\}\).
- \(k=7\) (about \(4\cdot10^8\) nodes) is queued behind the q1 run;
  \(k=8\) is \(\approx1.3\cdot10^{10}\) nodes and needs the 8-thread
  machine for an hour or two.
